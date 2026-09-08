const assert=require("node:assert/strict");
const semantics=require("../demo/semantics.js");

const percentage={name:"Cobertura de AUH",unitCode:"PORCENTAJE"};
const perThousand={name:"Tasa de mortalidad",unitCode:"TASA_X_MIL"};
const base100={name:"Evolución comparada con 2015 (base 100)",unitCode:"PORCENTAJE"};

assert.equal(semantics.calculation(percentage,{value:1512200,aux:4427790}).mode,"ratio");
assert.equal(semantics.displayValue({value:1512200,aux:4427790},percentage).toFixed(2),"34.15");
assert.equal(semantics.displayValue({value:362,aux:147081},perThousand).toFixed(2),"2.46");
assert.equal(semantics.calculation(base100,{value:100,aux:18.497}).mode,"direct-index");
assert.equal(semantics.displayValue({value:100,aux:18.497},base100),100);
assert.equal(semantics.aggregate([{value:10},{value:20}],{unitCode:"CANTIDAD"}),null);
assert.equal(semantics.aggregate([{value:10,aux:100},{value:20,aux:200}],percentage,{allowAggregate:true}),10);
assert.notEqual(
  semantics.dimensionKey({level1:"Edad",mode1:"0–17"}),
  semantics.dimensionKey({level1:"Edad",mode1:"0–19"})
);
console.log("Semantic unit tests passed");
