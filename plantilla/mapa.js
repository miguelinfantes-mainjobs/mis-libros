document.addEventListener('click',e=>{
 const n=e.target.closest('.nodo');
 if(n){const li=n.parentElement;const a=li.classList.toggle('abierto');n.setAttribute('aria-expanded',a);return}
 const c=e.target.closest('[data-accion]');
 if(c){const abrir=c.dataset.accion==='abrir';document.querySelectorAll('.mapa li').forEach(li=>{if(li.querySelector(':scope>ul')&&!li.classList.contains('raiz')){li.classList.toggle('abierto',abrir);li.firstElementChild.setAttribute('aria-expanded',abrir)}});return}
 const p=e.target.closest('[data-vista]');
 if(p){document.querySelectorAll('[data-vista]').forEach(b=>b.classList.toggle('activa',b===p));document.querySelectorAll('.vista').forEach(v=>v.classList.toggle('oculto',v.id!=='v-'+p.dataset.vista))}
});
