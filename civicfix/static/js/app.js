(() => {
"use strict";
const $ = (s, r=document) => r.querySelector(s);
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const POLL_MS = 5000;
const mapEl = $("#map");
let map, markers = [];
if (mapEl && window.L) {
  map = L.map(mapEl).setView([20.5937,78.9629],5);
  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors", maxZoom:19, referrerPolicy:"origin"
  }).addTo(map);
}
function showMarkers(issues) {
  if (!map) return;
  markers.forEach(m => m.remove());
  markers = issues.filter(i => Number.isFinite(Number(i.lat)) && Number.isFinite(Number(i.lng)))
    .map(i => L.marker([Number(i.lat),Number(i.lng)]).addTo(map)
      .bindPopup(`<b>${esc(i.title)}</b><br>${esc(i.status_label)}<br><a href="${esc(i.url)}">Open complaint</a>`));
  if (markers.length && !map._fitted) {
    map.fitBounds(L.featureGroup(markers).getBounds().pad(.3),{maxZoom:15});
    map._fitted=true;
  }
}
function live(ok) {
  const el=$("#live");
  if(el){el.textContent=ok?"Live":"Reconnecting";el.classList.toggle("off",!ok);}
}
function setStats(st) {
  document.querySelectorAll("[data-stat]").forEach(el=>{
    const key=el.dataset.stat;
    if(st && st[key]!==undefined) el.textContent=st[key];
  });
}
async function getJSON(url) {
  const response=await fetch(url,{credentials:"same-origin",headers:{"X-Requested-With":"XMLHttpRequest"}});
  if(!response.ok) throw new Error("Request failed");
  return response.json();
}
// Report form: click the map, drag the marker, or use geolocation.
if(mapEl?.dataset.mode==="picker" && map) {
  const lat=$("#id_latitude"),lng=$("#id_longitude"),locate=$("#locate");
  let pin;
  const set=(a,b)=>{
    if(lat)lat.value=Number(a).toFixed(6);
    if(lng)lng.value=Number(b).toFixed(6);
    if(pin)pin.setLatLng([a,b]);
    else pin=L.marker([a,b],{draggable:true}).addTo(map).on("dragend",e=>{
      const p=e.target.getLatLng();set(p.lat,p.lng);
    });
  };
  map.on("click",e=>set(e.latlng.lat,e.latlng.lng));
  if(locate) locate.addEventListener("click",()=>{
    if(!navigator.geolocation){alert("Geolocation is not supported. Click the map to place the pin.");return;}
    navigator.geolocation.getCurrentPosition(p=>{
      set(p.coords.latitude,p.coords.longitude);map.setView([p.coords.latitude,p.coords.longitude],16);
    },()=>alert("Location access was blocked. Click the map to place the pin instead."));
  });
}
// Detail page: live status and timeline.
if(mapEl?.dataset.mode==="single" && map) {
  const lat=Number(mapEl.dataset.lat),lng=Number(mapEl.dataset.lng);
  if(Number.isFinite(lat)&&Number.isFinite(lng)){map.setView([lat,lng],16);L.marker([lat,lng]).addTo(map);}
  const issue=$("#issue"),id=issue?.dataset.id;
  const tick=async()=>{
    try{
      const d=await getJSON(`/api/issue/${encodeURIComponent(id)}/`);live(true);
      const badge=$("#badge");
      if(badge && badge.textContent!==d.status_label){
        badge.textContent=d.status_label;badge.className=`badge s-${d.status}`;badge.classList.add("flash");
      }
      const timeline=$("#timeline");
      if(timeline && Array.isArray(d.updates)){
        const html=d.updates.map(u=>`<li class="s-${esc(u.key)}"><b>${esc(u.status)}</b> <span class="hint">${esc(u.at)} · ${esc(u.by)}</span>${u.note?`<br>${esc(u.note)}`:""}</li>`).join("");
        if(timeline.innerHTML.replace(/\s+/g,"")!==html.replace(/\s+/g,""))timeline.innerHTML=html;
      }
    }catch{live(false);}
  };
  tick();setInterval(tick,POLL_MS);
}
// Home/dashboard: refresh data every five seconds.
if(mapEl?.dataset.mode==="public") {
  const table=$("#issues tbody"),status=$("#f-status"),category=$("#f-category");
  const tick=async()=>{
    try{
      const params=new URLSearchParams();
      if(!table)params.set("public","1");
      else {if(status?.value)params.set("status",status.value);if(category?.value)params.set("category",category.value);}
      const data=await getJSON("/api/issues/?"+params.toString());
      live(true);setStats(data.stats);showMarkers(data.issues||[]);
      if(table){
        table.innerHTML=(data.issues||[]).map(i=>`<tr><td>${esc(i.id)}</td><td><a href="${esc(i.url)}">${esc(i.title)}</a></td><td>${esc(i.category)}</td><td>${esc(i.department)}</td><td>${esc(i.reporter)}</td><td><span class="badge s-${esc(i.status)}">${esc(i.status_label)}</span></td><td>${esc(i.created)}</td></tr>`).join("");
        const empty=$("#empty");if(empty)empty.hidden=(data.issues||[]).length>0;
      }
    }catch{live(false);}
  };
  if(table){[status,category].filter(Boolean).forEach(el=>el.addEventListener("change",tick));}
  tick();setInterval(tick,POLL_MS);
}
document.querySelectorAll("[data-back]").forEach(a=>a.addEventListener("click",e=>{
  if(history.length>1 && document.referrer.startsWith(location.origin)){e.preventDefault();history.back();}
}));
})();
