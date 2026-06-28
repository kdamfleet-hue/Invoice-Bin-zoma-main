# -*- coding: utf-8 -*-
"""
محرّك مزامنة أبشر — يُستخدم داخل التطبيق (المستورِد) وبدون أي تبعيات خارجية:
قارئ xlsx بالمكتبة القياسية (zipfile + XML) + استخراج الحقول + حساب الفروقات.

يعمل على الخادم كما هو (لا يتطلب openpyxl/pandas).
"""
import io
import re
import zipfile
from xml.etree import ElementTree as ET

_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
_R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
_PR = "{http://schemas.openxmlformats.org/package/2006/relationships}"

_AR2EN = {ord(a): e for a, e in zip("٠١٢٣٤٥٦٧٨٩", "0123456789")}


def to_en_digits(s):
    return ("" if s is None else str(s)).translate(_AR2EN)


def norm_plate(p):
    return re.sub(r"\s+", "", to_en_digits(p)) if p else ""


def norm_id(v):
    if v is None:
        return None
    s = re.sub(r"[^\d]", "", to_en_digits(v)).strip()
    return s or None


def clean(v):
    if v is None:
        return ""
    s = str(v).strip()
    return "" if s in ("-", "—") else s


def _col_to_idx(ref):
    m = re.match(r"([A-Za-z]+)", ref or "A")
    letters = (m.group(1) if m else "A").upper()
    n = 0
    for ch in letters:
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def read_xlsx_rows(fileobj, want_sheet="vehicle_list"):
    """يقرأ أول/المطلوب من ورقة xlsx → قائمة صفوف (كل صف قائمة قيم حسب العمود)."""
    z = zipfile.ZipFile(fileobj)
    names = z.namelist()

    shared = []
    if "xl/sharedStrings.xml" in names:
        root = ET.fromstring(z.read("xl/sharedStrings.xml"))
        for si in root.findall(_NS + "si"):
            shared.append("".join(t.text or "" for t in si.iter(_NS + "t")))

    target = None
    try:
        wb = ET.fromstring(z.read("xl/workbook.xml"))
        rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        rid_by_name = {s.get("name"): s.get(_R + "id") for s in wb.find(_NS + "sheets")}
        relmap = {rel.get("Id"): rel.get("Target") for rel in rels.findall(_PR + "Relationship")}
        rid = rid_by_name.get(want_sheet) or (next(iter(rid_by_name.values()), None))
        tgt = relmap.get(rid)
        if tgt:
            tgt = tgt.lstrip("/")
            target = tgt if tgt.startswith("xl/") else "xl/" + tgt
    except Exception:
        target = None
    if not target or target not in names:
        cands = sorted(n for n in names if n.startswith("xl/worksheets/") and n.endswith(".xml"))
        target = cands[0] if cands else None
    if not target:
        return []

    ws = ET.fromstring(z.read(target))
    sd = ws.find(_NS + "sheetData")
    rows = []
    if sd is None:
        return rows
    for row in sd.findall(_NS + "row"):
        cells, maxc = {}, -1
        for c in row.findall(_NS + "c"):
            ci = _col_to_idx(c.get("r", "A1"))
            t = c.get("t")
            if t == "inlineStr":
                isn = c.find(_NS + "is")
                val = "".join(x.text or "" for x in isn.iter(_NS + "t")) if isn is not None else ""
            else:
                v = c.find(_NS + "v")
                if t == "s":
                    val = shared[int(v.text)] if (v is not None and v.text is not None) else ""
                else:
                    val = v.text if v is not None else ""
            cells[ci] = val
            maxc = max(maxc, ci)
        rows.append([cells.get(i) for i in range(maxc + 1)])
    return rows


COL_ALIASES = {
    "plate": ["رقم اللوحة"],
    "brand": ["الماركة"], "model": ["الطراز"], "year": ["سنة الصنع"],
    "iqama": ["رقم هوية المستخدم الفعلي", "رقم هوية المستخدم", "رقم الهوية"],
    "name": ["اسم المستخدم الفعلي", "اسم المستخدم"],
    "lic_exp": ["تاريخ انتهاء رخصة السير"], "insp_exp": ["تاريخ انتهاء الفحص"],
}


def parse_rows(rows):
    """يحوّل صفوف الورقة إلى سجلات مركبات."""
    h_idx = None
    header = None
    for i, row in enumerate(rows):
        vals = [clean(c) for c in row]
        if "رقم اللوحة" in vals and ("اسم المستخدم الفعلي" in vals or "رقم هوية المستخدم الفعلي" in vals):
            h_idx, header = i, vals
            break
    if h_idx is None:
        raise ValueError("لم يُعثر على صف العناوين (رقم اللوحة) في الملف.")
    cmap = {}
    for key, aliases in COL_ALIASES.items():
        for a in aliases:
            if a in header:
                cmap[key] = header.index(a)
                break
    out = []
    for row in rows[h_idx + 1:]:
        if not row:
            continue

        def get(k):
            i = cmap.get(k)
            return row[i] if (i is not None and i < len(row)) else None

        plate = clean(get("plate"))
        if not plate:
            continue
        brand, model, year = clean(get("brand")), clean(get("model")), clean(get("year"))
        out.append({
            "plate": plate, "plate_norm": norm_plate(plate),
            "vehicle": " ".join(x for x in (brand, model, year) if x).strip(),
            "iqama": norm_id(get("iqama")), "name": clean(get("name")),
            "lic_exp": clean(get("lic_exp")), "insp_exp": clean(get("insp_exp")),
        })
    return out


def parse_file(fileobj):
    return parse_rows(read_xlsx_rows(fileobj))


def index_by_iqama(records):
    by = {}
    for r in records:
        if r["iqama"]:
            by.setdefault(r["iqama"], r)
    return by


def compute_diff(db_drivers, by_iqama, update_names=False):
    """db_drivers: list of dicts {name, empid, iqama, plate, car, phone}."""
    db_iqamas = {norm_id(d.get("iqama")) for d in db_drivers if norm_id(d.get("iqama"))}
    updates, deauth, no_vehicle, unchanged = [], [], [], []
    for d in db_drivers:
        iq = norm_id(d.get("iqama"))
        ex = by_iqama.get(iq) if iq else None
        if ex:
            chg = {}
            if ex["plate"] and ex["plate"] != (d.get("plate") or ""):
                chg["plate"] = ex["plate"]
            if ex["vehicle"] and ex["vehicle"] != (d.get("car") or ""):
                chg["car"] = ex["vehicle"]
            db_name = (d.get("name") or "").strip()
            if ex["name"] and ex["name"] != db_name and (update_names or not db_name):
                chg["name"] = ex["name"]
            if chg:
                updates.append({"iqama": iq, "id": d.get("id"), "current_name": d.get("name"), "changes": chg})
            else:
                unchanged.append(iq)
        else:
            row = {"name": d.get("name"), "empid": d.get("empid"), "iqama": iq,
                   "plate": d.get("plate"), "car": d.get("car"), "phone": d.get("phone")}
            (deauth if (d.get("plate") or "").strip() else no_vehicle).append(row)
    new = [{"name": ex["name"], "iqama": iq, "plate": ex["plate"], "car": ex["vehicle"], "phone": ""}
           for iq, ex in by_iqama.items() if iq not in db_iqamas]
    return {"updates": updates, "new": new, "deauthorized": deauth,
            "no_vehicle": no_vehicle, "unchanged": len(unchanged)}
