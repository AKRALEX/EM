/* Service worker : rend l'appli utilisable hors ligne une fois installee.
   - fichiers de l'appli (page, scripts Python, tirages, parametres) :
     reseau d'abord, pour toujours avoir la derniere version ; copie locale
     si le telephone est hors ligne.
   - moteur Pyodide et polices (autres sites, jamais modifies) : copie
     locale d'abord.
   Changer VERSION vide l'ancien cache. */
const VERSION = "em-v3";

self.addEventListener("install", (e) => { self.skipWaiting(); });
self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((cles) => Promise.all(cles.filter((c) => c !== VERSION).map((c) => caches.delete(c))))
      .then(() => self.clients.claim())
  );
});

async function reseauDabord(requete) {
  const cache = await caches.open(VERSION);
  try {
    const reponse = await fetch(requete);
    if (reponse.ok) cache.put(requete, reponse.clone());
    return reponse;
  } catch (err) {
    const copie = await cache.match(requete);
    if (copie) return copie;
    throw err;
  }
}

async function cacheDabord(requete) {
  const cache = await caches.open(VERSION);
  const copie = await cache.match(requete);
  const maj = fetch(requete).then((reponse) => {
    if (reponse.ok || reponse.type === "opaque") cache.put(requete, reponse.clone());
    return reponse;
  });
  if (copie) { maj.catch(() => {}); return copie; }
  return maj;
}

self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET") return;
  const url = new URL(e.request.url);
  const appli = url.origin === location.origin;
  e.respondWith(appli ? reseauDabord(e.request) : cacheDabord(e.request));
});
