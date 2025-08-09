const CACHE_NAME='spider-quest-v2';
const ASSETS=['./','./index.html','./style.css','./script.js','./manifest.json','./icon-192.png','./icon-512.png','./books/Spiders_Eight_Legs_of_Awesome_8p5x8p5.pdf','./books/Spiders_Eight_Legs_of_Awesome_8x10.pdf'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE_NAME).then(c=>c.addAll(ASSETS)))});
self.addEventListener('activate',e=>{e.waitUntil(self.clients.claim())});
self.addEventListener('fetch',e=>{e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request)))}});
