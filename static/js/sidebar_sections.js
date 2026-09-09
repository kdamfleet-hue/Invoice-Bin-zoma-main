(function () {
  'use strict';

  function initSidebarSections() {
    var nav = document.querySelector('.bz-sidebar-nav');
    if (!nav) return;
    var groups = Array.prototype.slice.call(nav.querySelectorAll('.bz-nav-group'));
    var search = document.getElementById('bzSidebarSearch');
    var key = 'bz-sidebar-groups';
    var saved = {};
    try { saved = JSON.parse(localStorage.getItem(key) || '{}'); } catch (e) { saved = {}; }

    groups.forEach(function (group) {
      var name = group.getAttribute('data-nav-group');
      var button = group.querySelector('.bz-nav-group-toggle');
      var links = Array.prototype.slice.call(group.querySelectorAll('.bz-nav-group-links a'));
      var active = links.some(function (link) { return link.classList.contains('active'); });
      if (active) group.classList.add('has-active');
      if (Object.prototype.hasOwnProperty.call(saved, name) && !active) {
        group.classList.toggle('is-collapsed', !saved[name]);
        if (button) button.setAttribute('aria-expanded', String(saved[name]));
      }
      if (button) button.addEventListener('click', function () {
        var open = group.classList.toggle('is-collapsed') === false;
        button.setAttribute('aria-expanded', String(open));
        saved[name] = open;
        try { localStorage.setItem(key, JSON.stringify(saved)); } catch (e) {}
      });
    });

    if (search) search.addEventListener('input', function () {
      var query = String(search.value || '').trim().toLocaleLowerCase('ar');
      groups.forEach(function (group) {
        var links = Array.prototype.slice.call(group.querySelectorAll('.bz-nav-group-links a'));
        var visible = 0;
        links.forEach(function (link) {
          var match = !query || String(link.textContent || '').toLocaleLowerCase('ar').indexOf(query) !== -1;
          link.style.display = match ? '' : 'none';
          if (match) visible += 1;
        });
        var button = group.querySelector('.bz-nav-group-toggle');
        var active = links.some(function (link) { return link.classList.contains('active'); });
        var show = !query || visible > 0;
        group.style.display = show ? '' : 'none';
        if (query && show) {
          group.classList.remove('is-collapsed');
          if (button) button.setAttribute('aria-expanded', 'true');
        } else if (!query && !active && Object.prototype.hasOwnProperty.call(saved, group.getAttribute('data-nav-group'))) {
          var open = saved[group.getAttribute('data-nav-group')];
          group.classList.toggle('is-collapsed', !open);
          if (button) button.setAttribute('aria-expanded', String(open));
        }
      });
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initSidebarSections);
  else initSidebarSections();
})();
