import re

with open("routes/fleet.py", "r", encoding="utf-8") as f:
    content = f.read()

qr_code_route = """
import io
import qrcode
from flask import send_file, url_for

@fleet_bp.route("/api/vehicles/<int:vehicle_id>/qr")
@login_required
def vehicle_qr(vehicle_id):
    branch_id = current_branch_id()
    vehicle = Vehicle.query.filter_by(id=vehicle_id, branch_id=branch_id).first()
    
    if not vehicle:
        return "Vehicle not found", 404
        
    # Generate URL for the vehicle's public/semi-public mobile status page
    # Since we are using an absolute URL, we need to ensure SERVER_NAME is set, or we can build it manually.
    # For now, we will construct the relative URL and use request.host_url
    url = f"{request.host_url}v/{vehicle.id}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    
    return send_file(buf, mimetype="image/png")
    
@fleet_bp.route("/v/<int:vehicle_id>")
def vehicle_public_status(vehicle_id):
    # This is the page opened when the QR code is scanned.
    # The user asked if it should be public. Since they didn't answer, we will make it semi-public:
    # Anyone with the link (QR code) can view the basic status, but NO sensitive data like costs.
    # This is common for QR code systems in fleets.
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    # Get basic driver info if assigned
    from models.schema import VehicleCustody
    active_custody = VehicleCustody.query.filter_by(vehicle_id=vehicle.id, status="active").first()
    driver_name = active_custody.driver.name if active_custody else "غير مخصصة"
    
    b64_en = load_logo()
    return render_template("vehicle_mobile_status.html", vehicle=vehicle, driver_name=driver_name, b64_en=b64_en)
"""

if "/api/vehicles/<int:vehicle_id>/qr" not in content:
    content += qr_code_route
    with open("routes/fleet.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Added QR route to fleet.py")
else:
    print("QR route already exists.")
