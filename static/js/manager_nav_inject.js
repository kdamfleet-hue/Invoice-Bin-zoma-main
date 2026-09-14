(function () {
  function inject() {
    var href = '/manager-tasks';
    document.querySelectorAll('.bz-sidebar nav, .bz-sidebar-nav, nav.bz-sidebar-nav').forEach(function (nav) {
      if (nav.querySelector('a[href="' + href + '"]')) return;
      var sch = nav.querySelector('a[href="/schedule"]');
      var a = document.createElement('a');
      a.href = href;
      if (location.pathname === href) a.className = 'active';
      a.innerHTML = '<span class="si">◆</span><span class="slab">مهام المسؤول</span>';
      if (sch && sch.parentNode) sch.parentNode.insertBefore(a, sch.nextSibling);
      else nav.appendChild(a);
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', inject);
  else inject();
  window.addEventListener('load', inject);
  setTimeout(inject, 400);
  setTimeout(inject, 1200);
})();
