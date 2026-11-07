(function(root,factory){
  const api=factory();
  if(typeof module==="object"&&module.exports)module.exports=api;
  else root.LadefeMap=api;
})(typeof globalThis!=="undefined"?globalThis:this,function(){
  const PALETTE=["#ffffcc","#a1dab4","#41b6c4","#2c7fb8","#253494"];
  const MISSING="#e3e9ed";
  const radians=value=>value*Math.PI/180;
  const allowed=point=>point&&point[0]>=-74.5&&point[0]<=-52.5&&point[1]>=-56&&point[1]<=-20;

  function norm(value){return String(value||"").normalize("NFD").replace(/[\u0300-\u036f]/g,"").toUpperCase().replace(/[^A-Z]/g,"")}
  function provinceKey(value){const n=norm(value);if(n.includes("CIUDADAUTONOMA")||n==="CABA"||n.includes("CAPITALFEDERAL"))return"CABA";if(n.includes("TIERRADELFUEGO"))return"TIERRADELFUEGO";return n.replace(/^PROVINCIADE/,"")}
  function featureName(feature){const p=feature.properties||{};return p.nam||p.nombre||p.NAME_1||p.fna||"Provincia"}
  function rings(geometry){if(!geometry)return[];if(geometry.type==="Polygon")return geometry.coordinates;if(geometry.type==="MultiPolygon")return geometry.coordinates.flat();return[]}
  function territoryLabel(value){
    const text=String(value||"").trim();if(!text)return"Sin especificar";if(provinceKey(text)==="CABA")return"CABA";
    const lower=text.toLocaleLowerCase("es-AR"),minor=new Set(["de","del","la","las","los","y","e"]);
    return lower.split(/\s+/).map((word,index)=>index&&minor.has(word)?word:word.charAt(0).toLocaleUpperCase("es-AR")+word.slice(1)).join(" ");
  }
  function rawAlbers(point){
    const lambda=radians(point[0]),phi=radians(point[1]),lambda0=radians(-65),phi0=radians(-40),phi1=radians(-20),phi2=radians(-50);
    const n=(Math.sin(phi1)+Math.sin(phi2))/2,c=1+Math.sin(phi1)*(2*n-Math.sin(phi1)),rho0=Math.sqrt(c-2*n*Math.sin(phi0))/n,rho=Math.sqrt(c-2*n*Math.sin(phi))/n,theta=n*(lambda-lambda0);
    return[rho*Math.sin(theta),rho*Math.cos(theta)-rho0];
  }
  function projector(geo,width=420,height=470,padding=18){
    const raw=[];for(const feature of geo.features||[])for(const ring of rings(feature.geometry))for(const point of ring)if(allowed(point))raw.push(rawAlbers(point));
    if(!raw.length)return()=>[width/2,height/2];
    const xs=raw.map(p=>p[0]),ys=raw.map(p=>p[1]),minX=Math.min(...xs),maxX=Math.max(...xs),minY=Math.min(...ys),maxY=Math.max(...ys),scale=Math.min((width-padding*2)/(maxX-minX||1),(height-padding*2)/(maxY-minY||1)),offsetX=(width-(maxX-minX)*scale)/2,offsetY=(height-(maxY-minY)*scale)/2;
    return point=>{const p=rawAlbers(point);return[offsetX+(p[0]-minX)*scale,offsetY+(p[1]-minY)*scale]};
  }
  function pathForFeature(feature,project){let d="";for(const ring of rings(feature.geometry)){const points=ring.filter(allowed).map(project);if(points.length>2)d+=points.map((p,index)=>(index?"L":"M")+p[0].toFixed(1)+","+p[1].toFixed(1)).join("")+"Z"}return d}
  function discreteScale(values,colors=PALETTE,options={}){
    // Accept scalar finite decimals only; never coerce objects, arrays or booleans to zero.
    const numeric=value=>{
      if(typeof value==="number")return Number.isFinite(value)?value:null;
      if(typeof value!=="string"||!/^[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?$/.test(value.trim()))return null;
      const number=Number(value);return Number.isFinite(number)?number:null;
    };
    if(!Array.isArray(colors)||!colors.length)throw new TypeError("A non-empty color palette is required");
    const nums=values.map(numeric).filter(value=>value!==null);
    let lo,hi;
    if(options.domain!==undefined){
      if(!Array.isArray(options.domain)||options.domain.length!==2)throw new TypeError("Scale domain requires two finite numbers");
      [lo,hi]=options.domain.map(numeric);
      if(lo===null||hi===null||lo>hi)throw new TypeError("Scale domain must be finite and ordered");
    }else if(nums.length){lo=Math.min(...nums);hi=Math.max(...nums)}
    else return{lo:null,hi:null,colors,missing:MISSING,color:()=>MISSING,ranges:[]};
    const span=hi-lo,middle=Math.floor(colors.length/2);
    const index=value=>{const n=numeric(value);return n===null?-1:span===0?middle:Math.max(0,Math.min(colors.length-1,Math.floor((n-lo)/span*colors.length)))};
    const ranges=span===0?[{color:colors[middle],from:lo,to:hi}]:colors.map((color,i)=>({color,from:lo+span*i/colors.length,to:lo+span*(i+1)/colors.length}));
    return{lo,hi,colors,missing:MISSING,color:value=>{const i=index(value);return i<0?MISSING:colors[i]},ranges};
  }
  return{PALETTE,MISSING,allowed,norm,provinceKey,featureName,rings,territoryLabel,rawAlbers,projector,pathForFeature,discreteScale};
});
