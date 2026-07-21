import re

# 1. Update app.py
app_path = "app.py"
with open(app_path, "r", encoding="utf-8") as f:
    app_content = f.read()

excel_sync_code = """
@app.route("/api/sync_excel", methods=["POST"])
@login_required
def api_sync_excel():
    try:
        import pandas as pd
        df = pd.read_excel('DB-WORK/dammam_employees_data.xlsx', header=[0, 1])
        df.columns = [f"{c[0]}_{c[1]}" if 'Unnamed' not in str(c[0]) else str(c[1]) for c in df.columns]
        
        updated_count = 0
        with db_connection() as conn:
            c = conn.cursor()
            for index, row in df.iterrows():
                empid = None
                name = None
                iqama = None
                for col in df.columns:
                    if 'الرقم الوظيفي' in str(col): empid = str(row[col]).strip()
                    if 'اسم العامل' in str(col) or 'الاسم' in str(col): name = str(row[col]).strip()
                    if 'الإقامة' in str(col) or 'البطاقة' in str(col): iqama = str(row[col]).strip()
                
                if not name or str(name) == 'nan':
                    continue
                
                if str(empid) == 'nan': empid = None
                if str(iqama) == 'nan': iqama = None

                c.execute("SELECT id FROM drivers WHERE name=? OR empid=?", (name, empid))
                res = c.fetchone()
                if res:
                    driver_id = res['id']
                    if iqama:
                        c.execute("UPDATE drivers SET iqama=? WHERE id=?", (iqama, driver_id))
                    updated_count += 1
                else:
                    c.execute("INSERT INTO drivers (name, empid, iqama) VALUES (?, ?, ?)", (name, empid, iqama))
                    updated_count += 1
            conn.commit()
            
        return jsonify({"success": True, "message": "تم تحديث البيانات من ملف الإكسيل بنجاح", "updated_count": updated_count})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/fleet_data")
"""

app_content = app_content.replace('@app.route("/api/fleet_data")', excel_sync_code)

with open(app_path, "w", encoding="utf-8") as f:
    f.write(app_content)


# 2. Update templates/fleet_dashboard.html
dashboard_path = "templates/fleet_dashboard.html"
with open(dashboard_path, "r", encoding="utf-8") as f:
    dash_content = f.read()

rbac_js = """
    // ── RBAC System ──────────────────────────────────────────────────
    const currentUser = {
        name: "مسؤول النظام",
        role: "admin" // admin or viewer
    };

    function canEdit() {
        if (currentUser.role !== 'admin') {
            alert("تنبيه: لا تملك صلاحية التعديل. يرجى مراجعة مدير النظام.");
            return false;
        }
        return true;
    }

    // ── Load fleet data ──────────────────────────────────────────────
"""

dash_content = dash_content.replace('// ── Load fleet data ──────────────────────────────────────────────', rbac_js)

dash_content = dash_content.replace('async function deleteDriver(id, name) {', 'async function deleteDriver(id, name) {\n      if (!canEdit()) return;')
dash_content = dash_content.replace('function addLiveTrip(e) {', 'function addLiveTrip(e) {\n      if (!canEdit()) return;')

role_selector = """
      <select id="roleSelector" onchange="currentUser.role = this.value; if(window.showToast) showToast('تم التبديل إلى ' + this.value, 'info')" style="background: var(--fd-surface2); color: var(--fd-gold); border: 1px solid var(--fd-border); border-radius: 8px; padding: 5px; margin-left: 10px;">
        <option value="admin">مدير (Admin)</option>
        <option value="viewer">مشاهد (Viewer)</option>
      </select>
"""
dash_content = dash_content.replace('<div class="bz-actions">', '<div class="bz-actions">' + role_selector)

sync_btn = """
        <button class="btn-sync" onclick="syncExcelDammam()" id="syncExcelBtn">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="12" y1="18" x2="12" y2="12"/><polyline points="9 15 12 18 15 15"/></svg>
          مزامنة إكسيل الدمام
        </button>
        <button class="btn-sync" onclick="openSyncModal()" id="syncBtn">
"""
dash_content = dash_content.replace('<button class="btn-sync" onclick="openSyncModal()" id="syncBtn">', sync_btn)

sync_js = """
    // ── Sync Excel Dammam ─────────────────────────────────────────────
    async function syncExcelDammam() {
        if (!canEdit()) return;
        const btn = document.getElementById('syncExcelBtn');
        btn.innerHTML = '⏳ جارٍ المزامنة...';
        btn.disabled = true;
        try {
            const r = await fetch('/api/sync_excel', { method: 'POST' });
            const j = await r.json();
            if (j.success) {
                if (window.showToast) showToast(`تم التحديث بنجاح: ${j.updated_count} سجل`, 'success');
                await init();
            } else {
                if (window.showToast) showToast(j.error || 'خطأ في المزامنة', 'error');
            }
        } catch(e) {
            if (window.showToast) showToast('خطأ في الاتصال بالخادم', 'error');
        }
        btn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="12" y1="18" x2="12" y2="12"/><polyline points="9 15 12 18 15 15"/></svg> مزامنة إكسيل الدمام`;
        btn.disabled = false;
    }

    // ── Smart Sync Modal ─────────────────────────────────────────────
"""
dash_content = dash_content.replace('// ── Smart Sync Modal ─────────────────────────────────────────────', sync_js)

with open(dashboard_path, "w", encoding="utf-8") as f:
    f.write(dash_content)

# Update root index.html as well
with open("index.html", "w", encoding="utf-8") as f:
    f.write(dash_content)

print("Modifications for RBAC and Excel Sync complete.")
