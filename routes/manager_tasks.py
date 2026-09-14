# routes/manager_tasks.py — غرفة عمليات المسؤول (لا إرسال بريد)
from datetime import date
from flask import render_template, session, abort
from helpers import login_required, load_logo, current_branch_id

from routes.operations import operations_bp

MANAGER_ROLES = {"admin", "branch_manager", "operations"}

SEED = [
    {"ref": "MT-014", "title": "تأمين حساب Google: Takeout وربط Manus", "status": "وارد", "priority": "عاجل", "category": "أمن", "waiting": "—", "due": "2026-09-14", "meta": "تنفيذ من المتصفح. لا تخزين رموز."},
    {"ref": "MT-015", "title": "تدوير كلمة مرور نظام التتبع", "status": "وارد", "priority": "عالي", "category": "تتبع", "waiting": "—", "due": "2026-09-14", "meta": "بعد التحقق من الدخول."},
    {"ref": "MT-016", "title": "حسم هوية اللوحة: ب س ل 5541 × أ ص هـ 6135", "status": "قيد التنفيذ", "priority": "عاجل", "category": "تعارض", "waiting": "—", "due": "2026-09-14", "meta": "يُوقف الاعتماد حتى تثبيت لوحة واحدة."},
    {"ref": "MT-017", "title": "تجديد المنتهي والقريب — تجزئة", "status": "قيد التنفيذ", "priority": "عالي", "category": "وثائق", "waiting": "—", "due": "2026-09-18", "meta": "19 منتهية + 12 خلال 30 يوماً."},
    {"ref": "MT-018", "title": "اعتماد جدول سبتمبر — نسخة سيادية واحدة", "status": "بانتظار اعتماد", "priority": "عاجل", "category": "تشغيل", "waiting": "نجود عبدالله", "due": "2026-09-14", "meta": "الإرسال ≠ اعتماد."},
    {"ref": "MT-019", "title": "إيقاف الاحتياطي بعد جاهزية ب س ل 5541", "status": "بانتظار اعتماد", "priority": "عاجل", "category": "ورشة", "waiting": "نجود عبدالله", "due": "2026-09-14", "meta": "تم الاطلاع ليست موافقة."},
    {"ref": "MT-020", "title": "تأكيد جملة الجلسة — موظف 102775", "status": "بانتظار اعتماد", "priority": "عاجل", "category": "تحقيق", "waiting": "فيصل العتيبي", "due": "2026-09-14", "meta": "استيضاح 6 سبتمبر."},
    {"ref": "MT-021", "title": "رصيد تجديد رخصة د د و 4282", "status": "بانتظار اعتماد", "priority": "عالي", "category": "شرط", "waiting": "رصيد / جدة", "due": "2026-09-15", "meta": "التفويض معلّق على الرصيد."},
    {"ref": "MT-011", "title": "تنشيط شريحة أ ر و 4071", "status": "مغلق", "priority": "متوسط", "category": "وقود", "waiting": "—", "due": "2026-09-05", "meta": "دليل: رد عبدالعزيز 5 سبتمبر."},
]


def _role_ok():
    if session.get("is_admin"):
        return True
    role = (session.get("role") or session.get("user_role") or "").strip().lower()
    if role in MANAGER_ROLES:
        return True
    user = session.get("user") or session.get("google_user") or {}
    if isinstance(user, dict) and str(user.get("role") or "").lower() in MANAGER_ROLES:
        return True
    return False


@operations_bp.route("/manager-tasks")
@login_required
def manager_tasks_page():
    if not _role_ok():
        abort(403)
    tasks = list(SEED)
    try:
        from models.schema import ManagerTask
        from helpers import branch_scope
        bid = current_branch_id()
        rows = ManagerTask.query.filter(branch_scope(ManagerTask.branch_id, bid)).order_by(ManagerTask.id.asc()).all()
        if rows:
            tasks = []
            for t in rows:
                tasks.append({
                    "ref": f"MT-{t.id:03d}",
                    "title": t.title,
                    "status": t.status,
                    "priority": t.priority,
                    "category": t.category or "أخرى",
                    "waiting": t.waiting_on_name or "—",
                    "due": t.due_date.isoformat() if t.due_date else "—",
                    "meta": (t.details or t.close_evidence or "")[:180],
                })
    except Exception:
        pass

    by = {"وارد": [], "قيد التنفيذ": [], "بانتظار اعتماد": [], "مغلق": []}
    for t in tasks:
        by.setdefault(t["status"], []).append(t)
    open_n = sum(len(by[k]) for k in by if k != "مغلق")
    waiting_n = len(by.get("بانتظار اعتماد") or [])
    urgent_n = sum(1 for t in tasks if t.get("priority") == "عاجل" and t.get("status") != "مغلق")
    today = date.today().isoformat()
    overdue_n = 0
    for t in tasks:
        if t.get("status") == "مغلق":
            continue
        d = t.get("due") or ""
        if d and d <= today:
            overdue_n += 1

    return render_template(
        "manager_tasks.html",
        google_user=session.get("google_user"),
        b64_en=load_logo(),
        columns=by,
        kpi={"open": open_n, "waiting": waiting_n, "overdue": overdue_n, "urgent": urgent_n},
    )
