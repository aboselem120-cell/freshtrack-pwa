// Service Worker for FreshTrack — caches the app shell so the interface
// loads instantly and works offline after the first visit.

const CACHE_NAME = 'freshtrack-shell-v5'; // v5: drops the per-query/API entries v4 accumulated
const APP_SHELL = [
  './',
  './index.html',
  './manifest.json',
  './icon-192.png',
  './icon-512.png',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL))
  );
  // No automatic skipWaiting() here — a newly installed worker stays in
  // "waiting" until the page's update banner (see index.html) tells it to
  // take over. Without this, updates activate silently in the background
  // and an already-open tab keeps running old JS indefinitely.
});

self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        // keep the current shell and the small prefs store (app language)
        keys.filter((key) => key !== CACHE_NAME && key !== 'freshtrack-prefs').map((key) => caches.delete(key))
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
    // API responses are never cached.
    if (url.pathname.startsWith('/api/')) return;
    // Cache pages under their path only: every ?utm_source=… / ?notrack /
    // ?action=scan variant used to get its own permanent cache entry.
    const cacheKey = event.request.mode === 'navigate'
      ? new Request(url.origin + url.pathname)
      : event.request;
    // Network-first for the app itself. A pure cache-first strategy here would
    // mean code updates never reach a phone that already has the app installed
    // — the cached index.html would be served forever with no way to notice a
    // newer version exists. Network-first always tries the live file first
    // (so every fix/feature ships immediately on next reload) and only falls
    // back to the cached copy when there's genuinely no connection.
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          if (response.ok) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(cacheKey, clone));
          }
          return response;
        })
        .catch(() => caches.match(cacheKey))
    );
    return;
  }

  // External: only static assets (fonts, the Supabase JS library) are cached
  // for offline use. Supabase API calls and analytics pass straight through —
  // each distinct query used to add another cache entry.
  const STATIC_HOSTS = ['fonts.googleapis.com', 'fonts.gstatic.com', 'cdn.jsdelivr.net'];
  if (!STATIC_HOSTS.includes(url.hostname)) return;

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
const PUSH_TEXT = {
  en: (n) => `${n} item${n > 1 ? 's' : ''} expiring soon — check FreshTrack`,
  ar: (n) => `${n} غرض قريب من الانتهاء — افتح FreshTrack`,
  es: (n) => `${n} artículo${n > 1 ? 's' : ''} por caducar — revisa FreshTrack`,
};
const PUSH_TEST_TEXT = {
  en: 'Test notification — reminders will arrive like this.',
  ar: 'إشعار تجريبي — التذكيرات بتوصلك بهذا الشكل.',
  es: 'Notificación de prueba — los recordatorios llegarán así.',
};

// The app saves its current language here (see rememberLangForPush in index.html).
async function appLanguage() {
  try {
    const res = await (await caches.open('freshtrack-prefs')).match('/__lang');
    const lang = res ? (await res.text()).trim() : '';
    return PUSH_TEXT[lang] ? lang : 'en';
  } catch (e) {
    return 'en';
  }
}

self.addEventListener('push', (event) => {
  let data = { title: 'FreshTrack', body: 'You have items expiring soon.' };
  try {
    if (event.data) data = event.data.json();
  } catch (e) {
    if (event.data) data.body = event.data.text();
  }

  event.waitUntil((async () => {
    // Newer payloads carry just the count; word it in the app's language.
    let body = data.body;
    if (data.test) body = PUSH_TEST_TEXT[await appLanguage()];
    else if (typeof data.count === 'number') body = PUSH_TEXT[await appLanguage()](data.count);
    await self.registration.showNotification(data.title || 'FreshTrack', {
      body,
      icon: './icon-192.png',
      badge: './icon-192.png',
    });
  })());
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

