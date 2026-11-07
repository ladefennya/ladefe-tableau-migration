import argparse
import json
from pathlib import Path
from osgeo import ogr,osr,gdal
a=argparse.ArgumentParser();a.add_argument('--source',type=Path,required=True);a.add_argument('--display',type=Path,required=True);a.add_argument('--out',type=Path,required=True);args=a.parse_args()
O=args.out;O.mkdir(parents=True,exist_ok=True);j=json.loads(args.source.read_text());c=json.loads(args.display.read_text());original={x['properties']['nam']:x for x in j['features']};current={x['properties']['nam']:x for x in c['features']};src=osr.SpatialReference();src.ImportFromEPSG(4326);src.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER);dst=osr.SpatialReference();dst.ImportFromEPSG(6933);dst.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER);tr=osr.CoordinateTransformation(src,dst);rs=[]
for names in [('Ciudad Autónoma de Buenos Aires','Buenos Aires'),('San Luis','Córdoba'),('San Luis','Mendoza')]:
 out={'pair':names}
 for label,data in [('original',original),('simplified',current)]:
  gs=[ogr.CreateGeometryFromJson(json.dumps(data[n]['geometry'])) for n in names];valid=[g.IsValid() for g in gs]
  for g in gs:g.AssignSpatialReference(src);g.Transform(tr)
  inter=gs[0].Intersection(gs[1]);out[label]={'valid':valid,'area_a_km2':gs[0].GetArea()/1e6,'intersection_km2':inter.GetArea()/1e6 if inter else None,'intersection_area_caution':not all(valid)}
 rs.append(out)
(O/'boundary_case_comparisons.json').write_text(json.dumps(rs,ensure_ascii=False,indent=2));print(json.dumps(rs,ensure_ascii=False,indent=2))
