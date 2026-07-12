import re

file_path = "templates/fleet_dashboard.html"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add CSS for Bell, Notifications and Weekly Schedule
css_addition = """
    /* ── Notifications & Bell ── */
    .fd-bell-wrap {
      position: relative;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      margin-left: 10px;
    }
    .fd-bell-icon {
      color: var(--fd-gold);
      transition: transform 0.2s;
    }
    .fd-bell-wrap:hover .fd-bell-icon {
      transform: scale(1.1) rotate(5deg);
    }
    .fd-bell-badge {
      position: absolute;
      top: -4px;
      right: -6px;
      background: var(--fd-red);
      color: white;
      font-size: 0.65rem;
      font-weight: bold;
      padding: 2px 5px;
      border-radius: 10px;
      line-height: 1;
      border: 2px solid var(--fd-bg);
    }
    .fd-notifications {
      position: absolute;
      top: 100%;
      left: 0;
      margin-top: 10px;
      width: 320px;
      background: var(--fd-surface);
      border: 1px solid var(--fd-border);
      border-radius: 12px;
      box-shadow: 0 10px 40px rgba(0,0,0,0.6);
      display: none;
      flex-direction: column;
      z-index: 1000;
      overflow: hidden;
    }
    .fd-bell-wrap:hover .fd-notifications {
      display: flex;
    }
    .fd-noti-header {
      background: var(--fd-surface2);
      padding: 12px 16px;
      border-bottom: 1px solid var(--fd-border);
      font-weight: bold;
      color: var(--fd-gold2);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .fd-noti-body {
      max-height: 300px;
      overflow-y: auto;
      padding: 0;
      margin: 0;
      list-style: none;
    }
    .fd-noti-item {
      padding: 12px 16px;
      border-bottom: 1px solid var(--fd-border);
      font-size: 0.8rem;
      display: flex;
      align-items: flex-start;
      gap: 10px;
      transition: background 0.2s;
    }
    .fd-noti-item:hover {
      background: rgba(197, 160, 89, 0.05);
    }
    .fd-noti-item.urgent { border-right: 3px solid var(--fd-red); }
    .fd-noti-item.warn { border-right: 3px solid var(--fd-orange); }
    
    /* ── Weekly Schedule Luxurious Tab ── */
    .lux-sched-container {
      display: grid;
      grid-template-columns: 300px 1fr;
      gap: 20px;
      padding: 24px 28px;
    }
    .lux-form-card {
      background: linear-gradient(145deg, var(--fd-surface), #1a1c22);
      border: 1px solid var(--fd-border);
      border-radius: 16px;
      padding: 24px;
      box-shadow: inset 0 0 20px rgba(0,0,0,0.2), 0 8px 24px rgba(0,0,0,0.4);
    }
    .lux-form-card h3 {
      color: var(--fd-gold2);
      margin-top: 0;
      font-size: 1.1rem;
      margin-bottom: 20px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .lux-input {
      width: 100%;
      background: var(--fd-surface2);
      border: 1px solid var(--fd-border);
      color: var(--fd-text);
      padding: 10px 14px;
      border-radius: 8px;
      margin-bottom: 14px;
      font-family: 'Tajawal', sans-serif;
      transition: border-color 0.3s;
      box-sizing: border-box;
    }
    .lux-input:focus { border-color: var(--fd-gold); outline: none; }
    
    .lux-table-wrap {
      background: var(--fd-surface);
      border: 1px solid var(--fd-border);
      border-radius: 16px;
      overflow: hidden;
      box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .lux-table { width: 100%; border-collapse: collapse; }
    .lux-table th {
      background: linear-gradient(90deg, #111318, #1a1c22);
      color: var(--fd-gold);
      padding: 14px 16px;
      text-align: right;
      font-weight: 800;
      border-bottom: 2px solid var(--fd-gold);
    }
    .lux-table td {
      padding: 14px 16px;
      border-bottom: 1px solid var(--fd-border);
      font-size: 0.85rem;
    }
    .lux-table tr:hover { background: rgba(197, 160, 89, 0.08); }
    .status-badge {
      padding: 4px 10px;
      border-radius: 20px;
      font-size: 0.7rem;
      font-weight: 700;
    }
    .status-live { background: rgba(34,197,94,0.15); color: #22c55e; border: 1px solid #22c55e; }
"""
content = content.replace("</style>", css_addition + "\n  </style>")

# 2. Add Audio element and Bell icon to header
audio_html = """
  <!-- Alert Sound -->
  <audio id="alertSound" src="https://assets.mixkit.co/sfx/preview/mixkit-software-interface-back-2575.mp3" preload="auto"></audio>
"""
content = content.replace("<body>", "<body>\n" + audio_html)

bell_html = """
      <div class="fd-bell-wrap">
        <svg class="fd-bell-icon" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
          <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
        </svg>
        <span class="fd-bell-badge" id="bellBadge">0</span>
        <div class="fd-notifications">
          <div class="fd-noti-header">
            تنبيهات ذكية <span style="font-size:0.7rem;color:var(--fd-muted)" id="liveStatus">🟢 متصل</span>
          </div>
          <ul class="fd-noti-body" id="notiBody">
            <li class="fd-noti-item"><div style="color:var(--fd-muted)">لا توجد تنبيهات حالياً</div></li>
          </ul>
        </div>
      </div>
"""
content = content.replace('<div class="bz-actions">', '<div class="bz-actions">\n' + bell_html)

# 3. Add Tab Button
tab_button = """
      <button class="fd-tab" onclick="switchFdTab('tab-weekly', this)" id="btn-tab-weekly">
        📅 الجدول الأسبوعي (حي)
      </button>
"""
content = content.replace('</div>\n\n    <!-- ══════════════════════════ TAB: DASHBOARD ══════════════════════════ -->', tab_button + '    </div>\n\n    <!-- ══════════════════════════ TAB: DASHBOARD ══════════════════════════ -->')

# 4. Add Weekly Schedule Panel
weekly_panel = """
    <!-- ══════════════════════════ TAB: WEEKLY SCHEDULE ══════════════════════════ -->
    <div id="tab-weekly" class="fd-tab-panel">
      <div class="lux-sched-container">
        <!-- Input Form -->
        <div class="lux-form-card">
          <h3>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
            إضافة رحلة / مهمة جديدة
          </h3>
          <form id="tripForm" onsubmit="addLiveTrip(event)">
            <input type="text" id="tripDriver" class="lux-input" placeholder="اسم السائق" required>
            <input type="text" id="tripDest" class="lux-input" placeholder="الوجهة (مثال: الرياض)" required>
            <input type="date" id="tripDate" class="lux-input" required>
            <select id="tripStatus" class="lux-input">
              <option value="مجدول">مجدول</option>
              <option value="في الطريق">في الطريق</option>
              <option value="مكتمل">مكتمل</option>
            </select>
            <button type="submit" class="btn-primary" style="width:100%;justify-content:center;margin-top:10px;">إضافة للجدول الحي</button>
          </form>
        </div>
        
        <!-- Live Table -->
        <div class="lux-table-wrap">
          <table class="lux-table" id="liveSchedTable">
            <thead>
              <tr>
                <th>السائق</th>
                <th>الوجهة</th>
                <th>التاريخ</th>
                <th>الحالة</th>
                <th>تحديث حي</th>
              </tr>
            </thead>
            <tbody id="liveSchedBody">
              <!-- Populated by JS -->
            </tbody>
          </table>
        </div>
      </div>
    </div>
"""
content = content.replace('</div><!-- /tab-fleet -->', '</div><!-- /tab-fleet -->\n' + weekly_panel)

# 5. Modify JS for Live Updates and Alerts
js_mod = """
    // ── Live Updates & Smart Alerts ────────────────────────────────
    let lastAlertsCount = 0;
    let liveTrips = [
      { driver: 'أحمد محمد', dest: 'الرياض', date: '2026-07-13', status: 'مجدول' },
      { driver: 'خالد عبدالله', dest: 'جدة', date: '2026-07-12', status: 'في الطريق' }
    ];

    function renderLiveTrips() {
      const tbody = document.getElementById('liveSchedBody');
      if (!tbody) return;
      tbody.innerHTML = liveTrips.map(t => `
        <tr>
          <td style="color:var(--fd-gold2);font-weight:bold;">${t.driver}</td>
          <td>${t.dest}</td>
          <td>${t.date}</td>
          <td><span class="status-badge ${t.status === 'في الطريق' ? 'status-live' : ''}" style="${t.status === 'مكتمل' ? 'background:rgba(255,255,255,0.1);border:1px solid #666;' : (t.status === 'مجدول' ? 'background:rgba(249,115,22,0.15);color:#f97316;border:1px solid #f97316;' : '')}">${t.status}</span></td>
          <td style="color:var(--fd-muted);font-size:0.7rem;">تحديث الآن ⚡</td>
        </tr>
      `).join('');
    }

    function addLiveTrip(e) {
      e.preventDefault();
      const driver = document.getElementById('tripDriver').value;
      const dest = document.getElementById('tripDest').value;
      const date = document.getElementById('tripDate').value;
      const status = document.getElementById('tripStatus').value;
      liveTrips.unshift({ driver, dest, date, status });
      renderLiveTrips();
      e.target.reset();
      if(window.showToast) showToast('تمت الإضافة للجدول الحي بنجاح', 'success');
      
      // Trigger a smart alert for the new trip
      triggerSmartAlert('تمت إضافة رحلة جديدة للسائق ' + driver, 'info');
    }

    function triggerSmartAlert(msg, type) {
      const notiBody = document.getElementById('notiBody');
      const li = document.createElement('li');
      li.className = `fd-noti-item ${type === 'urgent' ? 'urgent' : 'warn'}`;
      li.innerHTML = `<div><strong>${type === 'urgent' ? 'عاجل' : 'تنبيه'}:</strong> ${msg}</div>`;
      notiBody.prepend(li);
      
      let count = parseInt(document.getElementById('bellBadge').textContent) || 0;
      count++;
      document.getElementById('bellBadge').textContent = count;
      
      // Play sound
      const audio = document.getElementById('alertSound');
      if(audio) {
         audio.play().catch(e => console.log("Audio play blocked by browser:", e));
      }
    }

    // Replace the end of updateStats to handle smart alerts logic properly
    const origUpdateStats = updateStats;
    updateStats = function() {
      origUpdateStats();
      
      // Build Smart Alerts
      const notiBody = document.getElementById('notiBody');
      let alertsHTML = '';
      let alertCount = 0;
      
      // 1. Expiring Docs Alerts
      const expiringList = allDrivers.reduce((acc, d) => {
        ['drivercard', 'inspect', 'license', 'opcard'].forEach(f => {
          const dd = dateDiff(d[f]);
          if (dd !== null && dd <= 30) {
             acc.push({ name: d.name, doc: f, days: dd });
          }
        });
        return acc;
      }, []);
      
      expiringList.slice(0, 5).forEach(e => {
        const isUrgent = e.days < 0;
        alertsHTML += `<li class="fd-noti-item ${isUrgent ? 'urgent' : 'warn'}">
          <div><strong>${isUrgent ? '🚨 وثيقة منتهية' : '⚠️ وثيقة قاربت على الانتهاء'}</strong><br>
          <span style="color:var(--fd-muted)">${e.name} - وثيقة (${e.doc}) ${isUrgent ? 'منتهية' : `متبقي ${e.days} يوم`}</span></div>
        </li>`;
        alertCount++;
      });
      
      // 2. Mock Maintenance Alert (Randomly appears)
      if (Math.random() > 0.8) {
         alertsHTML += `<li class="fd-noti-item urgent">
          <div><strong>🔧 تنبيه صيانة عاجل</strong><br>
          <span style="color:var(--fd-muted)">المركبة تحتاج صيانة دورية فورية</span></div>
        </li>`;
         alertCount++;
      }
      
      if (alertsHTML) {
         notiBody.innerHTML = alertsHTML;
      } else {
         notiBody.innerHTML = '<li class="fd-noti-item"><div style="color:var(--fd-muted)">لا توجد تنبيهات حالياً</div></li>';
      }
      
      document.getElementById('bellBadge').textContent = alertCount;
      
      if (alertCount > lastAlertsCount) {
         const audio = document.getElementById('alertSound');
         if(audio) audio.play().catch(e=>console.log(e));
         if(window.showToast) showToast('تنبيهات ذكية جديدة!', 'warning');
      }
      lastAlertsCount = alertCount;
    };

    // Live Data Polling (every 5 seconds)
    setInterval(async () => {
      // Simulate live update by re-fetching fleet and updating UI seamlessly
      document.getElementById('liveStatus').textContent = '⚡ يتحدث...';
      try {
          await loadFleet();
          filterTable(document.getElementById('fdSearch') ? document.getElementById('fdSearch').value : '');
          updateStats();
          setTimeout(() => document.getElementById('liveStatus').textContent = '🟢 متصل', 1000);
      } catch(e) {
          document.getElementById('liveStatus').textContent = '🔴 غير متصل';
      }
    }, 5000);

"""

content = content.replace("document.addEventListener('DOMContentLoaded', init);", js_mod + "\n    document.addEventListener('DOMContentLoaded', () => { init(); renderLiveTrips(); });")

with open("templates/fleet_dashboard.html", "w", encoding="utf-8") as f:
    f.write(content)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)

print("Modifications complete.")
