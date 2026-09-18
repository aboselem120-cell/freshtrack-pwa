// Service Worker for FreshTrack — caches the app shell so the interface
// loads instantly and works offline after the first visit.

const CACHE_NAME = 'freshtrack-shell-v3';
const APP_SHELL = [
  './',
  './index.html',
  './manifest.json',
  './icons/icon-192.png',
  './icons/icon-512.png',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      )
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  // The Cache API only supports GET requests. Our POST to /api/analyze (photo
  // analysis) must never be intercepted here — just let it go straight to the
  // network untouched, or it fails with a "response is null" error.
  if (event.request.method !== 'GET') {
    return; // let the browser handle it normally, no respondWith at all
  }

  const url = new URL(event.request.url);

  if (url.origin === self.location.origin) {
    // Network-first for the app itself. A pure cache-first strategy here would
    // mean code updates never reach a phone that already has the app installed
    // — the cached index.html would be served forever with no way to notice a
    // newer version exists. Network-first always tries the live file first
    // (so every fix/feature ships immediately on next reload) and only falls
    // back to the cached copy when there's genuinely no connection.
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
          return response;
        })
        .catch(() => caches.match(event.request))
    );
    return;
  }

  // External resources (fonts, etc.): network-first, falling back to cache when offline.
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        const clone = response.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
        return response;
      })
      .catch(() => caches.match(event.request))
  );
});

// --- Real push notifications ---
// Fired by the browser even if the app is fully closed, whenever the
// /api/send-reminders cron job sends a push through the subscription
// stored in Supabase. This is what makes notifications work without the
// app open — the piece localStorage-only reminders could never do.
self.addEventListener('push', (event) => {
  let data = { title: 'FreshTrack', body: 'You have items expiring soon.' };
  try {
    if (event.data) data = event.data.json();
  } catch (e) {
    if (event.data) data.body = event.data.text();
  }

  event.waitUntil(
    self.registration.showNotification(data.title || 'FreshTrack', {
      body: data.body,
      icon: './icons/icon-192.png',
      badge: './icons/icon-192.png',
    })
  );
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
      for (const client of clientList) {
        if ('focus' in client) return client.focus();
      }
      if (clients.openWindow) return clients.openWindow('./');
    })
  );
});

