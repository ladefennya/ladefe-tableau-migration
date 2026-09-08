const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const ui=require("../demo/ui-utils.js");

const root=path.join(__dirname,"..");
const catalog=JSON.parse(fs.readFileSync(path.join(root,"demo","catalog.json"),"utf8")).dashboards;
let indicators=0,coded=0,boardsWithMap=0;
for(const board of catalog){
  const data=JSON.parse(fs.readFileSync(path.join(root,"demo",board.data),"utf8")),titles=new Set();let hasMap=false;
  for(const indicator of data.indicators){
    indicators+=1;const parts=ui.splitIndicatorName(indicator.name),key=parts.title.toLocaleLowerCase("es-AR");
    assert.ok(parts.title,`${board.slug}: indicator ${indicator.id} needs a public title`);
    assert.ok(!titles.has(key),`${board.slug}: duplicate public indicator title ${parts.title}`);titles.add(key);
    if(parts.code)coded+=1;
    if(data.rows.some(row=>String(row.indicatorId)===String(indicator.id)&&row.type==="MAPA"))hasMap=true;
  }
  if(hasMap)boardsWithMap+=1;
}
assert.equal(catalog.length,71,"All dashboards must remain available");
assert.equal(indicators,761,"All indicators must remain available");
assert.equal(boardsWithMap,51,"Map availability regression");
assert.ok(coded>=740,"Most inherited editorial codes should remain recoverable as secondary metadata");
assert.deepEqual(ui.capabilityLabels(["DISTRIBUCION"],["MAPA","SERIE_TEMPORAL"]).map(x=>x.label),["Serie relacionada","Mapa relacionado","Distribución"]);
console.log("Navigation labels and 71-dashboard coverage passed");
