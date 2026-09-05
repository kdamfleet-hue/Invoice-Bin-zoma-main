(function () {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const trigger = $('bzNotificationTrigger');
  if (!trigger) return;
  const panel = $('bzNotificationPanel');
  const badge = $('bzNotificationBadge');
  const list = $('bzNotificationList');
  const soundToggle = $('bzSoundToggle');
  const soundStatus = $('bzSoundStatus');
  const markAll = $('bzMarkAllRead');
  let previousIds = new Set();
  let audioContext = null;
  const soundKey = 'bzAlertSoundEnabled';

  function soundEnabled() { return localStorage.getItem(soundKey) === '1'; }
  function updateSoundLabel() {
    const on = soundEnabled();
    soundStatus.textContent = on ? 'الصوت مفعّل' : 'الصوت متوقف';
    soundToggle.textContent = on ? 'إيقاف الصوت' : 'تفعيل الصوت';
  }
  function beep() {
    if (!soundEnabled()) return;
    try {
      audioContext = audioContext || new (window.AudioContext || window.webkitAudioContext)();
      const now = audioContext.currentTime;
      [0, 0.14].forEach((offset, i) => {
        const osc = audioContext.createOscillator();
        const gain = audioContext.createGain();
        osc.type = 'sine'; osc.frequency.value = i ? 660 : 520;
        gain.gain.setValueAtTime(0.0001, now + offset);
        gain.gain.exponentialRampToValueAtTime(0.12, now + offset + 0.02);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + offset + 0.11);
        osc.connect(gain).connect(audioContext.destination);
        osc.start(now + offset); osc.stop(now + offset + 0.12);
      });
    } catch (_) {}
  }
  function escapeHtml(value) {
    return String(value || '').replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));
  }
  function formatTime(value) {
    if (!value) return '';
    const d = new Date(value);
    return Number.isNaN(d.getTime()) ? escapeHtml(value) : d.toLocaleString('ar-SA', {dateStyle:'short', timeStyle:'short'});
  }
  function render(data) {
    const rows = data.rows || [];
    const count = Number(data.unread_count || 0);
    badge.hidden = count < 1; badge.textContent = count > 99 ? '99+' : String(count);
    if (!rows.length) { list.innerHTML = '<div class="bz-notification-empty">لا توجد تنبيهات حالية</div>'; return; }
    list.innerHTML = rows.map((n) => '<div class="bz-notification-item ' + (n.read ? '' : 'unread') + '" data-id="' + escapeHtml(n.id) + '"><strong>' + escapeHtml(n.title) + '</strong><span>' + escapeHtml(n.message) + '</span><small>' + formatTime(n.created_at) + '</small></div>').join('');
  }
  async function load() {
    try {
      const response = await fetch('/api/notifications?limit=40', {headers: {'Accept': 'application/json'}, credentials: 'same-origin'});
      if (!response.ok) return;
      const data = await response.json();
      const ids = new Set((data.rows || []).filter((n) => !n.read).map((n) => String(n.id)));
      const hasNew = [...ids].some((id) => !previousIds.has(id));
      if (previousIds.size && hasNew) beep();
      previousIds = ids; render(data);
    } catch (_) { /* transient network error: retain current UI */ }
  }
  trigger.addEventListener('click', () => {
    const open = panel.classList.toggle('is-open');
    trigger.setAttribute('aria-expanded', String(open));
    if (open) load();
  });
  soundToggle.addEventListener('click', () => {
    const enable = !soundEnabled();
    localStorage.setItem(soundKey, enable ? '1' : '0');
    if (enable) { beep(); }
    updateSoundLabel();
  });
  markAll.addEventListener('click', async () => {
    try {
      await fetch('/api/notifications', {method:'POST', headers:{'Content-Type':'application/json','X-Requested-With':'XMLHttpRequest'}, credentials:'same-origin', body:JSON.stringify({all:true})});
      previousIds = new Set(); await load();
    } catch (_) {}
  });
  updateSoundLabel(); load(); window.setInterval(load, 15000);
})();
