(function () {
  'use strict';

  var GROUPS = [
    { key: 'overview', label: 'الرئيسية', paths: ['/', '/admin', '/fleet_dashboard', '/ops', '/kpis', '/insights'] },
    { key: 'operations', label: 'التشغيل', paths: ['/schedule', '/schedule/transport', '/m/transport', '/yard', '/tracking', '/handover'] },
    { key: 'people', label: 'المركبات والأفراد', paths: ['/employees', '/dammam', '/drivers_info', '/driver-vehicle-assignments', '/data-quality', '/alerts', '/documents'] },
    { key: 'maintenance', label: 'الصيانة والمخزون', paths: ['/workshop', '/fuel', '/oils', '/inventory/tires', '/inventory/batteries', '/spare_parts', '/washing'] },
    { key: 'finance', label: 'المالية والسجلات', paths: ['/purchase', '/finance/petty-cash', '/invoice', '/incidents', '/records', '/audit-log'] },
    { key: 'system', label: 'النظام', paths: ['/master_editor', '/system_commands', '/settings', '/branches', '/overview', '/logout'] }
  ];
  var STORAGE_KEY = 'bz-sidebar-groups-v2';

  function pathOf(link) {
    try { return new URL(link.getAttribute('href') || '/', location.origin).pathname; } catch (e) { return link.getAttribute('href') || ''; }
  }

  var FALLBACK_GROUPS = [
    { key: 'overview', label: 'الرئيسية', links: [['👑','مركز القرار','/admin'], ['📊','لوحة الأسطول','/fleet_dashboard'], ['📈','مؤشرات الأداء','/kpis'], ['🧠','التحليلات','/insights']] },
    { key: 'operations', label: 'التشغيل', links: [['📋','الجدول الأسبوعي','/schedule'], ['🚚','نقل عام وخاص','/schedule/transport'], ['📱','تطبيق النقل','/m/transport'], ['🅿️','إدارة الساحات','/yard'], ['🛰️','التتبع الحي','/tracking'], ['🔑','تسليم واستلام','/handover']] },
    { key: 'people', label: 'المركبات والأفراد', links: [['🚗','مركبات الدمام','/dammam'], ['🚛','سائقو النقل','/drivers_info'], ['🔗','ربط السائق بالمركبة','/driver-vehicle-assignments'], ['✓','جودة البيانات','/data-quality'], ['🔔','تنبيهات الوثائق','/alerts'], ['📂','الوثائق','/documents']] },
    { key: 'maintenance', label: 'الصيانة والمخزون', links: [['🔧','الورشة','/workshop'], ['⛽','المحروقات','/fuel'], ['📜','الزيوت والفلاتر','/oils'], ['💿','الإطارات','/inventory/tires'], ['🔋','البطاريات','/inventory/batteries'], ['📦','قطع الغيار','/spare_parts'], ['🚿','الغسيل','/washing']] },
    { key: 'finance', label: 'المالية والسجلات', links: [['🛒','المشتريات','/purchase'], ['💵','العهد','/finance/petty-cash'], ['🧾','الفواتير','/invoice'], ['🚨','الحوادث','/incidents'], ['📁','السجلات','/records'], ['🛡','سجل التدقيق','/audit-log']] },
    { key: 'system', label: 'النظام', links: [['⚙️','الإعدادات','/settings'], ['🏢','مركز الفروع','/branches'], ['⚡','أوامر النظام','/system_commands'], ['↪','تسجيل الخروج','/logout']] }
  ];

  function makeFallbackLink(icon, label, href) {
    var link = document.createElement('a');
    link.href = href;
    link.innerHTML = '<span class="si" aria-hidden="true">' + icon + '</span><span class="slab">' + label + '</span>';
    if (location.pathname === href || (href === '/purchase' && location.pathname.indexOf('/purchase') === 0)) {
      link.className = 'active';
    }
    return link;
  }

  function ensureFallbackGroups(nav) {
    var existing = {};
    Array.prototype.slice.call(nav.querySelectorAll('a[href]')).forEach(function (link) { existing[pathOf(link)] = true; });
    var hasFullMenu = nav.querySelectorAll('.bz-nav-group').length >= 4;
    if (hasFullMenu) return;
    FALLBACK_GROUPS.forEach(function (meta) {
      var section = nav.querySelector('[data-nav-group="' + meta.key + '"]');
      if (!section) {
        section = document.createElement('section');
        section.className = 'bz-nav-group is-open';
        section.setAttribute('data-nav-group', meta.key);
        var button = document.createElement('button');
        button.type = 'button';
        button.className = 'bz-nav-group-toggle';
        button.setAttribute('aria-expanded', 'true');
        button.innerHTML = '<span>' + meta.label + '</span><span class="group-arrow" aria-hidden="true">⌄</span>';
        var items = document.createElement('div');
        items.className = 'bz-nav-group-links';
        section.appendChild(button);
        section.appendChild(items);
        nav.appendChild(section);
      }
      var container = section.querySelector('.bz-nav-group-links') || section;
      meta.links.forEach(function (item) {
        if (!existing[item[2]]) {
          container.appendChild(makeFallbackLink(item[0], item[1], item[2]));
          existing[item[2]] = true;
        }
      });
    });
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
    ensureFallbackGroups(nav);
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
      } else if (!active) {
        group.classList.add('is-collapsed');
        if (button) button.setAttribute('aria-expanded', 'false');
      } else {
        group.classList.remove('is-collapsed');
        if (button) button.setAttribute('aria-expanded', 'true');
      }
      if (button && !button.dataset.bound) {
        button.dataset.bound = '1';
        button.addEventListener('click', function () {
          groups.forEach(function (other) {
            if (other === group) return;
            other.classList.add('is-collapsed');
            var otherButton = other.querySelector('.bz-nav-group-toggle');
            if (otherButton) otherButton.setAttribute('aria-expanded', 'false');
            saved[other.getAttribute('data-nav-group')] = false;
          });
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

    groups.forEach(function (group) {
      Array.prototype.forEach.call(group.querySelectorAll('.bz-nav-group-links a'), function (link) {
        if (link.dataset.mobileCloseBound) return;
        link.dataset.mobileCloseBound = '1';
        link.addEventListener('click', function () {
          if (window.matchMedia && window.matchMedia('(max-width: 900px)').matches) {
            document.body.classList.remove('sidebar-is-open');
            var overlay = document.getElementById('bzOverlay');
            if (overlay) overlay.setAttribute('aria-hidden', 'true');
          }
        });
      });
    });
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
