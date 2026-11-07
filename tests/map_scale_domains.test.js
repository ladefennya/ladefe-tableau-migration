const assert=require('node:assert/strict'),path=require('node:path');
const map=require(process.argv[2]?path.resolve(process.argv[2]):'../demo/map-utils.js');
const s=map.discreteScale([0,5,10]);
// These values can arise from a bad JSON shape or UI input: coercion must not invent data.
const dangerous={valueOf(){throw new Error('must never be coerced')}};
for(const value of [[],[0],[5],{},new Number(0),new Date(0),dangerous,Symbol('x'),0n,true,false,null,undefined,'',' ','0x10','0b10','1,5']){
 assert.doesNotThrow(()=>s.color(value),'Invalid input must be treated as missing without invoking conversion');
 assert.equal(s.color(value),map.MISSING,`Non-decimal or non-scalar value must be missing: ${typeof value}`);
}
assert.equal(s.color(0),s.color('0'));assert.notEqual(s.color(0),map.MISSING);assert.equal(s.color('5e0'),s.color(5));
const constant=map.discreteScale([7,7,7]);assert.equal(constant.ranges.length,1,'A constant indicator must not show five contradictory equal legend ranges');assert.equal(constant.ranges[0].color,constant.color(7));
const fixed1=map.discreteScale([0,5,10],undefined,{domain:[0,100]}),fixed2=map.discreteScale([5,80],undefined,{domain:[0,100]});assert.equal(fixed1.color(5),fixed2.color(5));assert.deepEqual(fixed1.ranges,fixed2.ranges,'Same approved domain must remain stable between years/filters');
for(const domain of [[100,0],[null,100],[0,Infinity],[0],[]])assert.throws(()=>map.discreteScale([5],undefined,{domain}),TypeError,'Malformed domain must block instead of silently reclassifying');
assert.throws(()=>map.discreteScale([1],[]),TypeError);
console.log('PASS: scalar validation; no coercion; constant legend; fixed-domain stability; invalid configuration blocked');
