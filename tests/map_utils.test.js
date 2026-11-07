const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const map=require("../demo/map-utils.js");

const geo=JSON.parse(fs.readFileSync(path.join(__dirname,"..","demo","provincias.geojson"),"utf8"));
const project=map.projector(geo,420,470,18);
let points=0;
for(const feature of geo.features){
  assert.ok(map.pathForFeature(feature,project).startsWith("M"),`Missing projected path for ${map.featureName(feature)}`);
  for(const ring of map.rings(feature.geometry))for(const coordinate of ring)if(map.allowed(coordinate)){
    const [x,y]=project(coordinate);points+=1;
    assert.ok(Number.isFinite(x)&&Number.isFinite(y),"Projected coordinates must be finite");
    assert.ok(x>=17.9&&x<=402.1&&y>=17.9&&y<=452.1,"Projection must fit without stretching or clipping");
  }
}
assert.ok(points>100,"Expected province geometry points");
assert.ok(project([-65,-22])[1]<project([-65,-54])[1],"North must render above south");

const scale=map.discreteScale([18,21,24,27,30,32]);
assert.equal(new Set([18,21,24,27,30,32].map(scale.color)).size,5,"Five distinguishable color classes are required");
assert.equal(scale.color(null),map.MISSING,"Missing values need a neutral color");
assert.equal(map.territoryLabel("SANTIAGO DEL ESTERO"),"Santiago del Estero");
assert.equal(map.territoryLabel("CIUDAD AUTÓNOMA DE BUENOS AIRES"),"CABA");
assert.equal(map.territoryLabel("TIERRA DEL FUEGO"),"Tierra del Fuego");
// Recuadro bicontinental: sector antártico e islas del Atlántico Sur dentro de su caja, Polo Sur abajo.
const inset=JSON.parse(fs.readFileSync(path.join(__dirname,"..","demo","antartida.geojson"),"utf8"));
const box={x:432,y:240,w:122,h:222},insetProject=map.insetProjector(inset,box);
for(const ring of map.rings(inset.features[0].geometry))for(const coordinate of ring){
  const [x,y]=insetProject(coordinate);
  assert.ok(x>=box.x-0.1&&x<=box.x+box.w+0.1&&y>=box.y-0.1&&y<=box.y+box.h+0.1,"Inset must fit inside its box");
}
assert.ok(insetProject([-49.5,-90])[1]>insetProject([-36.5,-54.3])[1],"South Pole must render below the Georgias del Sur");
assert.ok(map.insetPath(inset.features[0],insetProject).startsWith("M"),"Inset path required");
assert.ok(geo.features.some(f=>map.provinceKey(map.featureName(f))===map.provinceKey(map.featureName(inset.features[0]))),"Inset must share the Tierra del Fuego key");
console.log("Map projection, colors, territory labels and bicontinental inset passed");
