import argparse
import json,hashlib
from pathlib import Path
from osgeo import ogr,osr,gdal
a=argparse.ArgumentParser();a.add_argument('--source',type=Path,required=True);a.add_argument('--display',type=Path,required=True);a.add_argument('--out',type=Path,required=True);args=a.parse_args()
O=args.out;O.mkdir(parents=True,exist_ok=True);P=args.source;raw=json.loads(P.read_text());j=json.loads(args.display.read_text());display={x['properties']['nam']:x for x in j['features']};results=[];errors=[]
gdal.PushErrorHandler(lambda typ,no,msg:errors.append(msg));s=osr.SpatialReference();s.ImportFromEPSG(4326);s.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER);p=osr.SpatialReference();p.ImportFromEPSG(6933);p.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER);tr=osr.CoordinateTransformation(s,p)
for f in raw['features']:
 name=f['properties']['nam'];errors.clear();g=ogr.CreateGeometryFromJson(json.dumps(f['geometry']));valid=g.IsValid();diagnostics=list(errors);current=ogr.CreateGeometryFromJson(json.dumps(display[name]['geometry']));cv=current.IsValid();g.AssignSpatialReference(s);current.AssignSpatialReference(s)
 # Compare in common clipped footprint; simple bbox is *analysis* frame, not new territorial policy.
 clip=ogr.CreateGeometryFromWkt('POLYGON((-74.5 -56,-52.5 -56,-52.5 -20,-74.5 -20,-74.5 -56))');clipped=g.Intersection(clip);clip_valid=clipped.IsValid() if clipped else None
 orig_measure=clipped.Clone() if clipped else None;cur_measure=current.Clone();cur_measure.Transform(tr)
 if orig_measure:orig_measure.Transform(tr)
 original_area=orig_measure.GetArea() if orig_measure else None;current_area=cur_measure.GetArea()
 results.append({'name':name,'source_in1':f['properties'].get('in1'),'source_geometry_valid':valid,'source_validity_diagnostics':diagnostics,'current_simplified_valid':cv,'source_clipped_valid':clip_valid,'source_clipped_area_m2':original_area,'current_simplified_area_m2':current_area,'relative_area_difference_pct':(current_area-original_area)/original_area*100 if original_area else None,'source_envelope':g.GetEnvelope()});print(name,'source',valid,'current',cv,flush=True)
result={'source_file_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'source_bytes':P.stat().st_size,'common_comparison_frame':[-74.5,-56,-52.5,-20],'source_valid_count':sum(r['source_geometry_valid'] for r in results),'current_valid_count':sum(r['current_simplified_valid'] for r in results),'features':results,'cautions':['Area comparisons are diagnostics of the two files within the comparison frame, not official areas.','Intersection of invalid source or current geometries is not a certified area result.','A fresh WFS response is not a byte-identical reconstruction of the historical source download.']};(O/'source_geometry_comparison.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print('DONE',result['source_valid_count'],result['current_valid_count'])
