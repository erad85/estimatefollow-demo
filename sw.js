/* EstimateFollow fictional-data-only demo offline shell */
const CACHE_NAME='estimatefollow-shell-pages-v034';
const APP_SHELL=['./','./index.html','./manifest.webmanifest','./icons/icon.svg','./icons/icon-192.png'];
self.addEventListener('install',event=>event.waitUntil(caches.open(CACHE_NAME).then(cache=>cache.addAll(APP_SHELL)).then(()=>self.skipWaiting())));
self.addEventListener('activate',event=>event.waitUntil(Promise.all([caches.keys().then(keys=>Promise.all(keys.filter(key=>key.startsWith('estimatefollow-shell-')&&key!==CACHE_NAME).map(key=>caches.delete(key)))),self.clients.claim()])));
self.addEventListener('fetch',event=>{
const request=event.request;
if(request.method!=='GET'||new URL(request.url).origin!==self.location.origin)return;
event.respondWith(caches.match(request).then(cached=>cached||fetch(request)));
});