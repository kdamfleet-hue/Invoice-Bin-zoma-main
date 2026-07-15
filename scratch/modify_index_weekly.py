import os

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add the new tab button
tab_btn = '''      <button class="fd-tab" onclick="switchFdTab('tab-weekly-update', this)" id="btn-tab-weekly-update">
        📝 بيانات التحديث الأسبوعي
      </button>'''
content = content.replace("📅 الجدول الأسبوعي (حي)\n        </button>", "📅 الجدول الأسبوعي (حي)\n        </button>\n" + tab_btn)

# 2. Add the new tab panel
tab_panel = '''
    <!-- ══════════════════════════ TAB: WEEKLY UPDATE ══════════════════════════ -->
    <div id="tab-weekly-update" class="fd-tab-panel">
      <div class="lux-sched-container">
        <div class="fd-header">
          <div class="fd-header-title">
            <div class="fd-header-icon">📝</div>
            <div>
              <h1>بيانات التحديث الأسبوعي</h1>
              <span>مزامنة مباشرة مع ملف الإكسل</span>
            </div>
          </div>
          <div class="fd-toolbar">
            <button class="lux-btn" onclick="saveWeeklyUpdate()">حفظ التعديلات</button>
          </div>
        </div>
        <div style="padding: 20px;">
          <select id="weeklySheetSelector" class="lux-input" style="max-width: 250px; margin-bottom: 20px; padding: 10px; border-radius: 5px; background: var(--fd-surface2); color: white; border: 1px solid var(--fd-border);" onchange="renderWeeklySheet()">
            <option value="">جاري التحميل...</option>
          </select>
          <div style="overflow-x: auto; max-height: 70vh;">
            <table class="fd-table" id="weeklyUpdateTable">
                <thead id="weeklyUpdateHead"></thead>
                <tbody id="weeklyUpdateBody"></tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
'''

content = content.replace("<!-- ══════════════════════════ MODALS ══════════════════════════ -->", tab_panel + "\n    <!-- ══════════════════════════ MODALS ══════════════════════════ -->")

# 3. Add JS for it
js_code = '''
let weeklyUpdateData = {};

async function loadWeeklyUpdate() {
    try {
        const res = await fetch('/api/weekly_update');
        const data = await res.json();
        if (data.success) {
            weeklyUpdateData = data.data;
            const selector = document.getElementById('weeklySheetSelector');
            selector.innerHTML = '';
            data.sheets.forEach(sheet => {
                const opt = document.createElement('option');
                opt.value = sheet;
                opt.textContent = sheet;
                selector.appendChild(opt);
            });
            if (data.sheets.length > 0) {
                renderWeeklySheet();
            }
        } else {
            alert('خطأ في تحميل البيانات: ' + data.error);
        }
    } catch (e) {
        console.error(e);
    }
}

function renderWeeklySheet() {
    const sheetName = document.getElementById('weeklySheetSelector').value;
    const sheetData = weeklyUpdateData[sheetName];
    if (!sheetData) return;
    
    const thead = document.getElementById('weeklyUpdateHead');
    const tbody = document.getElementById('weeklyUpdateBody');
    thead.innerHTML = '';
    tbody.innerHTML = '';
    
    if (sheetData.length === 0) return;
    
    sheetData.forEach((row, rowIndex) => {
        const tr = document.createElement('tr');
        row.forEach((cell, colIndex) => {
            const el = document.createElement(rowIndex === 0 || rowIndex === 1 ? 'th' : 'td');
            el.textContent = cell !== null && cell !== undefined ? cell : "";
            el.contentEditable = true;
            el.style.border = '1px solid var(--fd-border)';
            el.style.padding = '8px';
            el.style.minWidth = '100px';
            if (rowIndex === 0 || rowIndex === 1) {
                el.style.background = '#1a1a1a';
                el.style.color = 'var(--fd-gold)';
            }
            el.onblur = (e) => {
                weeklyUpdateData[sheetName][rowIndex][colIndex] = e.target.textContent;
            };
            tr.appendChild(el);
        });
        if (rowIndex === 0 || rowIndex === 1) {
            thead.appendChild(tr);
        } else {
            tbody.appendChild(tr);
        }
    });
}

async function saveWeeklyUpdate() {
    const btn = event.target;
    btn.textContent = 'جاري الحفظ...';
    try {
        const res = await fetch('/api/weekly_update', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({data: weeklyUpdateData})
        });
        const data = await res.json();
        if (data.success) {
            alert('تم حفظ التعديلات في ملف الإكسل بنجاح!');
        } else {
            alert('خطأ في الحفظ: ' + data.error);
        }
    } catch (e) {
        console.error(e);
        alert('حدث خطأ في الاتصال بالخادم');
    }
    btn.textContent = 'حفظ التعديلات';
}

document.addEventListener('DOMContentLoaded', () => {
    loadWeeklyUpdate();
});
'''

content = content.replace("</body>", f"<script>{js_code}</script>\n</body>")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Modified index.html successfully")
