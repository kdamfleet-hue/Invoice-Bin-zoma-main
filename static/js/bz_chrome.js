(function(){
  if (window.__bzChromeBound) return;
  window.__bzChromeBound = true;
  try {
    const theme = localStorage.getItem('bzTheme') || 'dark';
    document.documentElement.setAttribute('data-theme', theme);
    document.body.classList.toggle('theme-light', theme==='light');
    // base_styles.css's real content palette is driven by .light-mode (app_ux.js's
    // toggleDarkMode), whose only other trigger is a header that is now display:none
    // on every page. Drive it from this one visible control too.
    document.documentElement.classList.toggle('light-mode', theme === 'light');
    document.body.classList.toggle('light-mode', theme === 'light');
    localStorage.setItem('darkMode', theme === 'light' ? 'false' : 'true');
  } catch(e) {}
  const side = document.getElementById('bzSidebar');
  const toggle = document.getElementById('sidebarToggle');
  const overlay = document.getElementById('bzOverlay');
  const pin = document.getElementById('bzPinBtn');
  const themeBtn = document.getElementById('bzThemeBtn');
  const isMobile = function(){ return window.matchMedia('(max-width: 900px)').matches; };
  const isPinned = function(){ try { return localStorage.getItem('bzSidebarPinned') === '1'; } catch(e){ return false; } };
  function applyPin(){
    document.body.classList.toggle('sidebar-pinned', isPinned() && !isMobile());
    if (pin) pin.classList.toggle('on', isPinned());
  }
  function closeSide(){
    if (!side) return;
    side.classList.add('collapsed');
    document.body.classList.remove('sidebar-is-open');
  }
  function openSide(){
    if (!side) return;
    side.classList.remove('collapsed');
    if (isMobile()) document.body.classList.add('sidebar-is-open');
    else document.body.classList.remove('sidebar-is-open');
  }
  function layout(){
    if (!side) return;
    if (isMobile()) {
      side.classList.remove('rail');
      if (!side.dataset.userToggled) closeSide();
    } else {
      side.classList.add('rail');
      document.body.classList.remove('sidebar-is-open');
      if (!side.dataset.userToggled) {
        if (isPinned()) openSide();
        else { side.classList.remove('collapsed'); }
      }
    }
    applyPin();
  }
  layout();
  let lastMobile = isMobile();
  window.addEventListener('resize', function(){
    const now = isMobile();
    if (now !== lastMobile) { side && (side.dataset.userToggled = ''); lastMobile = now; layout(); }
  });
  if (toggle && side) {
    toggle.addEventListener('click', function(e){
      e.preventDefault();
      e.stopPropagation();
      if (e.stopImmediatePropagation) e.stopImmediatePropagation();
      side.dataset.userToggled = '1';
      if (side.classList.contains('collapsed')) openSide(); else closeSide();
    }, true);
  }
  if (overlay) overlay.addEventListener('click', closeSide);
  if (side) side.querySelectorAll('a[href]').forEach(function(a){
    a.addEventListener('click', function(){ if (isMobile()) closeSide(); });
  });
  if (pin) pin.addEventListener('click', function(e){
    e.preventDefault(); e.stopPropagation();
    try { localStorage.setItem('bzSidebarPinned', isPinned() ? '0' : '1'); } catch(err){}
    if (!isMobile()) { side.dataset.userToggled = ''; openSide(); }
    applyPin();
  });
  if (themeBtn) {
    const syncIcon = function(){
      const light = document.documentElement.getAttribute('data-theme')==='light';
      themeBtn.textContent = light ? '☀' : '☾';
    };
    syncIcon();
    themeBtn.addEventListener('click', function(){
      const next = document.documentElement.getAttribute('data-theme')==='light' ? 'dark' : 'light';
      document.documentElement.setAttribute('data-theme', next);
      document.body.classList.toggle('theme-light', next==='light');
      document.documentElement.classList.toggle('light-mode', next === 'light');
      document.body.classList.toggle('light-mode', next === 'light');
      try { localStorage.setItem('bzTheme', next); localStorage.setItem('darkMode', next === 'light' ? 'false' : 'true'); } catch(e){}
      syncIcon();
    });
  }
})();
