const CACHE_NAME = 'chat-v1';
const urlsToCache = [
  '/',
  '/chat.html',
  '/css/global.css',
  '/css/login.css',
  '/css/chat.css',
  '/js/api.js',
  '/js/auth.js',
  '/js/chat.js',
  '/manifest.json'
];

// 安装
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

// 激活
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.filter(name => name !== CACHE_NAME)
          .map(name => caches.delete(name))
      );
    })
  );
});

// 请求拦截
self.addEventListener('fetch', event => {
  // API请求不缓存
  if (event.request.url.includes('/users/') || 
      event.request.url.includes('/messages/') ||
      event.request.url.includes('/health')) {
    return;
  }
  
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        if (response) {
          return response;
        }
        return fetch(event.request);
      })
  );
});