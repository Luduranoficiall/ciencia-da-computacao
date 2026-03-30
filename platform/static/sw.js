const CACHE = "curso-ui-v2";
const ASSETS = [
  "/ui/",
  "/ui/index.html",
  "/ui/styles.css",
  "/ui/app.js",
  "/ui/manifest.json",
  "/ui/verify.html",
  "/ui/verify.js",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE).then((cache) => {
      return cache.addAll(ASSETS).catch(() => {});
    }),
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(keys.map((k) => (k === CACHE ? null : caches.delete(k))));
    }),
  );
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;

  event.respondWith(
    caches.match(req).then((cached) => {
      if (cached) return cached;
      return fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE).then((cache) => cache.put(req, copy)).catch(() => {});
          return res;
        })
        .catch(() => {
          // fallback simples: index
          return caches.match("/ui/index.html");
        });
    }),
  );
});

