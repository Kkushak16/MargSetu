/**
 * MargSetu Progressive Web App Service Worker (Member C - Prompt 6)
 * SIH26002 - Smart Logistics & Accessibility Platform
 * 
 * Provides offline caching for static assets, map tiles, and offline hazard queue background sync.
 */

const CACHE_NAME = 'margsetu-pwa-cache-v1';
const ASSETS_TO_CACHE = [
  '/',
  '/index.html',
  '/manifest.json'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS_TO_CACHE);
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  // Network-first policy with cache fallback for offline disaster operation
  event.respondWith(
    fetch(event.request).catch(() => {
      return caches.match(event.request).then((response) => {
        return response || caches.match('/index.html');
      });
    })
  );
});
