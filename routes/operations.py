import logging
from flask import Blueprint, render_template, session, request, jsonify
from helpers import login_required, load_logo, blob_get, blob_set, audit_and_verify, _audit_add, current_branch_id, branch_scope

logger = logging.getLogger("InvoiceApp")
operations_bp = Blueprint('operations', __name__)

@operations_bp.route("/oils")
@login_required
def oils():
    google_user = session.get("google_user")
    b64_en = load_logo()
    return render_template("oils.html", google_user=google_user, b64_en=b64_en)
