"""
cleanup.py
==========
ينظّف الملفات المؤقتة والزائدة في مجلد المشروع.

ما يُحذف:
  - ملفات Python المُجمَّعة (__pycache__, *.pyc)
  - ملفات الفحص المؤقتة (verify_output.txt, inspection_*.txt)
  - ملفات الصور المؤقتة التي لا تُستخدم في الإنتاج
  - نسخ GPS الوسيطة (يحتفظ بالنهائي فقط)

ما يُحتفظ به:
  - جميع ملفات .py الإنتاجية
  - جميع ملفات .xlsx الأصلية والنهائية
  - ملفات .env, .gitignore, requirements.txt
  - مجلدات static/, templates/, user_templates/

الاستخدام:
  python cleanup.py           (عرض ما سيُحذف فقط - وضع المعاينة)
  python cleanup.py --delete  (تنفيذ الحذف فعلاً)
"""
import os
import sys
import shutil
import argparse

# ── إعداد الـ encoding ────────────────────────────────────────────────────────
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ── الملفات المؤقتة التي يمكن حذفها ─────────────────────────────────────────
TEMP_FILES = [
    'verify_output.txt',
    'inspection_results.txt',
    'inspection_full.txt',
    'col_map.txt',
    'excel_layout.txt',
    'fleet.db',  # نسخة قديمة من قاعدة البيانات
]

# ── الصور التي لا تُستخدم في الإنتاج ─────────────────────────────────────────
TEMP_IMAGES = [
    'source_img_0.png',
    'source_img_1.png',
    'output-onlinepngtools.png',
]

# ── ملفات GPS الوسيطة (تُحذف بعد توليد الملف النهائي) ────────────────────────
GPS_INTERMEDIATE = [
    'كشف اجهزة GPSللمركبات فرع الدمام 2026_محدث.xlsx',
    'كشف اجهزة GPSللمركبات فرع الدمام 2026_محدث_مطابق.xlsx',
    'كشف اجهزة GPSللمركبات فرع الدمام 2026_محدث_احترافي.xlsx',
]

# ── السكريبتات المؤقتة التي انتهى دورها ──────────────────────────────────────
LEGACY_SCRIPTS = [
    'check_target_cols.py',
    'check_template.py',
    'check_spare.py',
    'check_db.py',
    'inspect_excel.py',
    'inspect_excel_gps.py',
    'inspect_full_gps.py',
    'verify_gps.py',
    'fix_all.py',
    'fix_excel.py',
    'fix_img.py',
    'fix_js.py',
    'patch_footers.py',
    'crop_logo.py',
    'crop_white.py',
    'process_logo.py',
    'process_new_logo.py',
    'process_png_logo.py',
    'replace_links.py',
    'translate_names.py',
    'update_filename.py',
    'extract_new_logo.py',
    'fuzzy_update.py',
    'test_payload.py',
]

LINE = '─' * 55

def get_size(path):
    try:
        return os.path.getsize(path) / 1024
    except Exception:
        return 0

def scan_and_delete(targets, label, dry_run=True):
    """فحص وحذف قائمة ملفات. يُعيد عدد الملفات وحجمها."""
    count = 0
    total_kb = 0.0
    for name in targets:
        path = os.path.join(BASE_DIR, name)
        if os.path.exists(path):
            kb = get_size(path)
            total_kb += kb
            count += 1
            if dry_run:
                print(f"  [معاينة] {name} ({kb:.1f} KB)")
            else:
                try:
                    os.remove(path)
                    print(f"  [حُذف]   {name} ({kb:.1f} KB)")
                except Exception as e:
                    print(f"  [خطأ]    {name}: {e}")
    if count:
        verb = "سيُحذف" if dry_run else "حُذف"
        print(f"  ← {count} ملف {verb} من '{label}' ({total_kb:.1f} KB)")
    return count, total_kb


def clean_pycache(dry_run=True):
    """حذف مجلدات __pycache__ وملفات .pyc."""
    total_kb = 0.0
    count = 0
    pycache = os.path.join(BASE_DIR, '__pycache__')
    if os.path.exists(pycache):
        size = sum(
            os.path.getsize(os.path.join(r, f))
            for r, _, fs in os.walk(pycache) for f in fs
        ) / 1024
        total_kb += size
        count += 1
        if dry_run:
            print(f"  [معاينة] __pycache__/ ({size:.1f} KB)")
        else:
            shutil.rmtree(pycache, ignore_errors=True)
            print(f"  [حُذف]   __pycache__/ ({size:.1f} KB)")
    return count, total_kb


def main():
    parser = argparse.ArgumentParser(description='Project Cleanup Tool')
    parser.add_argument('--delete', action='store_true',
                        help='تنفيذ الحذف فعلاً (افتراضياً: معاينة فقط)')
    parser.add_argument('--gps-intermediate', action='store_true',
                        help='حذف ملفات GPS الوسيطة أيضاً')
    args = parser.parse_args()

    dry_run = not args.delete

    print(LINE)
    print(' أداة تنظيف مشروع Fleet Management')
    if dry_run:
        print(' [وضع المعاينة] — لا شيء سيُحذف')
    else:
        print(' [وضع الحذف] — سيتم حذف الملفات!')
    print(LINE)

    total_count = 0
    total_kb = 0.0

    print('\n[1] ملفات Python المُجمَّعة:')
    c, kb = clean_pycache(dry_run)
    total_count += c; total_kb += kb

    print('\n[2] ملفات التقارير والفحص:')
    c, kb = scan_and_delete(TEMP_FILES, 'مؤقتة', dry_run)
    total_count += c; total_kb += kb

    print('\n[3] الصور المؤقتة:')
    c, kb = scan_and_delete(TEMP_IMAGES, 'صور', dry_run)
    total_count += c; total_kb += kb

    print('\n[4] السكريبتات القديمة:')
    c, kb = scan_and_delete(LEGACY_SCRIPTS, 'legacy', dry_run)
    total_count += c; total_kb += kb

    if args.gps_intermediate:
        print('\n[5] ملفات GPS الوسيطة:')
        final = 'كشف_اجهزة_GPS_الدمام_2026_نهائي_مميز.xlsx'
        if not os.path.exists(os.path.join(BASE_DIR, final)):
            print(f'  [SKIP] الملف النهائي غير موجود بعد — تخطي هذه الخطوة')
        else:
            c, kb = scan_and_delete(GPS_INTERMEDIATE, 'GPS وسيطة', dry_run)
            total_count += c; total_kb += kb

    print(f'\n{LINE}')
    verb = 'سيُحذف' if dry_run else 'حُذف'
    print(f' الإجمالي: {total_count} ملف {verb} ({total_kb:.1f} KB)')
    if dry_run and total_count > 0:
        print(f' لتنفيذ الحذف: python cleanup.py --delete')
    print(LINE)


if __name__ == '__main__':
    main()

