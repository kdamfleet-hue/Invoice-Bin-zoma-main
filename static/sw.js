const CACHE_NAME = 'bin-zomah-v2';
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
  // Force the waiting service worker to become the active service worker
  self.skipWaiting();
  
  e.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(urlsToCache);
    })
  );
});

self.addEventListener('activate', (e) => {
  // Take control of all pages immediately
  e.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName); // Delete all old caches
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  // Skip cross-origin requests
  if (!e.request.url.startsWith(self.location.origin)) {
    return;
  }

  // Network-first strategy: Always fetch latest from server, fallback to cache if offline
  e.respondWith(
    fetch(e.request).then(response => {
      // Check if valid response
      if (!response || response.status !== 200 || response.type !== 'basic') {
          return response;
      }
      
      // Update cache with the latest version
      const responseToCache = response.clone();
      caches.open(CACHE_NAME).then(cache => {
        cache.put(e.request, responseToCache);
      });
      
      return response;
    }).catch(() => {
      // Network failed (offline), try to serve from cache
      return caches.match(e.request);
    })
  );
});
