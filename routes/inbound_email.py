"""Manual, read-only inbound email import endpoint.

No inbox connection, scheduler, notification, or outbound email is used here.
"""
from flask import Blueprint, jsonify, request, session

from helpers import login_required, current_branch_id
from services.inbound_email import import_messages

inbound_email_bp = Blueprint('inbound_email', __name__)


@inbound_email_bp.route('/api/inbound-email/import', methods=['POST'])
@login_required
def import_inbound_email_tasks():
    role = str(session.get('role') or session.get('user_role') or '').lower()
    user = session.get('user') or session.get('google_user') or {}
    if isinstance(user, dict):
        role = str(user.get('role') or role).lower()
    if not session.get('is_admin') and role not in {'admin', 'branch_manager', 'operations'}:
        return jsonify({'error': 'forbidden'}), 403
    payload = request.get_json(silent=True) or {}
    messages = payload.get('messages') if isinstance(payload, dict) else None
    if not isinstance(messages, list):
        return jsonify({'error': 'messages must be a list'}), 400
    if len(messages) > 100:
        return jsonify({'error': 'maximum 100 messages per manual import'}), 400
    result = import_messages(messages, branch_id=current_branch_id())
    return jsonify({'read_only': True, 'outbound_email': False, **result})
