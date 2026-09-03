import os
import io
import base64
import requests
import openpyxl
import logging
import secrets
from urllib.parse import urlsplit
from flask import Blueprint, render_template, session, request, jsonify

from helpers import login_required, load_logo, blob_set, normalize_plate

logger = logging.getLogger("InvoiceApp")
gps_bp = Blueprint('gps', __name__)

GPS_USER = os.environ.get("GPS_USER", "")
GPS_PASS = os.environ.get("GPS_PASS", "")
GPS_API_BASE = os.environ.get(
    "GPS_API_BASE", "https://fleetmanagement-api-clust03.gpscockpit.com/api/"
).rstrip("/")
# 360Locate loads devices first, then resolves their live positions through StateLookup.
# Keep URLs configurable so a provider-side cluster change does not require a code edit.
GPS_DEVICES_URL = os.environ.get("GPS_DEVICES_URL", f"{GPS_API_BASE}/device/Limited")
GPS_STATE_URL = os.environ.get("GPS_STATE_URL", f"{GPS_API_BASE}/StateLookup")
GPS_REFRESH_URL = os.environ.get("GPS_REFRESH_URL", f"{GPS_API_BASE}/Authentication/RefreshToken")
GPS_PERMANENT_TOKEN = os.environ.get("GPS_TOKEN") or os.environ.get("GPS_PERMANENT_TOKEN", "")
GPS_AUTH_SCHEME = os.environ.get("GPS_AUTH_SCHEME", "GpsCockpitApiKey")

def get_gps_token():
    return GPS_PERMANENT_TOKEN

def _gps_headers(token, scheme=None):
    return {
        "Authorization": f"{scheme or GPS_AUTH_SCHEME} {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

def _gps_provider_headers(token, request_id=None):
    """Exchange a modern refresh token for a short-lived access token.

    Legacy API 360 tokens are kept as a fallback for existing deployments.
    Neither token nor response content is written to logs.
    """
    try:
        response = requests.post(
            GPS_REFRESH_URL,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            json={"RefreshToken": token},
            timeout=20,
        )
        if response.status_code == 200:
            payload = _gps_json(response, "token refresh")
            access_token = payload.get("token") or payload.get("accessToken") if isinstance(payload, dict) else None
            if access_token:
                return _gps_headers(access_token, "Bearer")
        else:
            logger.warning(
                "GPS token refresh rejected request_id=%s host=%s status=%s",
                request_id, urlsplit(GPS_REFRESH_URL).netloc, response.status_code,
            )
    except (requests.Timeout, requests.ConnectionError):
        logger.warning("GPS token refresh unavailable; trying configured legacy auth")
    except Exception:
        logger.warning("GPS token refresh failed; trying configured legacy auth")
    return _gps_headers(token)

def _gps_json(response, label):
    ctype = response.headers.get("Content-Type", "")
    if "application/json" not in ctype.lower():
        logger.warning("GPS %s returned non-JSON content type %s", label, ctype[:100])
        return None
    try:
        return response.json()
    except ValueError:
        logger.warning("GPS %s returned invalid JSON", label)
        return None


@gps_bp.route("/api/gps")
@login_required
def get_gps_locations():
    request_id = secrets.token_hex(6)
    token = get_gps_token()
    if not token:
        return (
            jsonify({"error": "خدمة التتبع غير مهيأة — لم يتم ضبط مفتاح GPS (GPS_TOKEN).", "request_id": request_id}),
            503,
        )

    headers = _gps_provider_headers(token, request_id)
    try:
        devices_response = requests.get(
            GPS_DEVICES_URL,
            headers=headers,
            params={
                "isActive": "null",
                "includeGroups": "false",
                "uniqueDevices": "false",
                "includeGroupIds": "true",
                "IncludeHierarchyGroupIds": "false",
            },
            timeout=20,
        )
        if devices_response.status_code != 200:
            logger.warning("GPS device lookup failed request_id=%s host=%s status=%s", request_id, urlsplit(GPS_DEVICES_URL).netloc, devices_response.status_code)
            result = jsonify({"error": "تعذّر جلب أجهزة التتبع من المزوّد حالياً.", "request_id": request_id})
            result.headers["X-GPS-Request-ID"] = request_id
            return result, 502
        devices_payload = _gps_json(devices_response, "device lookup")
        if devices_payload is None:
            result = jsonify({"error": "استجابة أجهزة التتبع غير صالحة من المزوّد.", "request_id": request_id})
            result.headers["X-GPS-Request-ID"] = request_id
            return result, 502

        devices = devices_payload if isinstance(devices_payload, list) else (
            devices_payload.get("items") or devices_payload.get("devices") or []
        )
        device_by_id = {}
        device_ids = []
        for item in devices:
            if not isinstance(item, dict) or item.get("id") is None:
                continue
            raw_id = item.get("id")
            try:
                device_id = int(raw_id)
            except (TypeError, ValueError):
                device_id = str(raw_id)
            device_ids.append(device_id)
            asset = item.get("asset") or {}
            device_by_id[str(raw_id)] = {
                "id": asset.get("id", raw_id),
                "name": asset.get("name") or item.get("name") or "مركبة",
                "plate": asset.get("plateNumber") or "",
            }
        if not device_ids:
            return jsonify([])

        state_response = requests.post(
            GPS_STATE_URL,
            headers=headers,
            json={
                "deviceIds": device_ids,
                "driverIds": [],
                "previousLookupTimestamp": None,
                "deviceState": 0,
                "activeOnly": False,
            },
            timeout=20,
        )
        if state_response.status_code != 200:
            logger.warning("GPS state lookup failed with status %s", state_response.status_code)
            result = jsonify({"error": "تعذّر جلب مواقع الأسطول من المزوّد حالياً.", "request_id": request_id})
            result.headers["X-GPS-Request-ID"] = request_id
            return result, 502
        state_payload = _gps_json(state_response, "state lookup")
        if state_payload is None:
            result = jsonify({"error": "استجابة مواقع الأسطول غير صالحة من المزوّد.", "request_id": request_id})
            result.headers["X-GPS-Request-ID"] = request_id
            return result, 502

        states = state_payload.get("deviceStates", {}) if isinstance(state_payload, dict) else {}
        locations = []
        if isinstance(states, dict):
            for device_id, state in states.items():
                if not isinstance(state, dict):
                    continue
                position = state.get("currentPosition") or state.get("cellPosition") or {}
                meta = device_by_id.get(str(device_id), {"id": device_id, "name": "مركبة", "plate": ""})
                latitude = position.get("latitude")
                longitude = position.get("longitude")
                communication = state.get("communicationState") or {}
                locations.append({
                    "id": meta["id"],
                    "name": meta["name"],
                    "plate": meta["plate"],
                    "lat": latitude,
                    "lng": longitude,
                    "latitude": latitude,
                    "longitude": longitude,
                    "online": bool(communication.get("isOnline")) or bool(state.get("isMoving")),
                    "updated_at": position.get("updateTimestamp"),
                })
        result = jsonify(locations)
        result.headers["X-GPS-Request-ID"] = request_id
        return result
    except requests.Timeout:
        logger.warning("GPS timeout request_id=%s", request_id)
        result = jsonify({"error": "تجاوز وقت الاستجابة من خدمة GPS.", "request_id": request_id})
        result.headers["X-GPS-Request-ID"] = request_id
        return result, 504
    except requests.ConnectionError:
        logger.warning("GPS connection failure request_id=%s", request_id)
        result = jsonify({"error": "تعذّر الاتصال بخدمة GPS.", "request_id": request_id})
        result.headers["X-GPS-Request-ID"] = request_id
        return result, 503
    except Exception as e:
        logger.exception("GPS API error request_id=%s", request_id)
        result = jsonify({"error": "حدث خطأ غير متوقع أثناء جلب بيانات GPS.", "request_id": request_id})
        result.headers["X-GPS-Request-ID"] = request_id
        return result, 500


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
            from app import db
            db.session.rollback()
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
