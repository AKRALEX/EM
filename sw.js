/* Service worker : rend l'appli utilisable hors ligne une fois installee.
   - data/ (tirages, parametres) : reseau d'abord, pour avoir le dernier
     tirage ; copie locale si le telephone est hors ligne.
   - tout le reste (page, scripts Python, moteur Pyodide, polices) : copie
     locale d'abord, rafraichie en arriere-plan.
   Changer VERSION force le renouvellement du cache apres une mise a jour. */
const VERSION = "em-v1";

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
  const donnees = url.origin === location.origin && url.pathname.includes("/data/");
  e.respondWith(donnees ? reseauDabord(e.request) : cacheDabord(e.request));
});
