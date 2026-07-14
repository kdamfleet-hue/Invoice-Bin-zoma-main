import re

with open('app.py', 'r', encoding='utf-8') as f:
    app_py = f.read()

new_export = """@app.route("/api/export_schedule_exact", methods=["POST"])
@login_required
def export_schedule_exact():
    try:
        data = request.json or {}
        template_path = os.path.join(app.root_path, "weekly_schedule_template.xlsx")
        
        if not os.path.exists(template_path):
            return jsonify({"success": False, "error": "قالب التصدير غير موجود"}), 500

        wb = openpyxl.load_workbook(template_path)
        
        def safe_set(sheet, row, col, val):
            cell = sheet.cell(row=row, column=col)
            try:
                cell.value = val
            except AttributeError:
                pass # Merged cell

        # --- Active Vehicles (المركبات النشطة) ---
        ws_main = wb["المركبات النشطة"]
        main_data = data.get("main", [])
        for idx, rd in enumerate(main_data):
            r = 5 + idx
            safe_set(ws_main, r, 1, idx + 1)
            safe_set(ws_main, r, 2, rd.get("empid", ""))
            safe_set(ws_main, r, 3, rd.get("name", ""))
            safe_set(ws_main, r, 4, rd.get("iqama", ""))
            safe_set(ws_main, r, 5, rd.get("job", ""))
            safe_set(ws_main, r, 6, rd.get("plate", ""))
            safe_set(ws_main, r, 7, rd.get("model", ""))
            safe_set(ws_main, r, 8, rd.get("vtype", ""))
            safe_set(ws_main, r, 9, rd.get("pallets", ""))
            safe_set(ws_main, r, 10, rd.get("load", ""))
            safe_set(ws_main, r, 11, rd.get("vserial", ""))
            safe_set(ws_main, r, 12, rd.get("inspect", ""))
            # Col 13 is formula (rem_days1)
            safe_set(ws_main, r, 14, rd.get("license", ""))
            # Col 15 is formula (rem_days2)
            safe_set(ws_main, r, 16, rd.get("drivercard", ""))
            # Col 17 is formula (rem_days3)
            safe_set(ws_main, r, 18, rd.get("opcard", ""))
            # Col 19 is formula (rem_days4)
            safe_set(ws_main, r, 20, rd.get("empNotes", ""))
            safe_set(ws_main, r, 21, rd.get("phone", ""))

        # --- Spare and Broken (الأسبير والمعطلة) ---
        if "الأسبير والمعطلة" in wb.sheetnames:
            ws_spare = wb["الأسبير والمعطلة"]
            spare_data = data.get("spare", [])
            for idx, rd in enumerate(spare_data):
                r = 4 + idx
                safe_set(ws_spare, r, 1, idx + 1)
                safe_set(ws_spare, r, 2, rd.get("status", "اسبير"))
                safe_set(ws_spare, r, 3, rd.get("plate", ""))
                safe_set(ws_spare, r, 4, rd.get("model", ""))
                safe_set(ws_spare, r, 5, rd.get("vtype", ""))
                safe_set(ws_spare, r, 6, rd.get("pallets", ""))
                safe_set(ws_spare, r, 7, rd.get("load", ""))
                safe_set(ws_spare, r, 8, rd.get("vserial", ""))
                safe_set(ws_spare, r, 9, rd.get("inspect", ""))
                # Col 10 is the formula for remaining days
                safe_set(ws_spare, r, 11, rd.get("license", ""))
                # Col 12 is the formula for remaining days
                safe_set(ws_spare, r, 13, rd.get("opcard", ""))
                # Col 14 is the formula for remaining days
                safe_set(ws_spare, r, 15, rd.get("empNotes", ""))

        # --- Vacation (السائقون في إجازة) ---
        if "السائقون في إجازة" in wb.sheetnames:
            ws_vac = wb["السائقون في إجازة"]
            vac_data = data.get("vacation", [])
            for idx, rd in enumerate(vac_data):
                r = 4 + idx
                safe_set(ws_vac, r, 1, idx + 1)
                safe_set(ws_vac, r, 2, rd.get("empid", ""))
                safe_set(ws_vac, r, 3, rd.get("name", ""))
                safe_set(ws_vac, r, 4, rd.get("iqama", ""))
                safe_set(ws_vac, r, 5, rd.get("job", ""))
                safe_set(ws_vac, r, 6, rd.get("drivercard", ""))
                # Col 7 is the formula
                safe_set(ws_vac, r, 8, rd.get("phone", ""))
                safe_set(ws_vac, r, 9, rd.get("empNotes", ""))

        import io, base64
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        b64 = base64.b64encode(output.read()).decode("utf-8")
        return jsonify({"success": True, "file_b64": b64})
    except Exception as e:
        import traceback
        logger.exception("export_schedule_exact error")
        return jsonify({"success": False, "error": str(e)}), 500"""

app_py = re.sub(
    r'@app\.route\("/api/export_schedule_exact", methods=\["POST"\]\).*?def export_schedule_exact\(\):.*?return jsonify\(\{"success": False, "error": str\(e\)\}\), 500',
    new_export.strip(),
    app_py,
    flags=re.DOTALL
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_py)

print("Updated export_schedule_exact columns in app.py")
