const cacheName = '1upou-pwa';
const filesToCache = [
    '/',
    '/static/app.js',
    '/static/styles/footer.css',
    '/static/styles/header.css',
    '/static/styles/modal.css',
    '/static/styles/sidebar.css',
    '/static/styles/template.css',
    '/static/styles/announcement.css',
    '/static/styles/toggle.css',
    '/static/styles/card.css',
    '/static/images/UPOU-Website-Header.png',
    '/static/offline.html',
    '/static/manifest.json',
    '/static/images/logo.png',
    '/static/images/favicon.ico',
    '/static/images/favicon.png',
    '/static/styles/optima/OPTIMA_B.woff',
    '/static/styles/avenir/avenirltstd-book-webfont.woff',
    '/static/images/University-of-the-Future-Official-Logo.png'
];

self.addEventListener('install', function(e) {
  console.log('[ServiceWorker] Install');
  e.waitUntil(
    caches.open(cacheName).then(function(cache) {
      console.log('[ServiceWorker] Caching app shell');
      return cache.addAll(filesToCache);
    })
  );
});

self.addEventListener('activate', function(e) {
  console.log('[ServiceWorker] Activate');
    e.waitUntil(
    caches.keys().then(function(keyList) {
      return Promise.all(keyList.map(function(key) {
        if (key !== cacheName) {
          console.log('[ServiceWorker] Removing old cache', key);
          return caches.delete(key);
        }
      }));
    })
  );
  return self.clients.claim();
});

// self.addEventListener('fetch', (e)=>{
//   e.respondWith(
//     fetch(e.request).catch(error =>{
      
//     })
//   )
// })

self.addEventListener('fetch', function(e) {
  console.log('[ServiceWorker] Fetch', e.request.url);
  e.respondWith(
    caches.match(e.request).then(function(response) {
      return fetch(e.request).catch(error => {
        if(response !== undefined) {return response}
        return caches.match('/static/offline.html')
      });
    })
  )
});