import re
import json
import base64
import logging
from datetime import datetime
from flask import Blueprint, render_template, session, request, jsonify, send_file
import threading
from helpers import login_required, load_logo, blob_get, blob_set, audit_and_verify, current_branch_id
from models.schema import db, Driver, Document

logger = logging.getLogger("InvoiceApp")
documents_bp = Blueprint('documents', __name__)

_ALERTS_CENTER_LOCK = threading.Lock()

@documents_bp.route("/documents")
@login_required
def documents_page():
    return render_template("documents.html", google_user=session.get("google_user"), b64_en=load_logo())

@documents_bp.route("/api/documents", methods=["GET", "POST"])
@login_required
def api_documents():
    branch_id = current_branch_id()
    
    if request.method == "GET":
        docs = Document.query.filter_by(branch_id=branch_id).all()
        rows = []
        for d in docs:
            rows.append({
                "id": str(d.id),
                "entity_type": d.entity_type,
                "entity_ref": d.entity_ref,
                "doc_type": d.doc_type,
                "number": d.number,
                "expiry": d.expiry.strftime('%Y-%m-%d') if d.expiry else "",
                "notes": d.notes,
                "ts": d.upload_date.strftime('%Y-%m-%d') if d.upload_date else "",
                "file": {"name": "ملف", "mime": d.mime_type, "size": d.file_size}
            })
        return jsonify({"success": True, "rows": rows, "doc_types": DOC_TYPES})
        
    body = request.get_json(silent=True) or {}
    
    current_count = Document.query.filter_by(branch_id=branch_id).count()
    if current_count >= DOC_MAX_ROWS:
        return jsonify({"success": False, "error": "بلغت الحد الأقصى لعدد الوثائق في هذا الفرع (%d)." % DOC_MAX_ROWS}), 400
        
    f = body.get("file") or {}
    data = f.get("data") or ""
    mime = (f.get("mime") or "").lower().strip()
    
    if not data or not str(data).startswith("data:"):
        return jsonify({"success": False, "error": "الملف مطلوب."}), 400
    if mime not in DOC_ALLOWED_MIME:
        return jsonify({"success": False, "error": "نوع الملف غير مدعوم (صور JPG/PNG/WebP/GIF أو PDF فقط)."}), 400
        
    size = _b64_size(data)
    if size <= 0 or size > DOC_MAX_FILE_BYTES:
        return jsonify({"success": False, "error": "حجم الملف يتجاوز 2.5 ميجابايت."}), 400
    if not _sniff_ok(data, mime):
        return jsonify({"success": False, "error": "محتوى الملف لا يطابق نوعه المُعلَن."}), 400
        
    if not body.get("entity_ref"):
        return jsonify({"success": False, "error": "حدّد المركبة/الموظف (المرجع)."}), 400

    def parse_date(dstr):
        if not dstr: return None
        try: return datetime.strptime(str(dstr)[:10], '%Y-%m-%d').date()
        except: return None

    try:
        new_doc = Document(
            branch_id=branch_id,
            doc_type=str(body.get("doc_type") or "أخرى")[:60],
            entity_type="vehicle" if body.get("entity_type") == "vehicle" else "employee",
            entity_ref=str(body.get("entity_ref") or "")[:120],
            number=str(body.get("number") or "")[:80],
            expiry=parse_date(body.get("expiry")),
            notes=str(body.get("notes") or "")[:300],
            file_data=data,
            mime_type=mime,
            file_size=size,
            file_path="base64", # legacy dummy path
            upload_date=datetime.now().date()
        )
        db.session.add(new_doc)
        db.session.flush() # To get ID
        
        audit = AuditLog(
            user_id=getattr(g, 'user', None),
            branch_id=branch_id,
            action="إضافة مستند",
            target_table="erp_documents",
            target_id=str(new_doc.id)
        )
        db.session.add(audit)
        db.session.commit()
        
        row_res = {
            "id": str(new_doc.id),
            "entity_type": new_doc.entity_type,
            "entity_ref": new_doc.entity_ref,
            "doc_type": new_doc.doc_type,
            "number": new_doc.number,
            "expiry": new_doc.expiry.strftime('%Y-%m-%d') if new_doc.expiry else "",
            "notes": new_doc.notes,
            "ts": new_doc.upload_date.strftime('%Y-%m-%d') if new_doc.upload_date else "",
            "file": {"name": "ملف", "mime": new_doc.mime_type, "size": new_doc.file_size}
        }
        return jsonify({"success": True, "row": row_res})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error saving document: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@documents_bp.route("/alerts")
@login_required
def alerts_page():
    """Admin page to configure the automatic daily document-expiry email digest."""
    if not session.get("is_admin"):
        return redirect(url_for("dashboard.index"))
    return render_template("alerts.html", google_user=session.get("google_user"), b64_en=load_logo())

@documents_bp.route("/api/alert_settings", methods=["GET", "POST"])
@login_required
def api_alert_settings():
    if not session.get("is_admin"):
        return jsonify({"error": "forbidden"}), 403
    if request.method == "GET":
        cfg = _alert_cfg()
        cfg["mail_configured"] = bool(app.config.get("MAIL_USERNAME") and app.config.get("MAIL_PASSWORD"))
        cfg["preview_count"] = len(_collect_all_branches_alerts(cfg["window_days"]))
        return jsonify({"success": True, "settings": cfg})
    body = request.get_json(silent=True) or {}

    def _recips(v):
        if isinstance(v, str):
            v = re.split(r"[,;\s]+", v)
        return [e.strip() for e in (v or []) if isinstance(e, str) and "@" in e.strip()][:50]

    if body.get("action") == "test":     # send a one-off test now
        cfg = _alert_cfg()
        recips = _recips(body.get("recipients")) or cfg["recipients"]
        try:
            wd = max(1, min(180, int(body.get("window_days") or cfg["window_days"])))
        except (TypeError, ValueError):
            wd = cfg["window_days"]
        res = _send_scheduled_digest(recips, wd)
        if res.get("sent"):
            _audit_add("إرسال تجريبي", "تنبيهات الوثائق التلقائية", res.get("count"),
                       "إلى: " + ", ".join(res.get("recipients", [])))
        return jsonify({"success": res.get("sent", False), **res})

    try:
        hour = max(0, min(23, int(body.get("hour", 7))))
    except (TypeError, ValueError):
        hour = 7
    try:
        wd = max(1, min(180, int(body.get("window_days", 30))))
    except (TypeError, ValueError):
        wd = 30
    cfg = {"enabled": bool(body.get("enabled")), "recipients": _recips(body.get("recipients")),
           "hour": hour, "window_days": wd, "last_sent": _alert_cfg().get("last_sent", "")}
    _alert_cfg_set(cfg)
    _audit_add("إعداد", "تنبيهات الوثائق التلقائية", len(cfg["recipients"]),
               ("مُفعّلة" if cfg["enabled"] else "مُعطّلة") + " · الساعة %d · خلال %d يوم" % (hour, wd))
    return jsonify({"success": True, "settings": cfg})

@documents_bp.route("/api/alerts_center/update", methods=["POST"])
@login_required
def alerts_center_update():
    try:
        body = request.get_json(silent=True) or {}
        src = body.get("src")
        target_field = body.get("targetField")
        if target_field not in ("date", "name", "plate", "doctype"):
            return jsonify({"success": False, "error": "طلب غير صالح."}), 400
        value, err_resp, err_code = _alerts_center_clean_value(target_field, body.get("value"))
        if err_resp is not None:
            return err_resp, err_code

        if src == "schedule":
            if target_field == "doctype":
                return jsonify({"success": False, "error": "طلب غير صالح."}), 400
            section = body.get("section")
            if section not in ("main", "spare"):
                return jsonify({"success": False, "error": "طلب غير صالح."}), 400
            try:
                idx = int(body.get("idx"))
            except (TypeError, ValueError):
                return jsonify({"success": False, "error": "طلب غير صالح."}), 400
            if target_field == "date":
                date_field = body.get("dateField")
                if date_field not in ("inspect", "license", "opcard", "drivercard"):
                    return jsonify({"success": False, "error": "طلب غير صالح."}), 400
                store_key = date_field
            else:
                store_key = target_field  # 'name' or 'plate'
            with _ALERTS_CENTER_LOCK:
                sd = blob_get("schedule_data")
                rows = sd.get(section) if isinstance(sd, dict) else None
                if not isinstance(rows, list) or idx < 0 or idx >= len(rows) or not isinstance(rows[idx], dict):
                    return jsonify({"success": False, "error": "لم يعد هذا الصف موجوداً — أعد تحميل الصفحة."}), 409
                row = rows[idx]
                # Anchor identity on whichever field ISN'T being written: plate identifies the
                # row/vehicle slot itself; iqama identifies the driver currently assigned to it.
                if store_key == "plate":
                    akey = _norm_iqama(row.get("iqama")); ok = bool(akey) and akey == _norm_iqama(body.get("iqama"))
                else:  # name, drivercard, inspect, license, opcard — all anchor on the row's plate
                    akey = str(row.get("plate") or "").strip(); ok = bool(akey) and akey == str(body.get("plate") or "").strip()
                if not ok:
                    return jsonify({"success": False, "error": "تغيّرت بيانات الصف — أعد تحميل الصفحة."}), 409
                if store_key in ("name", "plate") and not value:
                    return jsonify({"success": False, "error": "هذا الحقل لا يمكن تفريغه."}), 400
                row[store_key] = value
                blob_set("schedule_data", sd)
            try:
                _harvest_driver_registry(sd)
            except Exception:
                logger.warning("driver_registry harvest failed (non-fatal)")
            try:
                _harvest_vehicle_registry(sd)
            except Exception:
                logger.warning("vehicle_registry harvest failed (non-fatal)")
            _audit_add("تعديل", "مركز تنبيهات الوثائق", None, store_key + ": " + (value or "تفريغ") + " — " + (row.get("name") or row.get("plate") or ""))
            return jsonify({"success": True, "value": value})

        if src == "employee":
            if target_field == "doctype":
                return jsonify({"success": False, "error": "طلب غير صالح."}), 400
            try:
                idx = int(body.get("idx"))
            except (TypeError, ValueError):
                return jsonify({"success": False, "error": "طلب غير صالح."}), 400
            store_idx = None  # 'name' is resolved below, once the current row is known
            if target_field == "date":
                try:
                    store_idx = int(body.get("dateField"))
                except (TypeError, ValueError):
                    return jsonify({"success": False, "error": "طلب غير صالح."}), 400
                if store_idx not in (10, 11):  # matches employees.html COLS[10]/[11] = إقامة/جواز expiry
                    return jsonify({"success": False, "error": "طلب غير صالح."}), 400
            elif target_field == "plate":
                store_idx = 9  # COLS[9] = رقم اللوحة
            with _ALERTS_CENTER_LOCK:
                rows = blob_get("employees")
                if not isinstance(rows, list) or idx < 0 or idx >= len(rows) or not isinstance(rows[idx], list):
                    return jsonify({"success": False, "error": "لم يعد هذا الصف موجوداً — أعد تحميل الصفحة."}), 409
                row = rows[idx]
                actual_iqama = str(row[1] if len(row) > 1 else "").strip()
                if not actual_iqama or actual_iqama != str(body.get("iqama") or "").strip():
                    return jsonify({"success": False, "error": "تغيّرت بيانات الصف — أعد تحميل الصفحة."}), 409
                if store_idx is None:  # target_field == "name": whichever of COLS[2]/[3] is
                    # actually populated on the CURRENT row — decided server-side, not client-supplied.
                    store_idx = 2 if (row[2] if len(row) > 2 else "") or not (row[3] if len(row) > 3 else "") else 3
                if target_field in ("name", "plate") and not value:
                    return jsonify({"success": False, "error": "هذا الحقل لا يمكن تفريغه."}), 400
                if len(row) <= store_idx:
                    row.extend([""] * (store_idx + 1 - len(row)))
                row[store_idx] = value
                blob_set("employees", rows)
            _audit_add("تعديل", "مركز تنبيهات الوثائق", None, target_field + ": " + (value or "تفريغ") + " — " + (row[2] if len(row) > 2 and row[2] else (row[3] if len(row) > 3 else "")))
            return jsonify({"success": True, "value": value})

        if src == "document":
            store_key = {"date": "expiry", "name": "entity_ref", "plate": "entity_ref", "doctype": "doc_type"}[target_field]
            doc_id = str(body.get("id") or "")
            with _ALERTS_CENTER_LOCK:
                rows = _documents_rows()
                found = next((r for r in rows if r.get("id") == doc_id), None)
                if not found:
                    return jsonify({"success": False, "error": "الوثيقة لم تعد موجودة — أعد تحميل الصفحة."}), 409
                if store_key != "expiry" and not value:
                    return jsonify({"success": False, "error": "هذا الحقل لا يمكن تفريغه."}), 400
                found[store_key] = value
                blob_set("documents_data", {"rows": rows})
            _audit_add("تعديل", "مركز تنبيهات الوثائق", None, store_key + ": " + (value or "تفريغ") + " — " + (found.get("entity_ref") or ""))
            return jsonify({"success": True, "value": value})

        return jsonify({"success": False, "error": "مصدر غير معروف."}), 400
    except Exception:
        logger.exception("alerts_center_update error")
        return jsonify({"success": False, "error": "تعذّر حفظ التعديل."}), 500

@documents_bp.route("/api/send_expiry_alerts", methods=["POST"])
@login_required
def send_expiry_alerts():
    """Manual 'send now' from the dashboard. Recipients from the request or ALERT_RECIPIENTS."""
    body = request.json or {}
    # Lock: require the access code before sending (matches the workstation password).
    if not hmac.compare_digest(str(body.get("lock", "")), WORKSTATION_PASSWORD):
        return jsonify({"success": False, "reason": "locked"}), 403
    recips = body.get("recipients") or ALERT_RECIPIENTS
    if isinstance(recips, str):
        recips = [e.strip() for e in re.split(r"[,;\s]+", recips) if e.strip()]
    rows = body.get("rows")
    filt = (body.get("filter") or "").strip()
    if isinstance(rows, list) and rows:
        res = _send_expiry_alert_email(recips, rows=rows[:1000], filter_label=filt)
    else:
        res = _send_expiry_alert_email(recips, filter_label=filt)
    if res.get("sent"):
        _audit_add("إرسال", "تنبيهات الوثائق بالبريد", res.get("count"),
                   (("الفرز: " + filt + " — ") if filt else "") + "إلى: " + ", ".join(res.get("recipients", [])))
    return jsonify({"success": res.get("sent", False), **res})

@documents_bp.route("/api/cron/expiry_alerts", methods=["GET", "POST"])
def cron_expiry_alerts():
    """Token-protected trigger for an external daily scheduler (ArabCord cron / cron-job.org).
    Not login-protected; guarded by ALERT_CRON_KEY. Uses ALERT_RECIPIENTS for the recipient list."""
    key = request.args.get("key", "")
    if not key and request.is_json:
        key = (request.json or {}).get("key", "")
    if not ALERT_CRON_KEY or not hmac.compare_digest(str(key), ALERT_CRON_KEY):
        return jsonify({"success": False, "error": "unauthorized"}), 401
    res = _send_expiry_alert_email(ALERT_RECIPIENTS)
    if res.get("sent"):
        _audit_add("إرسال تلقائي", "تنبيهات الوثائق بالبريد", res.get("count"),
                   "مجدول — إلى: " + ", ".join(res.get("recipients", [])))
    return jsonify({"success": res.get("sent", False), **res})