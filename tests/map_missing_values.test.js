const assert=require('node:assert/strict');
const path=require('node:path');
const map=require(process.argv[2]?path.resolve(process.argv[2]):'../demo/map-utils.js');
for(const domain of [[0,5,10],[-5,0,5],[0],[null,undefined,NaN,'','  ']]){
 const s=map.discreteScale(domain);
 for(const v of [null,undefined,NaN,'','  ',Infinity,-Infinity,true,false])assert.equal(s.color(v),map.MISSING,`Missing ${String(v)} must stay missing in ${JSON.stringify(domain)}`);
 if(domain.some(x=>typeof x==='number'&&Number.isFinite(x))){
  assert.notEqual(s.color(0),map.MISSING,'Real zero must have a data color');
  assert.equal(s.color('0'),s.color(0),'Numeric string zero is a value');
 }else{assert.equal(s.lo,null);assert.equal(s.hi,null);assert.deepEqual(s.ranges,[]);}
}
const s=map.discreteScale([-5,0,5]);assert.notEqual(s.color(-5),map.MISSING);assert.equal(s.color(-10),s.colors[0]);assert.equal(s.color(10),s.colors[s.colors.length-1]);
assert.notEqual(s.color(-5),s.color(5));
console.log('PASS: missing/zero/negative/all-missing/numeric-string/bounds regressions');
