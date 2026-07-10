const CACHE_NAME = 'fleet-pwa-v3';
const OFFLINE_URL = '/offline.html';

// ملفات أساسية للتخزين
const CORE_ASSETS = [
  '/',
  '/manifest.json'
];

// تثبيت الـ Service Worker
self.addEventListener('install', (event) => {
  console.log('🚀 Service Worker Installing...');
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(CORE_ASSETS);
    })
  );
  self.skipWaiting();
});

// تنشيط الـ Service Worker
self.addEventListener('activate', (event) => {
  console.log('✅ Service Worker Activated');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cache) => {
          if (cache !== CACHE_NAME) {
            return caches.delete(cache);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// جلب الموارد (Network First + Cache Fallback)
self.addEventListener('fetch', (event) => {
  // للطلبات التي تخص الـ API (لا نستخدم الكاش لها)
  if (event.request.url.includes('/api/')) {
    event.respondWith(fetch(event.request));
    return;
  }

  // لباقي الطلبات (Network First)
  event.respondWith(
    fetch(event.request)
      .then(response => {
        // تحديث الكاش بالنسخة الجديدة
        const responseClone = response.clone();
        caches.open(CACHE_NAME).then(cache => {
          cache.put(event.request, responseClone);
        });
        return response;
      })
      .catch(() => {
        // إذا انقطع الاتصال، جرب جلب الملف من الكاش
        return caches.match(event.request).then(cachedResponse => {
          if (cachedResponse) {
            return cachedResponse;
          }
        });
      })
  );
});

// استلام الإشعارات (Push Notifications)
self.addEventListener('push', (event) => {
  const data = event.data ? event.data.json() : { title: 'إشعار جديد', body: 'تحديث في نظام الأسطول' };
  
  const options = {
    body: data.body,
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: '1'
    }
  };

  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

// التفاعل مع الإشعارات (عند النقر)
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  event.waitUntil(
    clients.openWindow('/')
  );
});
