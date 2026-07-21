import os
import io
import base64
import requests
import openpyxl
import logging
from flask import Blueprint, render_template, session, request, jsonify

from helpers import login_required, load_logo, blob_set, normalize_plate

logger = logging.getLogger("InvoiceApp")
gps_bp = Blueprint('gps', __name__)

GPS_USER = os.environ.get("GPS_USER", "")
GPS_PASS = os.environ.get("GPS_PASS", "")
GPS_ASSET_URL = os.environ.get(
    "GPS_ASSET_URL", "https://fleetmanagement-api-clust03.gpscockpit.com/api/asset"
)
GPS_PERMANENT_TOKEN = os.environ.get("GPS_TOKEN") or os.environ.get("GPS_PERMANENT_TOKEN", "")

def get_gps_token():
    return GPS_PERMANENT_TOKEN


@gps_bp.route("/api/gps")
@login_required
def get_gps_locations():
    token = get_gps_token()
    if not token:
        return (
            jsonify({"error": "خدمة التتبع غير مهيأة — لم يتم ضبط مفتاح GPS (GPS_TOKEN)."}),
            503,
        )

    headers = {
        "Authorization": f"GpsCockpitApiKey {token}",
        "Accept": "application/json",
    }
    try:
        response = requests.get(GPS_ASSET_URL, headers=headers, timeout=20)
        if response.status_code != 200:
            logger.warning("GPS API non-200 %s: %s", response.status_code, response.text[:300])
            return jsonify({"error": "تعذّر جلب بيانات GPS من المزوّد حالياً."}), 502
        
        ctype = response.headers.get("Content-Type", "")
        if "application/json" not in ctype:
            logger.warning("GPS API returned non-JSON (%s). Check GPS_ASSET_URL.", ctype)
            return jsonify({"error": "استجابة GPS غير صالحة — تأكد من ضبط GPS_ASSET_URL على نقطة API."}), 502
        return jsonify(response.json())
    except requests.Timeout:
        return jsonify({"error": "تجاوز وقت الاستجابة من خدمة GPS."}), 504
    except requests.ConnectionError:
        return jsonify({"error": "تعذّر الاتصال بخدمة GPS."}), 503
    except Exception as e:
        logger.error("GPS API error: %s", e)
        return jsonify({"error": "حدث خطأ غير متوقع أثناء جلب بيانات GPS."}), 500


@gps_bp.route("/gps_dashboard")
@login_required
def gps_dashboard():
    return render_template("gps_dashboard.html", google_user=session.get("google_user"), b64_en=load_logo())


@gps_bp.route("/gps_devices")
@login_required
def gps_devices():
    return render_template("gps_devices.html", google_user=session.get("google_user"), b64_en=load_logo())


@gps_bp.route("/gps_sync")
@login_required
def gps_sync():
    google_user = session.get("google_user")
    b64_en = load_logo()
    return render_template("gps_sync.html", google_user=google_user, b64_en=b64_en)


@gps_bp.route("/api/gps_devices", methods=["GET", "POST"])
@login_required
def gps_devices_data():
    """Persist the GPS tracking-device inventory (editable). Sandboxed for workstation."""
    if request.method == "POST":
        try:
            rows = (request.json or {}).get("rows", [])
            blob_set("gps_devices_data", rows)
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    # GET logic is currently handled globally by /api/<table>, but added here for completeness
    from helpers import blob_get
    data = blob_get("gps_devices_data")
    if data:
        return jsonify({"success": True, "rows": data})
    return jsonify({"success": False, "rows": []})


@gps_bp.route("/api/gps_sync", methods=["POST"])
@login_required
def api_gps_sync():
    if "source_file" not in request.files or "target_file" not in request.files:
        return jsonify({"success": False, "error": "الرجاء رفع الملفين المطلوبة"}), 400

    src_file = request.files["source_file"]
    tgt_file = request.files["target_file"]

    try:
        wb_src = openpyxl.load_workbook(src_file, data_only=True)
        ws_src = wb_src.active

        headers = {}
        for c in range(1, ws_src.max_column + 1):
            val = ws_src.cell(row=4, column=c).value
            if val:
                headers[str(val).strip()] = c

        if "رقم اللوحة" not in headers:
            headers = {}
            for c in range(1, ws_src.max_column + 1):
                val = ws_src.cell(row=1, column=c).value
                if val:
                    headers[str(val).strip()] = c

        lookup = {}
        plate_src_col = headers.get("رقم اللوحة")
        if plate_src_col:
            start_row = 5 if "رقم اللوحة" in [ws_src.cell(row=4, column=c).value for c in range(1, ws_src.max_column + 1)] else 2
            for r in range(start_row, ws_src.max_row + 1):
                plate_val = ws_src.cell(row=r, column=plate_src_col).value
                norm = normalize_plate(plate_val)
                if norm:
                    row_data = {}
                    for col_name, c_idx in headers.items():
                        row_data[col_name] = ws_src.cell(row=r, column=c_idx).value
                    lookup[norm] = row_data

        wb = openpyxl.load_workbook(tgt_file)
        ws = wb.active

        plate_col = 9
        vin_col = 1
        sn_col = 2
        year_col = 3
        model_col = 4
        make_col = 5
        reg_col = 6
        branch_col = 7

        match_count = 0
        update_count = 0

        for r in range(6, ws.max_row + 1):
            plate_val = ws.cell(row=r, column=plate_col).value
            if not plate_val:
                continue
            norm = normalize_plate(plate_val)
            if norm in lookup:
                src = lookup[norm]
                match_count += 1
                updates = [
                    (vin_col, "رقم الهيكل"),
                    (sn_col, "الرقم التسلسلي"),
                    (year_col, "سنة الصنع"),
                    (model_col, "الطراز"),
                    (make_col, "الماركة"),
                    (reg_col, "نوع التسجيل"),
                    (branch_col, "الفرع"),
                ]
                for col_idx, src_col_name in updates:
                    if src_col_name in src:
                        new_val = src[src_col_name]
                        if new_val is not None and str(new_val).strip() != "" and str(new_val).lower() != "nan":
                            ws.cell(row=r, column=col_idx).value = new_val
                            update_count += 1

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        b64 = base64.b64encode(output.read()).decode("utf-8")

        return jsonify({
            "success": True,
            "matches": match_count,
            "updates": update_count,
            "file_b64": b64,
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
