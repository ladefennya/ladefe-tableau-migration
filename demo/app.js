const state={catalog:[],data:null,indicators:[],relations:{dashboards:{}},selected:[],geo:null,request:0,bound:false};
const $=id=>document.getElementById(id);
const esc=v=>String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const fmt=v=>Number.isFinite(Number(v))?new Intl.NumberFormat("es-AR",{maximumFractionDigits:2}).format(Number(v)):"—";
const unique=(rows,key)=>[...new Set(rows.map(r=>String(r[key]??"")).filter(Boolean))].sort((a,b)=>a.localeCompare(b,"es",{numeric:true}));
const VIEW_LABELS={APERTURA:"Aperturas",DISTRIBUCION:"Distribución",SERIE_TEMPORAL:"Evolución temporal",MAPA:"Comparación territorial"};
const TOPICS={
  "perfil-demografico-de-los-ninos-ninas-y-adolescentes":"Perfil demográfico de niñas, niños y adolescentes",
  "condiciones-de-vida-digna-en-la-ninez-y-adolescencia":"Condiciones de vida digna",
  "educacion-y-cuidado":"Educación y cuidado",
  salud:"Salud",
  "organismos-de-proteccion-de-derechos-de-la-ninez-adolescencia-y-justicia-juvenil":"Protección de derechos y justicia juvenil",
  "inversion-publica-en-ninez-y-adolescencia":"Inversión pública en niñez y adolescencia",
  adolescencia:"Adolescencia",
  "grupos-prioritarios":"Grupos prioritarios"
};
const SEM=window.LadefeSemantics;
const MAP=window.LadefeMap;
const UI=window.LadefeUI;

function fill(select,values,all=false){
  select.innerHTML=(all?'<option value="">Todas</option>':"")+values.map(v=>'<option value="'+esc(v.value??v)+'">'+esc(v.label??v)+'</option>').join("");
  select.value=all?"":String(values[0]?.value??values[0]??"");
}
function fillTopics(selected){
  const values=[...new Set(state.catalog.map(x=>x.topic))].map(value=>({value,label:TOPICS[value]||value})).sort((a,b)=>a.label.localeCompare(b.label,"es"));
  fill($("topic"),values); if(values.some(x=>x.value===selected))$("topic").value=selected;
}
function fillBoards(topic,selected){
  const values=state.catalog.filter(x=>x.topic===topic).sort((a,b)=>a.name.localeCompare(b.name,"es",{numeric:true})).map(x=>({value:x.slug,label:x.name}));
  fill($("board"),values); if(values.some(x=>x.value===selected))$("board").value=selected;
}
function currentIndicator(){return state.data?.indicators.find(x=>String(x.id)===$("indicator").value)||null}
function indicatorById(id){return state.data?.indicators.find(x=>String(x.id)===String(id))||null}
function base(){const id=$("indicator").value;return state.data?.rows.filter(r=>String(r.indicatorId)===id)||[]}
function ownRows(id,type){return state.data?.rows.filter(r=>String(r.indicatorId)===String(id)&&r.type===type)||[]}
function viewSpecFor(id,type){
  const selected=indicatorById(id),own=ownRows(id,type);if(own.length)return{rows:own,indicator:selected,related:false};
  const relation=(state.relations.dashboards?.[$("board").value]||[]).find(item=>item.members.map(String).includes(String(selected?.id))),field=type==="MAPA"?"mapIndicatorId":"seriesIndicatorId",target=relation?.[field],indicator=indicatorById(target);
  if(!indicator||indicator.unitCode!==selected?.unitCode)return{rows:[],indicator:selected,related:false};
  const rows=state.data.rows.filter(row=>String(row.indicatorId)===String(target)&&row.type===type);
  return{rows,indicator,related:Boolean(rows.length),relation};
}
function viewSpec(type){return viewSpecFor($("indicator").value,type)}
function rawValue(row){return SEM.rawValue(row)}
function rowValue(row,indicator=currentIndicator()){return SEM.displayValue(row,indicator)}
function unitLabel(indicator=currentIndicator()){return indicator?.unitDescription||indicator?.unit||"Valor"}
function cleanText(value){const text=String(value||"").trim();return !text||text==="."||text==="---"?"No informada":text}
function periodLabel(row){return [row.year,row.month].filter(v=>v!==null&&v!=="").join(" ")}
function periodRank(row){const y=Number(row.year)||0,m=String(row.month||"").toUpperCase(),n=Number((m.match(/\d+/)||[])[0]||0),factor=m.startsWith("T")||m.startsWith("Q")?3:m.startsWith("S")?6:1;return y*12+(n?n*factor:0)}
function dimensionLabel(row){
  const parts=[row.geoName,row.subGeo,row.opening,row.level1&&row.mode1?row.level1+": "+row.mode1:row.mode1,row.level2&&row.mode2?row.level2+": "+row.mode2:row.mode2].filter(Boolean);
  return parts.join(" · ")||"Serie";
}

function bind(){
  if(state.bound)return;state.bound=true;
  $("topic").addEventListener("change",()=>{fillBoards($("topic").value);loadBoard($("board").value)});
  $("board").addEventListener("change",()=>loadBoard($("board").value));
  $("indicator").addEventListener("change",()=>rebuildFilters());
  $("mapOnly").addEventListener("change",()=>{refreshIndicatorOptions($("indicator").value);rebuildFilters()});
  ["type","year"].forEach(id=>$(id).addEventListener("change",render));
  $("reset").onclick=()=>{$("mapOnly").checked=false;refreshIndicatorOptions();rebuildFilters()};
  $("download").onclick=download;
}
function ownTypes(id){return [...new Set((state.data?.rows||[]).filter(r=>String(r.indicatorId)===String(id)).map(r=>r.type).filter(Boolean))]}
function indicatorCapabilities(id){
  const own=ownTypes(id),related=[];
  for(const type of ["SERIE_TEMPORAL","MAPA"]){const spec=viewSpecFor(id,type);if(spec.related)related.push(type)}
  return UI.capabilityLabels(own,related);
}
function hasMap(id){return Boolean(viewSpecFor(id,"MAPA").rows.length)}
function preferredIndicator(indicators){return indicators.find(x=>{const types=ownTypes(x.id);return types.includes("MAPA")&&types.includes("SERIE_TEMPORAL")})||indicators.find(x=>hasMap(x.id))||indicators.find(x=>ownTypes(x.id).includes("SERIE_TEMPORAL"))||indicators[0]}
function refreshIndicatorOptions(preferredId){
  const available=$("mapOnly").checked?state.indicators.filter(x=>hasMap(x.id)):state.indicators;
  fill($("indicator"),available.map(x=>({value:x.id,label:UI.splitIndicatorName(x.name).title})));
  const preferred=available.find(x=>String(x.id)===String(preferredId))||preferredIndicator(available);
  $("indicator").value=String(preferred?.id||"");
  $("indicator").title=UI.splitIndicatorName(preferred?.name).title;
}

async function bootstrap(){
  bind();const response=await fetch("catalog.json");if(!response.ok)throw new Error("HTTP "+response.status);
  state.catalog=(await response.json()).dashboards;
  try{const relations=await fetch("view-relations.json?v=20260908-4");if(relations.ok)state.relations=await relations.json()}catch(_error){state.relations={dashboards:{}}}
  const params=new URLSearchParams(location.search),requested=params.get("tablero"),item=state.catalog.find(x=>x.slug===requested)||state.catalog[0];
  fillTopics(item.topic);fillBoards(item.topic,item.slug);await loadBoard(item.slug,true);
}
async function loadBoard(slug,restore=false){
  const item=state.catalog.find(x=>x.slug===slug);if(!item)return;
  const request=++state.request;$("theme").textContent=TOPICS[item.topic]||item.topic;$("message").hidden=false;$("message").textContent="Cargando "+item.name+"…";$("dashboard").hidden=true;
  const response=await fetch(item.data);if(!response.ok)throw new Error("HTTP "+response.status);const data=await response.json();if(request!==state.request)return;
  setup(data,restore);syncUrl();
}
function setup(data,restore){
  state.data=data;const params=new URLSearchParams(location.search);
  $("title").textContent=data.dashboard.name||"Tablero LADEFE";document.title="LADEFE · "+$("title").textContent;
  $("description").textContent=data.dashboard.description||"";$("updated").textContent=formatDate(data.dashboard.lastDataLoad);
  state.indicators=data.indicators.slice().sort((a,b)=>(Number(a.order)||9999)-(Number(b.order)||9999)||String(a.name).localeCompare(String(b.name),"es",{numeric:true}));
  const mapCount=state.indicators.filter(x=>hasMap(x.id)).length,anyMap=mapCount>0;
  if(restore)$("mapOnly").checked=params.get("solo_mapa")==="1";
  if(!anyMap)$("mapOnly").checked=false;
  $("mapOnly").disabled=!anyMap;$("mapOnlyText").textContent=anyMap?`Sólo con mapa (${mapCount} de ${state.indicators.length})`:"Sin mapas disponibles";
  const requested=restore?params.get("indicador"):null;
  refreshIndicatorOptions(requested);
  rebuildFilters(restore);
}
function formatDate(value){const match=String(value||"").match(/^(\d{4})-(\d{2})-(\d{2})/);return match?`${match[3]}/${match[2]}/${match[1]}`:"Sin informar"}
function rebuildFilters(restore=false){
  const rows=base(),params=new URLSearchParams(location.search),type=restore?params.get("vista"):null,year=restore?params.get("anio"):null;
  const types=unique(rows,"type").map(value=>({value,label:VIEW_LABELS[value]||value}));fill($("type"),types,true);if(types.some(x=>x.value===type))$("type").value=type;
  const years=unique(rows,"year").sort((a,b)=>Number(b)-Number(a));fill($("year"),years,true);if(years.includes(year))$("year").value=year;
  $("typeField").hidden=types.length<=1;$("yearField").hidden=years.length<=1;
  render();
}
function filtered(){return base().filter(r=>(!$("type").value||r.type===$("type").value)&&(!$("year").value||String(r.year)===$("year").value))}
function syncUrl(){
  if(!state.data)return;const url=new URL(location.href);url.searchParams.set("tablero",$("board").value);url.searchParams.set("indicador",$("indicator").value);
  $("type").value?url.searchParams.set("vista",$("type").value):url.searchParams.delete("vista");$("year").value?url.searchParams.set("anio",$("year").value):url.searchParams.delete("anio");
  $("mapOnly").checked?url.searchParams.set("solo_mapa","1"):url.searchParams.delete("solo_mapa");history.replaceState(null,"",url);
}

function renderIndicatorContext(indicator){
  const parts=UI.splitIndicatorName(indicator?.name),capabilities=indicatorCapabilities(indicator?.id),code=$("indicatorCode");
  code.hidden=!parts.code;code.textContent=parts.code;$("indicatorTitle").textContent=parts.title||"Indicador";$("indicator").title=parts.title;
  $("capabilities").innerHTML=capabilities.map(item=>'<span class="'+(item.related?"related":"")+'" title="'+(item.related?"Vista relacionada y curada provisionalmente":"Vista propia del indicador")+'">'+esc(item.label)+'</span>').join("");
}

function render(){
  const rows=filtered(),indicator=currentIndicator(),years=unique(base(),"year").map(Number).filter(Number.isFinite),latest=$("year").value||String(Math.max(...years));
  renderIndicatorContext(indicator);
  state.selected=rows;$("message").hidden=true;$("dashboard").hidden=false;$("records").textContent=rows.length+" registros seleccionados";$("range").textContent=years.length?Math.min(...years)+"–"+Math.max(...years):"—";
  $("unit").textContent=unitLabel(indicator);$("definition").textContent=cleanText(indicator?.definition);$("methodology").textContent=cleanText(indicator?.methodology);
  const groupIds=new Set(base().map(r=>String(r.groupId||""))),sources=state.data.groups.filter(g=>groupIds.has(String(g.id))).map(g=>g.sources).filter(Boolean);$("source").textContent=sources.length?[...new Set(sources)].join(" · "):"No informada";
  $("valueHeading").textContent="Valor ("+unitLabel(indicator)+")";
  const latestRows=rows.filter(r=>String(r.year)===latest),national=latestRows.filter(r=>/total|argentina|nacional|país/i.test((r.geoName||"")+" "+[r.opening,r.mode1,r.mode2].filter(Boolean).join(" ")));
  if(national.length===1){$("national").textContent=fmt(rowValue(national[0],indicator));$("nationalNote").textContent=unitLabel(indicator)+" · "+latest}else{$("national").textContent="—";$("nationalNote").textContent=national.length>1?"Seleccioná una apertura para obtener un valor único":"Sin agregado nacional"}
  const map=viewSpec("MAPA"),series=viewSpec("SERIE_TEMPORAL"),mapRows=map.rows,seriesRows=series.rows;$("chartPanel").hidden=!seriesRows.length;$("territoryPanel").hidden=!mapRows.length;$("capabilityMessage").hidden=Boolean(seriesRows.length||mapRows.length);
  const related=[series.related?"evolución: "+UI.splitIndicatorName(series.indicator.name).title:null,map.related?"territorio: "+UI.splitIndicatorName(map.indicator.name).title:null].filter(Boolean);$("relationNotice").hidden=!related.length;$("relationNotice").textContent=related.length?"Relación curada provisionalmente para este piloto (validación temática pendiente) — "+related.join(" · "):"";
  const visualGrid=$("chartPanel").parentElement;visualGrid.classList.toggle("single",Boolean(seriesRows.length)!==Boolean(mapRows.length));visualGrid.classList.toggle("empty",!seriesRows.length&&!mapRows.length);
  $("territories").textContent=mapRows.length?unique(mapRows.filter(r=>String(r.year)===($("year").value||String(Math.max(...unique(mapRows,"year").map(Number))))),"geoName").length:"—";
  if(seriesRows.length)drawLine(seriesRows,series.indicator);if(mapRows.length)drawMap(mapRows,map.indicator);drawTable(rows,indicator);syncUrl();
  $("message").textContent="Indicador actualizado: "+rows.length+" registros, "+unitLabel(indicator);
}

function drawLine(rows,indicator){
  const svg=$("lineChart");svg.innerHTML="";$("seriesLabel").textContent=UI.splitIndicatorName(indicator.name).title+" · "+unitLabel(indicator);
  const categories=[...new Map(rows.slice().sort((a,b)=>periodRank(a)-periodRank(b)).map(r=>[periodLabel(r),r])).entries()].map(([label,row])=>({label,rank:periodRank(row)})),index=new Map(categories.map((x,i)=>[x.label,i])),groups=new Map();
  rows.forEach(r=>{const name=dimensionLabel(r),value=rowValue(r,indicator),label=periodLabel(r);if(!Number.isFinite(value)||!index.has(label))return;if(!groups.has(name))groups.set(name,new Map());const points=groups.get(name);if(points.has(label)){points.set(label,null)}else points.set(label,value)});
  const valid=[...groups].map(([name,points])=>({name,points:[...points].filter(([,v])=>Number.isFinite(v)).map(([label,value])=>({i:index.get(label),label,value})).sort((a,b)=>a.i-b.i)})).filter(x=>x.points.length);
  const lines=valid.slice(0,6),all=lines.flatMap(x=>x.points.map(p=>p.value)),note=$("chartNote");note.hidden=valid.length<=6;note.textContent=valid.length>6?`Hay ${valid.length} series. Se muestran 6 para preservar la legibilidad; usá las aperturas de la tabla para revisar las restantes.`:"";if(!all.length)return;
  const W=760,H=330,p={l:65,r:18,t:55,b:45},lo=Math.min(...all),hi=Math.max(...all),sx=i=>p.l+i/Math.max(1,categories.length-1)*(W-p.l-p.r),sy=v=>p.t+(hi-v)/(hi-lo||1)*(H-p.t-p.b),colors=["#007b7b","#1769aa","#b24f18","#7654a8","#2d7a50","#b23455"];
  for(let i=0;i<5;i++){const y=p.t+i*(H-p.t-p.b)/4,val=hi-i*(hi-lo)/4;svg.insertAdjacentHTML("beforeend",'<line class="gridline" x1="'+p.l+'" y1="'+y+'" x2="'+(W-p.r)+'" y2="'+y+'"/><text class="tick" x="'+(p.l-8)+'" y="'+(y+4)+'" text-anchor="end">'+esc(fmt(val))+'</text>')}
  lines.forEach((line,k)=>{const color=colors[k%colors.length];svg.insertAdjacentHTML("beforeend",'<path class="series" stroke="'+color+'" d="'+line.points.map((q,i)=>(i?"L":"M")+sx(q.i)+","+sy(q.value)).join(" ")+'"/>');line.points.forEach(q=>svg.insertAdjacentHTML("beforeend",'<circle tabindex="0" cx="'+sx(q.i)+'" cy="'+sy(q.value)+'" r="4" fill="#fff" stroke="'+color+'" stroke-width="2" aria-label="'+esc(line.name+", "+q.label+": "+fmt(q.value)+" "+unitLabel(indicator))+'"><title>'+esc(line.name+" · "+q.label+": "+fmt(q.value))+'</title></circle>'));const lx=p.l+(k%2)*340,ly=17+Math.floor(k/2)*17;svg.insertAdjacentHTML("beforeend",'<line x1="'+lx+'" y1="'+ly+'" x2="'+(lx+18)+'" y2="'+ly+'" stroke="'+color+'" stroke-width="3"/><text class="tick" x="'+(lx+24)+'" y="'+(ly+4)+'">'+esc(line.name.slice(0,46))+'</text>')});
  const step=Math.max(1,Math.ceil(categories.length/7));categories.forEach((c,i)=>{if(i%step===0||i===categories.length-1)svg.insertAdjacentHTML("beforeend",'<text class="tick" x="'+sx(i)+'" y="'+(H-16)+'" text-anchor="middle">'+esc(c.label)+'</text>')});
}

async function ensureGeo(){if(state.geo)return state.geo;const response=await fetch("provincias.geojson");if(!response.ok)throw new Error("No se pudo cargar la geometría");return state.geo=await response.json()}
async function drawMap(source,indicator){
  const svg=$("mapChart"),selectionId=String(currentIndicator()?.id);svg.innerHTML='<text x="210" y="235" text-anchor="middle" class="tick">Cargando mapa…</text>';
  const years=unique(source,"year").map(Number).filter(Number.isFinite),requested=Number($("year").value),year=years.includes(requested)?requested:Math.max(...years),rows=source.filter(r=>Number(r.year)===year),byGeo=new Map(),ambiguous=[];
  rows.forEach(r=>{const key=MAP.provinceKey(r.geoName);if(key){if(!byGeo.has(key))byGeo.set(key,[]);byGeo.get(key).push(r)}});const values=new Map(),labels=new Map();byGeo.forEach((items,key)=>{if(items.length===1){values.set(key,rowValue(items[0],indicator));labels.set(key,MAP.territoryLabel(items[0].geoName))}else ambiguous.push(key)});
  const scale=MAP.discreteScale([...values.values()]);$("rankingYear").textContent="Año "+year+" · "+unitLabel(indicator)+(ambiguous.length?" · "+ambiguous.length+" territorios ambiguos omitidos":"");drawRanking(values,indicator,labels,scale);
  const geo=await ensureGeo();if(String(currentIndicator()?.id)!==selectionId)return;const project=MAP.projector(geo,420,470,18),hasMissing=(geo.features||[]).some(feature=>MAP.pathForFeature(feature,project)&&!Number.isFinite(values.get(MAP.provinceKey(MAP.featureName(feature)))));drawLegend(scale,hasMissing);paintMap(values,svg,geo,indicator,scale,project);
}
function drawLegend(scale,hasMissing){
  $("mapLegend").innerHTML='<span class="legend-title">Intervalos</span>'+scale.ranges.map(range=>'<span class="legend-bin"><i style="background:'+range.color+'"></i><small>'+esc(fmt(range.from))+"–"+esc(fmt(range.to))+"</small></span>").join("")+(hasMissing?'<span class="legend-bin"><i style="background:'+MAP.MISSING+'"></i><small>Sin dato</small></span>':"");
}
function paintMap(values,svg,geo,indicator,scale,project){
  svg.innerHTML="";
  for(const feature of geo.features||[]){const name=MAP.featureName(feature),value=values.get(MAP.provinceKey(name)),d=MAP.pathForFeature(feature,project);if(d){const label=name+": "+(Number.isFinite(value)?fmt(value)+" "+unitLabel(indicator):"sin dato");svg.insertAdjacentHTML("beforeend",'<path tabindex="0" role="img" aria-label="'+esc(label)+'" class="province" d="'+d+'" fill="'+scale.color(value)+'"><title>'+esc(label)+'</title></path>')}}
}
function drawRanking(values,indicator,labels,scale){const rows=[...values].filter(([,value])=>Number.isFinite(value)).map(([key,value])=>({name:labels.get(key)||key,value})).sort((a,b)=>b.value-a.value),max=Math.max(...rows.map(x=>Math.abs(x.value)),1);$("ranking").innerHTML=rows.map(x=>'<div class="rank"><span class="rank-name" title="'+esc(x.name)+'">'+esc(x.name)+'</span><span class="bar"><i style="width:'+Math.max(2,Math.abs(x.value)/max*100)+'%;background:'+scale.color(x.value)+'"></i></span><span class="rank-value">'+esc(fmt(x.value))+'</span></div>').join("");$("ranking").setAttribute("aria-label","Ranking provincial, "+unitLabel(indicator))}
function drawTable(rows,indicator){$("rows").innerHTML=rows.slice(0,250).map(r=>'<tr><td>'+esc(r.geoName||"—")+'</td><td>'+esc(r.year||"—")+'</td><td>'+esc(r.month||"—")+'</td><td>'+esc([r.opening,r.mode1,r.mode2].filter(Boolean).join(" · ")||"—")+'</td><td class="num">'+esc(fmt(rowValue(r,indicator)))+'</td></tr>').join("")}
function download(){
  const indicator=currentIndicator(),cols=["geoName","year","month","opening","mode1","mode2","displayValue","unit","rawValue","auxiliaryValue"],safe=value=>{let text=String(value??"");if(/^[=+\-@]/.test(text))text="'"+text;return '"'+text.replaceAll('"','""')+'"'},lines=[cols.join(","),...state.selected.map(r=>[r.geoName,r.year,r.month,r.opening,r.mode1,r.mode2,rowValue(r,indicator),unitLabel(indicator),rawValue(r),r.aux].map(safe).join(","))],url=URL.createObjectURL(new Blob(["\ufeff"+lines.join("\n")],{type:"text/csv;charset=utf-8"})),a=document.createElement("a");a.href=url;a.download="ladefe-"+$("board").value+".csv";a.click();URL.revokeObjectURL(url)
}
bootstrap().catch(error=>{$("message").hidden=false;$("message").textContent="No se pudo cargar el tablero: "+error.message});
