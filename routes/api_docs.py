from flask import Blueprint, request, jsonify, render_template, session, send_file
from werkzeug.utils import secure_filename
import pandas as pd
import math
import traceback
import json
import os
import io
from datetime import datetime

import app

api_docs_bp = Blueprint('api_docs', __name__)

@api_docs_bp.route("/api/documents", methods=["GET", "POST"])
@app.login_required
def api_documents():
    if request.method == "GET":
        return jsonify({"success": True, "rows": [app._doc_meta(r) for r in app._documents_rows()], "doc_types": app.DOC_TYPES})
    body = request.get_json(silent=True) or {}
    rows = app._documents_rows()
    if len(rows) >= app.DOC_MAX_ROWS:
        return jsonify({"success": False, "error": "بلغت الحد الأقصى لعدد الوثائق في هذا الفرع (%d)." % app.DOC_MAX_ROWS}), 400
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
    if sum(_b64_size((r.get("file") or {}).get("data", "")) for r in rows) + size > DOC_MAX_BLOB_BYTES:
        return jsonify({"success": False, "error": "امتلأت مساحة أرشيف الفرع — احذف وثائق قديمة."}), 400
    row = {
        "id": "d" + datetime.now().strftime("%Y%m%d%H%M%S") + secrets.token_hex(3),
        "entity_type": "vehicle" if body.get("entity_type") == "vehicle" else "employee",
        "entity_ref": str(body.get("entity_ref") or "")[:120],
        "doc_type": str(body.get("doc_type") or "أخرى")[:60],
        "number": str(body.get("number") or "")[:80],
        "expiry": str(body.get("expiry") or "")[:10],
        "notes": str(body.get("notes") or "")[:300],
        "file": {"name": str(f.get("name") or "ملف")[:160], "mime": mime, "size": size, "data": data},
        "ts": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    if not row["entity_ref"]:
        return jsonify({"success": False, "error": "حدّد المركبة/الموظف (المرجع)."}), 400
    rows.append(row)
    app.blob_set("documents_data", {"rows": rows})
    app._audit_add("إضافة", "أرشيف الوثائق", len(rows), row["doc_type"] + " — " + row["entity_ref"])
    return jsonify({"success": True, "row": app._doc_meta(row)})


@api_docs_bp.route("/api/documents/<doc_id>", methods=["DELETE"])
@app.login_required
def api_documents_delete(doc_id):
    with _ALERTS_CENTER_LOCK:  # avoid racing an alerts-center edit of the same document
        rows = app._documents_rows()
        kept = [r for r in rows if r.get("id") != doc_id]
        if len(kept) == len(rows):
            return jsonify({"success": False, "error": "غير موجود."}), 404
        app.blob_set("documents_data", {"rows": kept})
    app._audit_add("حذف", "أرشيف الوثائق", len(kept), str(doc_id))
    return jsonify({"success": True})


