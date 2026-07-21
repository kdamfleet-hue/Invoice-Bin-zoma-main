import re

with open('templates/fleet_dashboard.html', 'r', encoding='utf-8') as f:
    c = f.read()

css_addition = '''
    .table-wrapper {
        width: 100%;
        overflow-x: auto;
        margin-top: 20px;
        background: #1a1a2e;
        border-radius: 8px;
        padding: 10px;
    }
    .btn-edit {
        background: transparent;
        border: none;
        color: #4CAF50;
        cursor: pointer;
        font-size: 1.2rem;
        margin-left: 5px;
    }
'''
if '.table-wrapper {' not in c:
    c = c.replace('.fd-table {', css_addition + '\n    .fd-table {')

if '<div class="table-wrapper">' not in c:
    c = c.replace('<table class="fd-table" id="fleetTable">', '<div class="table-wrapper">\n        <table class="fd-table" id="fleetTable">')
    c = re.sub(r'(<table class="fd-table" id="fleetTable">.*?)</table>', r'\1</table>\n        </div>', c, flags=re.DOTALL)

modal_html = '''
<!-- Edit Modal -->
<div id="editModal" class="modal" style="display:none; position:fixed; top:20%; left:30%; background:#252545; padding:20px; border-radius:10px; z-index:1000; color:white; min-width: 300px; box-shadow: 0 4px 15px rgba(0,0,0,0.5);">
    <h3 style="margin-top:0; border-bottom:1px solid #444; padding-bottom:10px; color:var(--fd-gold)">تعديل حالة السائق</h3>
    <input type="hidden" id="editDriverId">
    <label style="display:block; margin-bottom: 10px;">الحالة:</label>
    <select id="editStatus" style="width:100%; padding: 8px; border-radius: 4px; background: #1a1a2e; color: white; border: 1px solid #444; margin-bottom: 20px;">
        <option value="في الطريق">في الطريق</option>
        <option value="مجدول">مجدول</option>
        <option value="نشط">نشط</option>
    </select>
    <div style="display:flex; justify-content: space-between;">
        <button onclick="saveDriverChanges()" style="background: var(--fd-gold); color: black; border: none; padding: 8px 15px; border-radius: 4px; cursor: pointer; font-weight: bold;">حفظ التغييرات</button>
        <button onclick="closeEditModal()" style="background: #444; color: white; border: none; padding: 8px 15px; border-radius: 4px; cursor: pointer;">إغلاق</button>
    </div>
</div>
'''
if 'id="editModal"' not in c:
    c = c.replace('</body>', modal_html + '\n</body>')

js_code = '''
function openEditModal(driverId) {
    if (typeof currentUser !== 'undefined' && currentUser.role !== 'admin') {
        alert("عذراً، هذه الخاصية للمدراء فقط.");
        return;
    }
    document.getElementById('editDriverId').value = driverId;
    document.getElementById('editModal').style.display = 'block';
}
function closeEditModal() {
    document.getElementById('editModal').style.display = 'none';
}
function saveDriverChanges() {
    const id = document.getElementById('editDriverId').value;
    const status = document.getElementById('editStatus').value;
    fetch('/update-driver', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({id: id, status: status})
    }).then(res => res.json()).then(data => {
        if(data.success) {
            closeEditModal();
            location.reload();
        } else {
            alert(data.error || 'حدث خطأ');
        }
    });
}
'''
if 'function openEditModal' not in c:
    c = c.replace('</script>', js_code + '\n</script>')

if 'openEditModal(' not in c:
    btn_str = '<button class="btn-danger-sm"'
    new_btn = '<button class="btn-edit" onclick="openEditModal(${d.id || i})" title="تعديل">✏️</button>\n          ' + btn_str
    c = c.replace(btn_str, new_btn)

with open('templates/fleet_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(c)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)

print('Frontend updated successfully')
