const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const semantics=require("../demo/semantics.js");

function dataset(slug){return JSON.parse(fs.readFileSync(path.join(__dirname,"..","demo","data",slug+".json"),"utf8"))}
function indicator(data,id){return data.indicators.find(row=>String(row.id)===String(id))}
function row(data,id,territory,extra=()=>true){return data.rows.find(item=>String(item.indicatorId)===String(id)&&item.geoName===territory&&extra(item))}
function displayed(data,id,item){return semantics.displayValue(item,indicator(data,id))}

const auh=dataset("2-2bauh");
assert.equal(displayed(auh,"218",row(auh,"218","BUENOS AIRES")).toFixed(2),"34.15","AUH coverage must be a percentage, not a beneficiary count");

const census=dataset("1-1aspectosdemogrficos-informacincensal");
assert.equal(displayed(census,"504",row(census,"504","BUENOS AIRES")).toFixed(2),"26.60","Census participation must use total population as denominator");

const housing=dataset("2-5aviviviendacfchabitacionales");
assert.equal(displayed(housing,"814",row(housing,"814","BUENOS AIRES")).toFixed(2),"9.12","Overcrowding must be expressed as a percentage");

const schools=dataset("3-2aestablecimientoscaracteristicas");
const base=schools.rows.find(item=>String(item.indicatorId)==="115"&&item.year===2015&&item.mode1==="Total de establecimientos de nivel inicial");
assert.equal(displayed(schools,"115",base),100,"Base-100 index must not be divided by its baseline count");

const migrants=dataset("8-3annyamigrantes-losmigrantesenloscensosnacionales");
const migrantRows=migrants.rows.filter(item=>String(item.indicatorId)==="1031"&&item.year===2022);
assert.ok(new Set(migrantRows.map(semantics.dimensionKey)).size>1,"Different migrant age universes must retain distinct dimensional keys");

const suicide=dataset("7-3emortalidadadolescentesuicidios");
const suicideIndicator=suicide.indicators.find(item=>item.unitCode==="TASA_X_CIENMIL");
const directRate=suicide.rows.find(item=>String(item.indicatorId)===String(suicideIndicator.id)&&item.aux==null);
assert.equal(semantics.calculation(suicideIndicator,directRate).mode,"direct","Pre-calculated F02 rates without denominator must remain direct values");

console.log("Six-pilot regression values passed");
