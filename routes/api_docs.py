from flask import Blueprint, request, jsonify, send_file
from helpers import login_required, DOC_TYPES
from models.schema import db, Document
import io
import datetime
import secrets

api_docs_bp = Blueprint('api_docs', __name__)

DOC_ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp", "image/gif", "application/pdf"}
DOC_MAX_FILE_BYTES = 2.5 * 1024 * 1024
DOC_MAX_ROWS = 800

def _b64_size(b64_str):
    if not b64_str:
        return 0
    return len(b64_str) * 3 // 4

@api_docs_bp.route("/api/documents", methods=["GET", "POST"])
@login_required
def api_documents():
    if request.method == "GET":
        docs = Document.query.all()
        rows = []
        for d in docs:
            rows.append({
                "id": str(d.id),
                "entity_type": d.entity_type,
                "entity_ref": d.entity_ref,
                "doc_type": d.doc_type,
                "number": d.number,
                "expiry": str(d.expiry) if d.expiry else "",
                "notes": d.notes,
                "file": {"name": "ملف", "mime": d.mime_type, "size": d.file_size, "data": ""}, # Omit data for list
                "ts": d.upload_date.strftime("%Y-%m-%d %H:%M:%S") if d.upload_date else ""
            })
        return jsonify({"success": True, "rows": rows, "doc_types": DOC_TYPES})

    # POST (Upload)
    body = request.get_json(silent=True) or {}
    
    current_count = Document.query.count()
    if current_count >= DOC_MAX_ROWS:
        return jsonify({"success": False, "error": f"بلغت الحد الأقصى لعدد الوثائق ({DOC_MAX_ROWS})."}), 400

    f = body.get("file") or {}
    data = f.get("data") or ""
    mime = (f.get("mime") or "").lower().strip()

    if not data or not str(data).startswith("data:"):
        return jsonify({"success": False, "error": "الملف مطلوب."}), 400
    if mime not in DOC_ALLOWED_MIME:
        return jsonify({"success": False, "error": "نوع الملف غير مدعوم."}), 400

    size = _b64_size(data)
    if size <= 0 or size > DOC_MAX_FILE_BYTES:
        return jsonify({"success": False, "error": "حجم الملف يتجاوز 2.5 ميجابايت."}), 400

    entity_ref = str(body.get("entity_ref") or "")[:120]
    if not entity_ref:
        return jsonify({"success": False, "error": "حدّد المركبة/الموظف (المرجع)."}), 400

    expiry_date = None
    try:
        expiry_str = str(body.get("expiry") or "")[:10]
        if expiry_str:
            expiry_date = datetime.datetime.strptime(expiry_str, '%Y-%m-%d').date()
    except Exception:
        pass

    new_doc = Document(
        branch_id=1,
        entity_type="vehicle" if body.get("entity_type") == "vehicle" else "employee",
        entity_ref=entity_ref,
        doc_type=str(body.get("doc_type") or "أخرى")[:60],
        number=str(body.get("number") or "")[:80],
        expiry=expiry_date,
        notes=str(body.get("notes") or "")[:300],
        file_data=data,
        mime_type=mime,
        file_size=size,
        file_path="" # empty since we use file_data for backwards compatibility
    )
    
    try:
        db.session.add(new_doc)
        db.session.commit()
        
        row_res = {
            "id": str(new_doc.id),
            "entity_type": new_doc.entity_type,
            "entity_ref": new_doc.entity_ref,
            "doc_type": new_doc.doc_type,
            "number": new_doc.number,
            "expiry": str(new_doc.expiry) if new_doc.expiry else "",
            "notes": new_doc.notes,
            "file": {"name": "ملف", "mime": new_doc.mime_type, "size": new_doc.file_size, "data": ""},
            "ts": new_doc.upload_date.strftime("%Y-%m-%d %H:%M:%S") if new_doc.upload_date else ""
        }
        return jsonify({"success": True, "row": row_res})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@api_docs_bp.route("/api/documents/<int:doc_id>", methods=["DELETE"])
@login_required
def api_documents_delete(doc_id):
    try:
        doc = Document.query.get(doc_id)
        if not doc:
            return jsonify({"success": False, "error": "غير موجود."}), 404
        
        db.session.delete(doc)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@api_docs_bp.route("/api/documents/<int:doc_id>/file")
@login_required
def api_documents_file(doc_id):
    doc = Document.query.get(doc_id)
    if not doc or not doc.file_data:
        return "Not found", 404
    
    try:
        # data:image/png;base64,iVBOR...
        header, b64 = doc.file_data.split(",", 1)
        import base64
        binary = base64.b64decode(b64)
        return send_file(io.BytesIO(binary), mimetype=doc.mime_type)
    except Exception:
        return "Invalid file data", 500

