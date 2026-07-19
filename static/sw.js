const CACHE_NAME = 'bin-zomah-v1';
const urlsToCache = [
  '/',
  '/manifest.json',
  '/static/logo_192.png',
  '/static/logo_512.png',
  '/static/nav_logo.png',
  '/static/base_styles.css',
  '/static/css/theme.css',
  '/static/app_ux.js'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(urlsToCache);
    })
  );
});

self.addEventListener('fetch', (e) => {
  e.respondWith(
    caches.match(e.request).then(response => {
      // Return cached response if found, else fetch from network
      return response || fetch(e.request);
    }).catch(() => {
        // Fallback for offline mode if needed
    })
  );
});

// Activate event to clean up old caches
self.addEventListener('activate', (e) => {
    const cacheWhitelist = [CACHE_NAME];
    e.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheWhitelist.indexOf(cacheName) === -1) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});
