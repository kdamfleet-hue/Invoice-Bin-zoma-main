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

# GET/POST /api/documents used to be defined here as well. routes/documents.py registers the
# same rule first, so this copy was never reachable — and unlike the live one it hard-coded
# branch_id=1 and listed every branch's documents with no branch filter. Removing the shadow
# so a change in blueprint registration order can never silently switch to it. The DELETE
# and /file routes below are unique to this module and stay.


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

