from flask import Blueprint, render_template, session
from helpers import login_required

schedule_vehicles_bp = Blueprint("schedule_vehicles", __name__)

@schedule_vehicles_bp.route("/schedule/vehicles")
@login_required
def schedule_vehicles():
    return render_template(
        "schedule_fleet.html",
        active_branch_id=session.get("active_branch_id", 1),
        active_branch=session.get("active_branch", {}),
        snap_tab="schedule_vehicles",
    )
