/* Bin Zomah Fleet — Service Worker (PWA offline support).
   Cache the app shell; never cache API calls (keeps data fresh + workstation isolation). */
const CACHE = 'binzomah-v5';
const SHELL = [
  '/',
  '/static/base_styles.css',
  '/static/app_ux.js',
  '/static/nav_logo.png',
  '/static/main_logo.png',
  '/static/manifest.json',
  '/static/logo_192.png',
  '/static/logo_512.png'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE)
      .then((c) => Promise.all(SHELL.map((u) => c.add(u).catch(() => null))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;            // leave CDNs/external alone
  if (url.pathname.indexOf('/api') !== -1) return;            // never cache API (fresh data + isolation)

  if (req.mode === 'navigate') {
    // Network-first for pages; fall back to cache (or home) when offline.
    e.respondWith(
      fetch(req)
        .then((r) => { const cp = r.clone(); caches.open(CACHE).then((c) => c.put(req, cp)); return r; })
        .catch(() => caches.match(req).then((m) => m || caches.match('/')))
    );
  } else if (/\.(css|js)$/i.test(url.pathname)) {
    // Network-first for CSS/JS; bypass the HTTP cache (cache:'reload') so updates show IMMEDIATELY when online.
    e.respondWith(
      fetch(new Request(req.url, { cache: 'reload' }))
        .then((r) => { if (r && r.ok) { const cp = r.clone(); caches.open(CACHE).then((c) => c.put(req, cp)); } return r; })
        .catch(() => caches.match(req))
    );
  } else {
    // Cache-first for other static assets (images, fonts); update cache in the background.
    e.respondWith(
      caches.match(req).then((m) => m || fetch(req).then((r) => {
        if (r && r.ok) { const cp = r.clone(); caches.open(CACHE).then((c) => c.put(req, cp)); }
        return r;
      }).catch(() => m))
    );
  }
});
