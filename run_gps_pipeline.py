"""
run_gps_pipeline.py
===================
يُشغّل خط أنابيب GPS الكامل بخطوة واحدة:
  الخطوة 1: merge_gps_data.py   — مطابقة اللوحات وتحديث الخلايا
  الخطوة 2: sync_gps_rows.py    — مزامنة 77 صف من المصدر
  الخطوة 3: apply_formatting.py — تطبيق التنسيق الاحترافي
  الخطوة 4: merge_gps_pro.py    — دمج احترافي مع الحفاظ على التنسيق
  الخطوة 5: finalize_gps.py     — الملف النهائي المميز

الاستخدام:
  python run_gps_pipeline.py
  python run_gps_pipeline.py --step 1      (تشغيل خطوة بعينها)
  python run_gps_pipeline.py --from 3      (من خطوة معينة للنهاية)
"""
import os
import sys
import time
import argparse
import subprocess

# ── إعداد الـ encoding ────────────────────────────────────────────────────────
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ── تعريف خطوات خط الأنابيب ───────────────────────────────────────────────────
PIPELINE = [
    {
        'step': 1,
        'name': 'مطابقة اللوحات وتحديث الخلايا',
        'script': 'merge_gps_data.py',
        'output': 'كشف اجهزة GPSللمركبات فرع الدمام 2026_محدث.xlsx',
    },
    {
        'step': 2,
        'name': 'مزامنة الصفوف من المصدر',
        'script': 'sync_gps_rows.py',
        'output': 'كشف اجهزة GPSللمركبات فرع الدمام 2026_محدث_مطابق.xlsx',
    },
    {
        'step': 3,
        'name': 'تطبيق التنسيق الاحترافي',
        'script': 'apply_formatting.py',
        'output': 'كشف اجهزة GPSللمركبات فرع الدمام 2026_محدث_نهائي.xlsx',
    },
    {
        'step': 4,
        'name': 'دمج احترافي مع الحفاظ على التنسيق',
        'script': 'merge_gps_pro.py',
        'output': 'كشف اجهزة GPSللمركبات فرع الدمام 2026_محدث_احترافي.xlsx',
    },
    {
        'step': 5,
        'name': 'إنشاء الملف النهائي المميز',
        'script': 'finalize_gps.py',
        'output': 'كشف_اجهزة_GPS_الدمام_2026_نهائي_مميز.xlsx',
    },
]

LINE = '─' * 55

def run_step(info):
    """تشغيل سكريبت واحد وإرجاع True عند النجاح."""
    script_path = os.path.join(BASE_DIR, info['script'])
    if not os.path.exists(script_path):
        print(f"  [ERROR] السكريبت غير موجود: {info['script']}")
        return False

    start = time.time()
    result = subprocess.run(
        [sys.executable, script_path],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    elapsed = time.time() - start

    if result.stdout:
        for line in result.stdout.strip().splitlines():
            print(f"  {line}")
    if result.stderr:
        for line in result.stderr.strip().splitlines():
            print(f"  [WARN] {line}")

    if result.returncode != 0:
        print(f"  [FAILED] خطأ في التشغيل (exit code {result.returncode})")
        return False

    # تحقق من وجود ملف الإخراج
    out_path = os.path.join(BASE_DIR, info['output'])
    if os.path.exists(out_path):
        size_kb = os.path.getsize(out_path) / 1024
        print(f"  ✔ الملف: {info['output']} ({size_kb:.1f} KB)")
    print(f"  ⏱  الوقت: {elapsed:.2f} ثانية")
    return True


def main():
    parser = argparse.ArgumentParser(description='GPS Pipeline Runner')
    parser.add_argument('--step', type=int, help='تشغيل خطوة واحدة فقط')
    parser.add_argument('--from',  dest='from_step', type=int, default=1,
                        help='البداية من خطوة معينة')
    args = parser.parse_args()

    steps = PIPELINE
    if args.step:
        steps = [p for p in PIPELINE if p['step'] == args.step]
        if not steps:
            print(f"[ERROR] خطوة غير موجودة: {args.step}")
            sys.exit(1)
    elif args.from_step > 1:
        steps = [p for p in PIPELINE if p['step'] >= args.from_step]

    print(LINE)
    print(' نظام بن زومة — خط أنابيب GPS الكامل')
    print(LINE)
    print(f" عدد الخطوات: {len(steps)}")
    print(LINE)

    total_start = time.time()
    failed = []

    for info in steps:
        print(f"\n[الخطوة {info['step']}/5] {info['name']}")
        print(f"  السكريبت: {info['script']}")
        ok = run_step(info)
        if not ok:
            failed.append(info['step'])
            ans = input(f"\n  هل تريد المتابعة رغم الخطأ؟ (y/N): ").strip().lower()
            if ans != 'y':
                print("\n[STOPPED] توقف خط الأنابيب.")
                sys.exit(1)

    total = time.time() - total_start
    print(f"\n{LINE}")
    if not failed:
        print(f" ✅ اكتمل خط الأنابيب بنجاح في {total:.1f} ثانية")
        print(f" الملف النهائي: كشف_اجهزة_GPS_الدمام_2026_نهائي_مميز.xlsx")
    else:
        print(f" ⚠️  اكتمل مع أخطاء في الخطوات: {failed}")
    print(LINE)


if __name__ == '__main__':
    main()


