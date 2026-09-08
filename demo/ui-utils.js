(function(root,factory){
  const api=factory();
  if(typeof module==="object"&&module.exports)module.exports=api;
  else root.LadefeUI=api;
})(typeof globalThis!=="undefined"?globalThis:this,function(){
  function splitIndicatorName(value){
    const name=String(value||"").trim(),match=name.match(/^([A-ZÁÉÍÓÚÑ]\.\d+(?:[a-z])?)\s*(?:[-–—]\s*)?(.+)$/i);
    return match?{code:match[1],title:match[2].trim()}:{code:"",title:name};
  }
  function capabilityLabels(ownTypes,relatedTypes=[]){
    const own=new Set(ownTypes),related=new Set(relatedTypes),items=[];
    if(own.has("SERIE_TEMPORAL"))items.push({type:"SERIE_TEMPORAL",label:"Serie temporal",related:false});else if(related.has("SERIE_TEMPORAL"))items.push({type:"SERIE_TEMPORAL",label:"Serie relacionada",related:true});
    if(own.has("MAPA"))items.push({type:"MAPA",label:"Mapa provincial",related:false});else if(related.has("MAPA"))items.push({type:"MAPA",label:"Mapa relacionado",related:true});
    if(own.has("DISTRIBUCION"))items.push({type:"DISTRIBUCION",label:"Distribución",related:false});
    if(own.has("APERTURA"))items.push({type:"APERTURA",label:"Aperturas",related:false});
    return items;
  }
  return{splitIndicatorName,capabilityLabels};
});
