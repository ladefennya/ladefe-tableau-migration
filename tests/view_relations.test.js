const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");

const root=path.join(__dirname,"..");
const relations=JSON.parse(fs.readFileSync(path.join(root,"demo","view-relations.json"),"utf8"));
const catalog=JSON.parse(fs.readFileSync(path.join(root,"demo","catalog.json"),"utf8")).dashboards;
const knownDashboards=new Set(catalog.map(item=>item.slug));

assert.equal(relations.version,1,"Relation schema version must be explicit");
assert.equal(relations.status,"pilot-provisional","Curated relations must remain marked as provisional until thematic sign-off");

let relationCount=0;
for(const [slug,groups] of Object.entries(relations.dashboards||{})){
  assert.ok(knownDashboards.has(slug),`Unknown dashboard in curated relations: ${slug}`);
  const data=JSON.parse(fs.readFileSync(path.join(root,"demo","data",`${slug}.json`),"utf8"));
  const indicators=new Map(data.indicators.map(item=>[String(item.id),item]));
  const rowsByIndicator=new Map();
  for(const row of data.rows){
    const id=String(row.indicatorId);
    if(!rowsByIndicator.has(id))rowsByIndicator.set(id,[]);
    rowsByIndicator.get(id).push(row);
  }
  const relationIds=new Set();
  for(const relation of groups){
    relationCount+=1;
    assert.ok(relation.id&&!relationIds.has(relation.id),`Duplicate relation id in ${slug}: ${relation.id}`);
    relationIds.add(relation.id);
    assert.ok(relation.rationale,"Every curated relation needs an auditable rationale");
    assert.ok(relation.members.map(String).includes(String(relation.seriesIndicatorId)),`${relation.id}: series target must be a member`);
    assert.ok(relation.members.map(String).includes(String(relation.mapIndicatorId)),`${relation.id}: map target must be a member`);
    const members=relation.members.map(id=>{
      const item=indicators.get(String(id));
      assert.ok(item,`${relation.id}: unknown member ${id}`);
      return item;
    });
    assert.equal(new Set(members.map(item=>item.unitCode)).size,1,`${relation.id}: members must use the same unit`);
    const seriesRows=rowsByIndicator.get(String(relation.seriesIndicatorId))||[];
    const mapRows=rowsByIndicator.get(String(relation.mapIndicatorId))||[];
    assert.ok(seriesRows.some(row=>row.type==="SERIE_TEMPORAL"),`${relation.id}: series target has no temporal rows`);
    assert.ok(mapRows.some(row=>row.type==="MAPA"),`${relation.id}: map target has no territorial rows`);
    assert.ok(new Set(seriesRows.filter(row=>row.type==="SERIE_TEMPORAL").map(row=>row.year)).size>=2,`${relation.id}: temporal target needs at least two periods`);
    const latestMapYear=Math.max(...mapRows.filter(row=>row.type==="MAPA").map(row=>Number(row.year)).filter(Number.isFinite));
    const latestMapRows=mapRows.filter(row=>row.type==="MAPA"&&Number(row.year)===latestMapYear);
    assert.equal(new Set(latestMapRows.map(row=>row.geoName)).size,24,`${relation.id}: latest territorial target must cover 24 jurisdictions`);
    assert.equal(latestMapRows.length,24,`${relation.id}: latest territorial target must have one unambiguous row per jurisdiction`);
  }
}

assert.equal(relationCount,3,"Only the three reviewed high-confidence pilot relations may be active");
console.log("Three curated pilot view relations passed");
