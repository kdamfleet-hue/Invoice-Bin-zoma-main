# -*- coding: utf-8 -*-
"""
مزامنة سجل السائقين من تقارير أبشر إلى قاعدة البيانات.

التدفّق:
  1) يقرأ ملف/ملفات أبشر  (--excel ...)
  2) يقرأ قاعدة البيانات الحالية:
        - معاينة بدون اتصال:  --from-json drivers_data.js
        - على الخادم الحقيقي: --from-db   (يتطلب DATABASE_URL + psycopg2)
  3) يحسب الفروقات:
        • إضافة   : مستخدم فعلي في أبشر غير موجود في قاعدة البيانات
        • تحديث   : موجود في الاثنين لكن تغيّرت لوحته/مركبته/اسمه (يُحفظ الجوال والرقم الوظيفي)
        • تم إلغاء تفويضهم : سائق في قاعدة البيانات (له لوحة) ولم يعد المستخدم الفعلي لأي مركبة
        • بدون مركبة : سائق في قاعدة البيانات بلا لوحة (لا يمكن اعتباره ملغى تفويضه آلياً)
  4) يكتب تقريراً + ملفات JSON (proposed_changes.json / deauthorized.json)
  5) الافتراضي تجريبي (لا يعدّل شيئاً). للتطبيق الفعلي:  --apply  (مع --from-db فقط)
     يأخذ نسخة احتياطية تلقائية قبل أي كتابة.

الجوال (رقم الجوال) غير موجود في تقارير أبشر، لذلك لا يُلمَس ويبقى كما هو في قاعدة البيانات.
"""
import os
import sys
import json
import argparse
import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from absher_parser import parse_many, norm_id  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "out")
BACKUP_DIR = os.path.join(HERE, "backups")


# ───────────────────────── مصادر قاعدة البيانات ─────────────────────────
def load_db_from_json(path):
    txt = open(path, encoding="utf-8").read()
    arr = json.loads(txt[txt.find("["): txt.rfind("]") + 1])
    out = []
    for d in arr:
        if not isinstance(d, dict):
            continue
        if str(d.get("iqama", "")).startswith("ID Number"):   # سطر العنوان الوهمي
            continue
        out.append(d)
    return out


def pg_connect():
    import psycopg2
    import psycopg2.extras
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise SystemExit("DATABASE_URL غير مضبوط على هذا الخادم.")
    return psycopg2.connect(url), psycopg2.extras


def load_db_from_postgres():
    conn, extras = pg_connect()
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    cur.execute("SELECT id, name, empid, plate, car, iqama, phone, drivercard FROM drivers ORDER BY id")
    rows = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


# ───────────────────────── منطق الفروقات ─────────────────────────
def build_excel_index(excel_paths):
    recs = parse_many(excel_paths)
    by_iqama, by_plate = {}, {}
    for r in recs:
        if r["iqama"]:
            by_iqama.setdefault(r["iqama"], r)
        if r["plate_norm"]:
            by_plate.setdefault(r["plate_norm"], r)
    return recs, by_iqama, by_plate


def compute_diff(db, by_iqama, update_names=False):
    db_iqamas = {norm_id(d.get("iqama")) for d in db if norm_id(d.get("iqama"))}
    updates, deauth, no_vehicle, unchanged = [], [], [], []

    for d in db:
        iq = norm_id(d.get("iqama"))
        ex = by_iqama.get(iq) if iq else None
        if ex:
            chg = {}
            if ex["plate"] and ex["plate"] != (d.get("plate") or ""):
                chg["plate"] = [d.get("plate") or "", ex["plate"]]
            if ex["vehicle"] and ex["vehicle"] != (d.get("car") or ""):
                chg["car"] = [d.get("car") or "", ex["vehicle"]]
            # الاسم: افتراضياً لا نستبدل اسم قاعدة البيانات (غالباً عربي أنظف من تهجئة أبشر
            # اللاتينية). نملأه فقط لو كان فارغاً، أو نحدّثه بالكامل عند تمرير --update-names.
            db_name = (d.get("name") or "").strip()
            if ex["name"] and ex["name"] != db_name and (update_names or not db_name):
                chg["name"] = [db_name, ex["name"]]
            if chg:
                updates.append({"iqama": iq, "empid": d.get("empid"), "current_name": d.get("name"), "changes": chg})
            else:
                unchanged.append(iq)
        else:
            row = {"name": d.get("name"), "empid": d.get("empid"), "iqama": iq,
                   "plate": d.get("plate"), "car": d.get("car"), "phone": d.get("phone")}
            (deauth if (d.get("plate") or "").strip() else no_vehicle).append(row)

    new = [{"name": ex["name"], "iqama": iq, "plate": ex["plate"], "car": ex["vehicle"], "phone": ""}
           for iq, ex in by_iqama.items() if iq not in db_iqamas]
    return updates, deauth, no_vehicle, new, unchanged


# ───────────────────────── التطبيق على Postgres ─────────────────────────
def apply_changes(updates, new, deauth):
    conn, extras = pg_connect()
    cur = conn.cursor()
    # 1) نسخة احتياطية كاملة لجدول drivers قبل أي تعديل
    os.makedirs(BACKUP_DIR, exist_ok=True)
    cur2 = conn.cursor(cursor_factory=extras.RealDictCursor)
    cur2.execute("SELECT * FROM drivers ORDER BY id")
    backup = [dict(r) for r in cur2.fetchall()]
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    bpath = os.path.join(BACKUP_DIR, "drivers_backup_%s.json" % ts)
    json.dump(backup, open(bpath, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("✓ نسخة احتياطية:", bpath, "(", len(backup), "سائق )")

    # 2) تحديثات (لا تلمس الجوال ولا الرقم الوظيفي)
    for u in updates:
        sets, params = [], []
        for f, (_old, newv) in u["changes"].items():
            sets.append("%s = %%s" % f)
            params.append(newv)
        if not sets:
            continue
        params.append(u["iqama"])
        cur.execute("UPDATE drivers SET %s WHERE regexp_replace(iqama,'[^0-9]','','g') = %%s" % ", ".join(sets), params)

    # 3) إضافات (جوال فارغ — يُكمَّل لاحقاً من «تم» أو يدوياً)
    for n in new:
        cur.execute(
            "INSERT INTO drivers (name, empid, plate, car, iqama, phone, drivercard) VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (n["name"], "", n["plate"], n["car"], n["iqama"], "", ""),
        )

    # 4) قائمة «تم إلغاء تفويضهم» تُكتب في بلوب deauthorized_data (الصف id=1 = فرع الدمام)
    payload = json.dumps(deauth, ensure_ascii=False)
    cur.execute("SELECT 1 FROM deauthorized_data WHERE id = 1")
    if cur.fetchone():
        cur.execute("UPDATE deauthorized_data SET data = %s WHERE id = 1", (payload,))
    else:
        cur.execute("INSERT INTO deauthorized_data (id, data) VALUES (1, %s)", (payload,))

    conn.commit()
    cur.close()
    cur2.close()
    conn.close()
    print("✓ طُبِّقت التغييرات: %d تحديث، %d إضافة، %d في قائمة إلغاء التفويض." % (len(updates), len(new), len(deauth)))


# ───────────────────────── التقرير ─────────────────────────
def write_report(excel_recs, by_iqama, db, updates, deauth, no_vehicle, new, unchanged, report_path):
    os.makedirs(OUT_DIR, exist_ok=True)
    lines = []
    a = lines.append
    a("=" * 78)
    a("تقرير مزامنة سجل السائقين — %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    a("=" * 78)
    a("مركبات أبشر (إجمالي):            %d" % len(excel_recs))
    a("مركبات لها مستخدم فعلي:          %d" % sum(1 for r in excel_recs if r["iqama"]))
    a("مركبات بلا مستخدم فعلي ('-'):     %d" % sum(1 for r in excel_recs if not r["iqama"]))
    a("أشخاص مفوّضون (هوية فريدة):       %d" % len(by_iqama))
    a("سائقون في قاعدة البيانات:        %d" % len(db))
    a("-" * 78)
    a("➕ إضافات (في أبشر وغير موجودين بقاعدة البيانات): %d" % len(new))
    a("✏️ تحديثات (تغيّرت لوحة/مركبة/اسم):              %d" % len(updates))
    a("🚫 تم إلغاء تفويضهم (لهم لوحة ولم يعودوا مستخدمين): %d" % len(deauth))
    a("🅿️ بلا مركبة في قاعدة البيانات:                  %d" % len(no_vehicle))
    a("= بدون تغيير:                                    %d" % len(unchanged))
    a("=" * 78)
    a("\n— عيّنة من «تم إلغاء تفويضهم» —")
    for d in deauth[:40]:
        a("   • %-32s | إقامة %-12s | لوحة %-12s | %s" % (
            (d["name"] or "")[:32], d["iqama"] or "", d["plate"] or "", d["car"] or ""))
    a("\n— عيّنة من الإضافات الجديدة —")
    for d in new[:25]:
        a("   • %-32s | إقامة %-12s | لوحة %-12s | %s" % (
            (d["name"] or "")[:32], d["iqama"] or "", d["plate"] or "", d["car"] or ""))
    a("\n— عيّنة من التحديثات —")
    for u in updates[:25]:
        a("   • %s (إقامة %s): %s" % (u["current_name"], u["iqama"],
                                      ", ".join("%s: %s ← %s" % (k, v[1], v[0]) for k, v in u["changes"].items())))
    open(report_path, "w", encoding="utf-8").write("\n".join(lines))
    # ملفات JSON للمراجعة/الاستخدام
    json.dump({"updates": updates, "new": new, "no_vehicle": no_vehicle},
              open(os.path.join(OUT_DIR, "proposed_changes.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(deauth, open(os.path.join(OUT_DIR, "deauthorized.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="مزامنة سجل السائقين من أبشر إلى قاعدة البيانات")
    ap.add_argument("--excel", nargs="+", required=True, help="ملف/ملفات أبشر (xlsx)")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--from-json", help="معاينة بدون اتصال من ملف drivers_data.js")
    src.add_argument("--from-db", action="store_true", help="قراءة من Postgres الحيّ (DATABASE_URL)")
    ap.add_argument("--apply", action="store_true", help="تطبيق التغييرات فعلياً (مع --from-db فقط)")
    ap.add_argument("--update-names", action="store_true", help="استبدال أسماء قاعدة البيانات بأسماء أبشر (افتراضياً تُحفظ الأسماء الحالية)")
    args = ap.parse_args()

    db = load_db_from_json(args.from_json) if args.from_json else load_db_from_postgres()
    excel_recs, by_iqama, _by_plate = build_excel_index(args.excel)
    updates, deauth, no_vehicle, new, unchanged = compute_diff(db, by_iqama, update_names=args.update_names)

    os.makedirs(OUT_DIR, exist_ok=True)
    report_path = os.path.join(OUT_DIR, "sync_report.txt")
    report = write_report(excel_recs, by_iqama, db, updates, deauth, no_vehicle, new, unchanged, report_path)
    print(report)
    print("\nتمت كتابة: %s" % report_path)

    if args.apply:
        if not args.from_db:
            raise SystemExit("التطبيق الفعلي يتطلب --from-db (لا يُطبَّق على معاينة JSON).")
        print("\n⚠️ تطبيق التغييرات فعلياً على قاعدة البيانات…")
        apply_changes(updates, new, deauth)
    else:
        print("\n(تشغيل تجريبي — لم تُعدّل قاعدة البيانات. أضف --apply مع --from-db للتطبيق.)")


if __name__ == "__main__":
    main()
