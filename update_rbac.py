import re

with open("routes/schedule.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("from helpers import login_required", "from helpers import login_required, role_required")
content = content.replace("@schedule_bp.route(\"/schedule\")\n@login_required", "@schedule_bp.route(\"/schedule\")\n@role_required('admin', 'operations')")
content = content.replace("@schedule_bp.route(\"/washing\")\n@login_required", "@schedule_bp.route(\"/washing\")\n@role_required('admin', 'operations', 'maintenance')")
content = content.replace("@schedule_bp.route(\"/api/schedule_data\", methods=[\"GET\", \"POST\"])\n@login_required", "@schedule_bp.route(\"/api/schedule_data\", methods=[\"GET\", \"POST\"])\n@role_required('admin', 'operations')")
content = content.replace("@schedule_bp.route(\"/api/washing_data\", methods=[\"GET\", \"POST\"])\n@login_required", "@schedule_bp.route(\"/api/washing_data\", methods=[\"GET\", \"POST\"])\n@role_required('admin', 'operations', 'maintenance')")
content = content.replace("@schedule_bp.route(\"/api/generate_schedule\", methods=[\"POST\"])\n@login_required", "@schedule_bp.route(\"/api/generate_schedule\", methods=[\"POST\"])\n@role_required('admin', 'operations')")
content = content.replace("@schedule_bp.route(\"/api/generate_washing\", methods=[\"POST\"])\n@login_required", "@schedule_bp.route(\"/api/generate_washing\", methods=[\"POST\"])\n@role_required('admin', 'operations', 'maintenance')")

with open("routes/schedule.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated RBAC in schedule.py")
