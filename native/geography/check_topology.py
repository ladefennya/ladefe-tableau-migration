import argparse
import json,sys,itertools,hashlib
from pathlib import Path
from osgeo import ogr,osr,gdal
a=argparse.ArgumentParser();a.add_argument('--geometry',type=Path,required=True);a.add_argument('--out',type=Path,required=True);args=a.parse_args()
O=args.out;O.mkdir(parents=True,exist_ok=True);P=args.geometry;j=json.loads(P.read_text());warnings=[]
gdal.PushErrorHandler(lambda typ,no,msg:warnings.append(msg))
src=osr.SpatialReference();src.ImportFromEPSG(4326);src.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
dst=osr.SpatialReference();dst.ImportFromEPSG(6933);dst.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER);tr=osr.CoordinateTransformation(src,dst)
geoms=[];features=[]
for f in j['features']:
 warnings.clear();g=ogr.CreateGeometryFromJson(json.dumps(f['geometry']));valid=g.IsValid();reasons=list(warnings);p=g.Clone();p.AssignSpatialReference(src);p.Transform(tr)
 features.append({'name':f['properties']['nam'],'valid_geos':valid,'diagnostics':reasons,'bbox_lonlat':g.GetEnvelope(),'area_m2_epsg6933':p.GetArea(),'components':g.GetGeometryCount(),'geometry_type':g.GetGeometryName()});geoms.append(p)
overlaps=[];failures=[]
for i,k in itertools.combinations(range(len(geoms)),2):
 warnings.clear()
 try:
  v=geoms[i].Intersection(geoms[k]);area=v.GetArea() if v else 0
  if area>1:overlaps.append({'a':features[i]['name'],'b':features[k]['name'],'intersection_area_m2':area,'both_geometries_valid':features[i]['valid_geos'] and features[k]['valid_geos'],'share_smaller_pct':area/min(features[i]['area_m2_epsg6933'],features[k]['area_m2_epsg6933'])*100})
  if warnings:failures.append({'a':features[i]['name'],'b':features[k]['name'],'diagnostics':list(warnings)})
 except Exception as e:failures.append({'a':features[i]['name'],'b':features[k]['name'],'error':str(e)})
# Presence in the existing geometry only, not an official sovereignty/toponymy validation.
tdf=next((f for f in j['features'] if 'Fuego' in f['properties']['nam']),None)
def polys(g):return g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
malv=[]
for poly in polys(tdf['geometry']):
 pts=[v for r in poly for v in r]
 if any(-62.5<=v[0]<=-57 and -53<=v[1]<=-50 for v in pts):malv.append(poly)
result={'source_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'gdal':gdal.VersionInfo(),'geos':f'{ogr.GetGEOSVersionMajor()}.{ogr.GetGEOSVersionMinor()}.{ogr.GetGEOSVersionMicro()}', 'features':features,'invalid_features':sum(not f['valid_geos'] for f in features),'pair_count':276,'overlaps_larger_than_1m2':overlaps,'intersection_diagnostics':failures,'overlap_pairs_both_valid':sum(x['both_geometries_valid'] for x in overlaps),'tdf_components_intersecting_malvinas_bbox':len(malv),'limitations':['Validity/overlap refer only to simplified file, not authoritative boundary correctness.','EPSG6933 used for numerical area diagnostics; not prescribed display CRS.','1m2 is diagnostic noise threshold, not an acceptable cartographic tolerance.','No source-original overlay was available to quantify simplification drift.']}
(O/'topology_results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print({'invalid':result['invalid_features'],'overlap_pairs':len(overlaps),'intersection_failures':len(failures),'malvinas_bbox_components':len(malv)});print([(f['name'],f['diagnostics']) for f in features if not f['valid_geos']]);print(overlaps[:5])
