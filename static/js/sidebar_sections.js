(function () {
  'use strict';

  var GROUPS = [
    { key: 'overview', label: 'نظرة عامة', paths: ['/', '/admin', '/fleet_dashboard', '/ops', '/kpis', '/insights'] },
    { key: 'operations', label: 'التشغيل اليومي', paths: ['/schedule', '/schedule/transport', '/m/transport', '/yard', '/tracking', '/handover'] },
    { key: 'people', label: 'الأفراد والمركبات', paths: ['/employees', '/dammam', '/drivers_info', '/driver-vehicle-assignments', '/data-quality', '/alerts', '/documents'] },
    { key: 'maintenance', label: 'الصيانة والمخزون', paths: ['/workshop', '/fuel', '/oils', '/inventory/tires', '/inventory/batteries', '/spare_parts', '/washing'] },
    { key: 'finance', label: 'المالية والسجلات', paths: ['/purchase', '/finance/petty-cash', '/invoice', '/incidents', '/records', '/audit-log'] },
    { key: 'system', label: 'النظام', paths: ['/master_editor', '/system_commands', '/settings', '/logout'] }
  ];
  var STORAGE_KEY = 'bz-sidebar-groups';

  function pathOf(link) {
    try { return new URL(link.getAttribute('href') || '/', location.origin).pathname; } catch (e) { return link.getAttribute('href') || ''; }
  }

  function buildGeneratedGroups(nav) {
    if (nav.querySelector('.bz-nav-group')) return;
    var directLinks = Array.prototype.slice.call(nav.children).filter(function (el) { return el.tagName === 'A'; });
    if (!directLinks.length) return;
    var buckets = GROUPS.map(function (g) { return { meta: g, links: [] }; });
    directLinks.forEach(function (link) {
      var path = pathOf(link);
      var bucket = buckets.find(function (b) { return b.meta.paths.indexOf(path) !== -1; });
      if (bucket) bucket.links.push(link);
    });
    var fragment = document.createDocumentFragment();
    buckets.forEach(function (bucket) {
      if (!bucket.links.length) return;
      var section = document.createElement('section');
      section.className = 'bz-nav-group is-open';
      section.setAttribute('data-nav-group', bucket.meta.key);
      var button = document.createElement('button');
      button.type = 'button'; button.className = 'bz-nav-group-toggle'; button.setAttribute('aria-expanded', 'true');
      button.innerHTML = '<span>' + bucket.meta.label + '</span><span class="group-arrow" aria-hidden="true">⌄</span>';
      var links = document.createElement('div'); links.className = 'bz-nav-group-links';
      bucket.links.forEach(function (link) { links.appendChild(link); });
      section.appendChild(button); section.appendChild(links); fragment.appendChild(section);
    });
    nav.appendChild(fragment);
  }

  function initSidebarSections() {
    var nav = document.querySelector('.bz-sidebar-nav');
    if (!nav) return;
    buildGeneratedGroups(nav);
    var groups = Array.prototype.slice.call(nav.querySelectorAll('.bz-nav-group'));
    var search = document.getElementById('bzSidebarSearch');
    var saved = {};
    try { saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}'); } catch (e) {}

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
      if (button && !button.dataset.bound) {
        button.dataset.bound = '1';
        button.addEventListener('click', function () {
          var open = group.classList.toggle('is-collapsed') === false;
          button.setAttribute('aria-expanded', String(open));
          saved[name] = open;
          try { localStorage.setItem(STORAGE_KEY, JSON.stringify(saved)); } catch (e) {}
        });
      }
    });

    if (search && !search.dataset.bound) {
      search.dataset.bound = '1';
      search.addEventListener('input', function () {
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
          group.style.display = (!query || visible > 0) ? '' : 'none';
          if (query && visible > 0) { group.classList.remove('is-collapsed'); if (button) button.setAttribute('aria-expanded', 'true'); }
          else if (!query && !active && Object.prototype.hasOwnProperty.call(saved, group.getAttribute('data-nav-group'))) {
            var open = saved[group.getAttribute('data-nav-group')];
            group.classList.toggle('is-collapsed', !open);
            if (button) button.setAttribute('aria-expanded', String(open));
          }
        });
      });
    }
  }

  function start() {
    initSidebarSections();
    setTimeout(initSidebarSections, 250);
    setTimeout(initSidebarSections, 1000);
    var nav = document.querySelector('.bz-sidebar-nav');
    if (nav && window.MutationObserver) {
      new MutationObserver(function () { if (!nav.querySelector('.bz-nav-group')) initSidebarSections(); }).observe(nav, { childList: true });
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();
