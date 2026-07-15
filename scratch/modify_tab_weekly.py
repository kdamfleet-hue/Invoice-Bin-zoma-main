import os

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add Search Input above the table
search_html = '''
          <div style="margin-bottom: 15px; display: flex; gap: 10px;">
            <input type="text" id="tripSearch" class="lux-input" placeholder="🔍 ابحث عن سائق، وجهة، أو حالة..." onkeyup="renderLiveTrips()" style="flex: 1;">
            <button class="lux-btn" onclick="clearTrips()" style="background: var(--fd-red); border-color: var(--fd-red);">🗑️ مسح الكل</button>
          </div>
'''
content = content.replace('<!-- Live Table -->\n          <div class="lux-table-wrap">', '<!-- Live Table -->\n' + search_html + '          <div class="lux-table-wrap">')

# 2. Update JS to use LocalStorage, Search, and Inline Edit
old_js = '''    let liveTrips = [
      { driver: 'أحمد محمد', dest: 'الرياض', date: '2026-07-13', status: 'مجدول' },
      { driver: 'خالد عبدالله', dest: 'جدة', date: '2026-07-12', status: 'في الطريق' }
    ];

    function renderLiveTrips() {
      const tbody = document.getElementById('liveSchedBody');
      if (!tbody) return;
      tbody.innerHTML = liveTrips.map(t => 
        <tr>
          <td style="color:var(--fd-gold2);font-weight:bold;"></td>
          <td></td>
          <td></td>
          <td><span class="status-badge " style=""></span></td>
          <td style="color:var(--fd-muted);font-size:0.7rem;">تحديث الآن ⚡</td>
        </tr>
      ).join('');
    }'''

new_js = '''    let liveTrips = JSON.parse(localStorage.getItem('bz_liveTrips')) || [
      { driver: 'أحمد محمد', dest: 'الرياض', date: '2026-07-13', status: 'مجدول' },
      { driver: 'خالد عبدالله', dest: 'جدة', date: '2026-07-12', status: 'في الطريق' }
    ];
    
    function saveLiveTrips() {
        localStorage.setItem('bz_liveTrips', JSON.stringify(liveTrips));
        updateStats(); // Dynamic counter update if hooked
    }
    
    function clearTrips() {
        if(confirm('هل أنت متأكد من مسح جميع الرحلات؟')) {
            liveTrips = [];
            saveLiveTrips();
            renderLiveTrips();
        }
    }
    
    function deleteTrip(index) {
        liveTrips.splice(index, 1);
        saveLiveTrips();
        renderLiveTrips();
    }
    
    function updateTripField(index, field, value) {
        liveTrips[index][field] = value;
        saveLiveTrips();
    }

    function renderLiveTrips() {
      const tbody = document.getElementById('liveSchedBody');
      const searchInput = document.getElementById('tripSearch');
      if (!tbody) return;
      
      let filterText = searchInput ? searchInput.value.toLowerCase() : '';
      let filteredTrips = liveTrips.map((t, i) => ({...t, originalIndex: i}))
                                   .filter(t => t.driver.toLowerCase().includes(filterText) || 
                                                t.dest.toLowerCase().includes(filterText) || 
                                                t.status.toLowerCase().includes(filterText));
      
      tbody.innerHTML = filteredTrips.map(t => 
        <tr>
          <td contenteditable="true" onblur="updateTripField(, 'driver', this.innerText)" style="color:var(--fd-gold2);font-weight:bold; border-bottom: 1px dashed var(--fd-border);"></td>
          <td contenteditable="true" onblur="updateTripField(, 'dest', this.innerText)" style="border-bottom: 1px dashed var(--fd-border);"></td>
          <td contenteditable="true" onblur="updateTripField(, 'date', this.innerText)" style="border-bottom: 1px dashed var(--fd-border);"></td>
          <td contenteditable="true" onblur="updateTripField(, 'status', this.innerText)" style="border-bottom: 1px dashed var(--fd-border);"><span class="status-badge " style=""></span></td>
          <td style="color:var(--fd-muted);font-size:0.9rem;">
             <button onclick="deleteTrip()" style="background:transparent; border:none; color:var(--fd-red); cursor:pointer;" title="حذف">❌</button>
          </td>
        </tr>
      ).join('');
    }'''

# 3. Update addLiveTrip to save
add_old_js = "liveTrips.unshift({ driver, dest, date, status });"
add_new_js = "liveTrips.unshift({ driver, dest, date, status });\n        saveLiveTrips();"

content = content.replace(old_js, new_js).replace(add_old_js, add_new_js)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Modified index.html successfully")
