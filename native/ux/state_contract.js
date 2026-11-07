(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.QueryContract=api})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const VERSION='1';
const allowed=['qv','dataset','snapshot','release','period','series_from','series_to','territory','compare','universe'];
function defaults(catalog,id='education') {const d=catalog[id];return {qv:VERSION,dataset:id,snapshot:d.snapshot,release:d.release,period:d.periods[0],series_from:d.periods[d.periods.length-1],series_to:d.periods[0],territory:d.domain==='national'?'00':'all',compare:'',universe:d.universes[0]}}
function validate(raw,catalog){
 const fail=x=>{throw new Error(x)};
 if(!raw||typeof raw!=='object'||Array.isArray(raw))fail('Estado de consulta inválido.');
 for(const k of Object.keys(raw))if(!allowed.includes(k))fail('Parámetro desconocido: '+k);
 if(raw.qv!==VERSION)fail('Versión de consulta no compatible.');
 const d=catalog[raw.dataset];if(!d)fail('Conjunto de datos desconocido.');
 if(raw.snapshot!==d.snapshot||raw.release!==d.release)fail('La versión solicitada no está incluida en este prototipo. No se sustituyó por otra.');
 if(!d.periods.includes(raw.period))fail('Período de cuadro no disponible.');
 const chronological=d.periods.slice().reverse(),a=chronological.indexOf(raw.series_from),b=chronological.indexOf(raw.series_to);
 if(a<0||b<0||a>b)fail('Ventana de serie inválida.');
 if(!d.universes.includes(raw.universe))fail('Universo no compatible con el indicador.');
 const geos=d.domain==='national'?['00']:['all',...d.geos];
 if(!geos.includes(raw.territory))fail('El territorio no está respaldado por esta fuente.');
 if(raw.compare&&!d.geos.includes(raw.compare))fail('Territorio de comparación no disponible.');
 if(raw.compare&&(d.domain==='national'||raw.territory==='all'||raw.compare===raw.territory))fail('La comparación requiere dos territorios distintos del mismo indicador y universo.');
 return Object.fromEntries(allowed.map(k=>[k,raw[k]??'']));
}
function read(search,catalog){const p=new URLSearchParams(search);if(!p.size)return defaults(catalog);const r={};for(const [k,v]of p){if(k in r)throw new Error('Parámetro repetido: '+k);r[k]=v;}return validate(r,catalog)}
function encode(s){return '?'+new URLSearchParams(Object.fromEntries(allowed.map(k=>[k,s[k]??'']))).toString()}
function transition(s,patch,catalog){if(patch.dataset&&patch.dataset!==s.dataset)return defaults(catalog,patch.dataset);return validate({...s,...patch},catalog)}
function selectedRows(rows,s){return rows.filter(r=>r.period===s.period&&r.universe===s.universe&&(s.territory==='all'||r.geo===s.territory||r.geo===s.compare))}
return {defaults,validate,read,encode,transition,selectedRows};
});
