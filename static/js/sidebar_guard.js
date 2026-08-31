/* UI-only. Neutralize leftover sidebar controllers. No data changes. */
(function () {
  function clean() {
    document.querySelectorAll('button.bz-sidebar-toggle:not(#sidebarToggle)').forEach(function (btn) {
      try { btn.remove(); } catch (e) {}
    });
    var backdrop = document.querySelector('.bz-side-backdrop');
    if (backdrop) backdrop.remove();
    document.body.classList.remove('bz-drawer-open');
    var topbar = document.querySelector('header.bz-topbar');
    if (topbar) topbar.classList.remove('sidebar-open');
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', clean);
  } else {
    clean();
  }
  window.addEventListener('load', clean);
})();
