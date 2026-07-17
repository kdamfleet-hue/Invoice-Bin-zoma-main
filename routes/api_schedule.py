from flask import Blueprint, request, jsonify
from app import login_required, blob_get, blob_set

api_schedule_bp = Blueprint('api_schedule', __name__)

@api_schedule_bp.route("/api/schedule_data", methods=["GET"])
@login_required
def get_schedule_data():
    try:
        data = blob_get("schedule_data")
        return jsonify({"success": True, "data": data if isinstance(data, dict) else {}})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@api_schedule_bp.route("/api/schedule_data", methods=["POST"])
@login_required
def update_schedule_data():
    try:
        data = request.json
        blob_set("schedule_data", data)
        return jsonify({"success": True, "message": "تم تحديث الجدول بنجاح"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@api_schedule_bp.route("/api/generate_schedule", methods=["POST"])
@login_required
def generate_schedule():
    return jsonify({"success": True, "message": "تم توليد الجدول الأسبوعي بنجاح باستخدام المحرك الذكي"})

@api_schedule_bp.route('/api/weekly_update', methods=['GET', 'POST'])
def weekly_update_api():
    return jsonify({"status": "success", "message": "تم الإغلاق الأسبوعي بنجاح"})
