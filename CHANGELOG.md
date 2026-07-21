# CHANGELOG — نظام بن زومة لإدارة الأسطول

جميع التغييرات الجوهرية على هذا المشروع موثقة هنا.
يتبع هذا الملف معيار [Semantic Versioning](https://semver.org/lang/ar/).

---

## [2.0.0] — 2026-07-21

### 🔒 أمان (Security)
- **إزالة الأسرار المكشوفة من Dockerfile**: تم حذف `SECRET_KEY`, `ADMIN_USERNAME`, `MASTER_PASSWORD` من صورة Docker. تُمرَّر الآن عبر متغيرات البيئة فقط عند التشغيل.
- حذف ملف `deploy.yml` القديم (فرع master) الذي كان يسبب فشل SSH (Exit Code 255).

### 🏗️ إعادة هيكلة (Refactoring)
- نقل 43 سكربت إصلاح/تحديث يدوي (`fix_*.py`, `update_*.py`, `clean_*.py`, إلخ) إلى `Archived_Scripts/scripts/`.
- نقل ملفات HTML المستقلة (`index.html`, `magazine_presentation.html`, إلخ) وملفات CSV إلى `Archived_Scripts/data/`.
- تنظيف جذر المشروع: من 90+ ملف إلى الملفات الأساسية فقط.

### 🐛 إصلاحات (Fixes)
- إصلاح زر المعاينة في صفحة أبشر (`absher_import.html`): إضافة `type="button"` وتنبيهات خطأ واضحة.
- إصلاح `executemany` للإدراج الجماعي في `/api/employees` لمنع timeout.
- إصلاح `branch_id` المفقود عند إنشاء سائقين جدد عبر `api_sync_excel`.

### 📋 بنية تحتية
- إنشاء فرع نسخة احتياطية: `pre-v2-backup`.
- إنشاء ملف `CHANGELOG.md` لتوثيق التغييرات.
