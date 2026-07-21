import codecs
import re

with codecs.open('app.py', 'r', 'utf-8') as f:
    lines = f.readlines()

def extract_function(func_name, start_keyword):
    start = -1
    end = -1
    for i, line in enumerate(lines):
        if start_keyword in line and ('def ' + func_name + '(') in lines[i+1]:
            start = i
            break
        elif ('def ' + func_name + '(') in line and start == -1:
            start = i - 1 # assume decorator above
            break
    
    if start == -1: return None, None
    
    # find end of function
    for i in range(start + 2, len(lines)):
        if lines[i].strip() == '' and (i+1 == len(lines) or lines[i+1].startswith('@app.route') or lines[i+1].startswith('def ') or lines[i+1].startswith('#')):
            end = i + 1
            break
            
    if end == -1: end = len(lines)
    
    func_lines = lines[start:end]
    for i in range(len(func_lines)):
        if '@app.route' in func_lines[i]:
            func_lines[i] = func_lines[i].replace('@app.route', '@api_fleet_bp.route')
            
    return func_lines, (start, end)

routes_to_extract = [
    ('api_gps', '@app.route("/api/gps"'),
    ('api_vehicles_lookup', '@app.route("/api/vehicles_lookup"'),
    ('api_driver_registry', '@app.route("/api/driver_registry"'),
    ('api_vehicle_registry', '@app.route("/api/vehicle_registry"'),
    ('api_gps_devices', '@app.route("/api/gps_devices"'),
    ('api_vehicle_custody_transfer', '@app.route("/api/vehicle_custody_transfer"'),
    ('api_drivers', '@app.route("/api/drivers"'),
    ('api_drivers_post', '@app.route("/api/drivers"'), # same route diff methods
    ('api_drivers_delete', '@app.route("/api/drivers/<int:driver_id>"'),
    ('api_drivers_bulk_delete', '@app.route("/api/drivers/bulk_delete"'),
    ('api_drivers_put', '@app.route("/api/drivers/<int:driver_id>"'),
    ('update_driver_route', '@app.route(\'/update-driver\''),
    ('api_sync_excel', '@app.route("/api/sync_excel"'),
    ('api_fleet_data', '@app.route("/api/fleet_data"'),
    ('api_sync_all_from_drivers', '@app.route("/api/sync_all_from_drivers"'),
    ('api_registry_import', '@app.route("/api/registry_import"'),
    ('api_registry_data', '@app.route("/api/registry_data"'),
    ('api_gps_sync', '@app.route("/api/gps_sync"'),
]

all_code = []
indices_to_delete = []

for func_name, keyword in routes_to_extract:
    code, idx = extract_function(func_name, keyword)
    if code:
        all_code.extend(code)
        indices_to_delete.extend(range(idx[0], idx[1]))
    else:
        print(f"Could not extract {func_name}")

bp_content = '''from flask import Blueprint, request, jsonify, render_template, session
from werkzeug.utils import secure_filename
import pandas as pd
import math
import traceback
import json
import os
from datetime import datetime

# Import helpers from app
import app

api_fleet_bp = Blueprint('api_fleet', __name__)

''' + ''.join(all_code)

# Fix decorator calls to use app module if they are not in standard flask
bp_content = bp_content.replace('@login_required', '@app.login_required')
bp_content = bp_content.replace('blob_get(', 'app.blob_get(')
bp_content = bp_content.replace('blob_set(', 'app.blob_set(')
bp_content = bp_content.replace('_audit_add(', 'app._audit_add(')
bp_content = bp_content.replace('logger.', 'app.logger.')
bp_content = bp_content.replace('sanitize_data(', 'app.sanitize_data(')
bp_content = bp_content.replace('get_branch_accounts(', 'app.get_branch_accounts(')
bp_content = bp_content.replace('_employees_rows(', 'app._employees_rows(')
bp_content = bp_content.replace('_sync_system_to_registry(', 'app._sync_system_to_registry(')
bp_content = bp_content.replace('_sync_system_to_fleet(', 'app._sync_system_to_fleet(')

with codecs.open('routes/api_fleet.py', 'w', 'utf-8') as f:
    f.write(bp_content)

new_lines = [line for i, line in enumerate(lines) if i not in indices_to_delete]

for i, line in enumerate(new_lines):
    if 'from routes.auth import auth_bp' in line:
        new_lines.insert(i, 'from routes.api_fleet import api_fleet_bp\n')
        new_lines.insert(i+2, 'app.register_blueprint(api_fleet_bp)\n')
        break

with codecs.open('app.py', 'w', 'utf-8') as f:
    f.writelines(new_lines)

print('Fleet API routes extracted.')
