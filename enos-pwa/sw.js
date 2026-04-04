const CACHE_NAME = 'enos-v3';
const API_CACHE = 'enos-api-v1';
const MAX_API_CACHE = 50;

self.addEventListener('install', (e) => {
  e.waitUntil(self.skipWaiting());
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(k => k !== CACHE_NAME && k !== API_CACHE).map(k => caches.delete(k))
      )
    ),
    self.clients.claim()
  );
});

self.addEventListener('fetch', (e) => {
  const { request } = e;
  if (request.method !== 'GET') return;
  const url = new URL(request.url);
  if (url.origin !== location.origin) return;

  // ── API requests: network-first, cache fallback ──────────────────────
  if (url.pathname.startsWith('/api/')) {
    e.respondWith(
      fetch(request)
        .then(r => {
          if (r.ok && r.status === 200) {
            const c = r.clone();
            caches.open(API_CACHE).then(m => m.put(request, c));
          }
          return r;
        })
        .catch(() => caches.match(request))
    );
    return;
  }

  // ── HTML: network-first, always update cache ────────────────────────
  if (request.headers.get('accept')?.includes('text/html')) {
    e.respondWith(
      fetch(request)
        .then(r => {
          if (r.ok) {
            const c = r.clone();
            caches.open(CACHE_NAME).then(m => m.put(request, c));
          }
          return r;
        })
        .catch(() => caches.match(request).then(r => r || caches.match('/')))
    );
    return;
  }

  // ── Static assets: cache-first ──────────────────────────────────────
  e.respondWith(
    caches.match(request).then(r => r || fetch(request).then(r2 => {
      if (r2.ok) {
        const c = r2.clone();
        caches.open(CACHE_NAME).then(m => m.put(request, c));
      }
      return r2;
    }))
  );
});
