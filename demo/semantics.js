(function attach(root,factory){
  const api=factory();
  if(typeof module!=="undefined"&&module.exports)module.exports=api;
  if(root)root.LadefeSemantics=api;
})(typeof window!=="undefined"?window:null,function build(){
  const FACTORS={PORCENTAJE:100,TASA_X_CIEN:100,TASA_X_MIL:1000,RAZON_X_DIEZMIL:10000,TASA_X_CIENMIL:100000,TASA_X_MILLON:1000000};
  const number=value=>{const result=Number(value);return value!==null&&value!==""&&Number.isFinite(result)?result:null};
  const rawValue=row=>number(row.rawValue??row.value);
  const metadataText=indicator=>[indicator?.name,indicator?.definition,indicator?.formula].filter(Boolean).join(" ").normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase();
  const isDirectIndex=indicator=>/base\s*100|indice|variacion porcentual/.test(metadataText(indicator));

  function calculation(indicator,row){
    const raw=rawValue(row),auxiliary=number(row.aux),factor=FACTORS[indicator?.unitCode];
    if(raw===null)return{value:null,mode:"invalid"};
    if(isDirectIndex(indicator))return{value:number(row.value??raw),mode:"direct-index"};
    if(factor&&auxiliary!==null&&auxiliary!==0){
      const value=raw/auxiliary*factor;
      if(indicator?.unitCode!=="PORCENTAJE"||(value>=0&&value<=100))return{value,mode:"ratio"};
      return{value:number(row.value??raw),mode:"direct-outlier"};
    }
    return{value:number(row.value??raw),mode:"direct"};
  }
  const displayValue=(row,indicator)=>calculation(indicator,row).value;
  const dimensionKey=row=>[row.geoCode,row.geoName,row.subGeo,row.opening,row.level1,row.mode1,row.level2,row.mode2].map(value=>String(value??"")).join("\u241f");

  function aggregate(rows,indicator,{allowAggregate=false}={}){
    if(!rows.length)return null;
    if(rows.length===1)return displayValue(rows[0],indicator);
    if(!allowAggregate)return null;
    const factor=FACTORS[indicator?.unitCode];
    if(factor&&!isDirectIndex(indicator)){
      const numerators=rows.map(rawValue),denominators=rows.map(row=>number(row.aux));
      if(numerators.every(value=>value!==null)&&denominators.every(value=>value!==null)&&denominators.reduce((a,b)=>a+b,0)!==0){
        return numerators.reduce((a,b)=>a+b,0)/denominators.reduce((a,b)=>a+b,0)*factor;
      }
    }
    return null;
  }
  return{FACTORS,number,rawValue,isDirectIndex,calculation,displayValue,dimensionKey,aggregate};
});
