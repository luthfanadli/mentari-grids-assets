"""Build the small-scale regional map behind OpenStreetMap tiles.

Run with the repository's GIS environment. Supply the QGIS ``world_map.gpkg``
(resources/data, QGIS 3.44.15) and the two zipped Natural Earth 1:50m physical
label layers. The latter are label areas v5.0.0 and marine areas v5.1.0 at
https://www.naturalearthdata.com/downloads/50m-physical-vectors/50m-physical-labels/ .
QGIS documents the 1:10m land source at
https://github.com/qgis/QGIS/blob/release-3_44/resources/data/README_world_map.md .
All three inputs derive from public-domain Natural Earth cartography.

Example: python scripts/prepare_basemap.py world_map.gpkg \
ne_50m_geography_regions_polys.zip ne_50m_geography_marine_polys.zip
"""
import argparse
import json
from pathlib import Path

import pyogrio
import shapely
from shapely.geometry import shape


EXTENT = (66, -48, 172, 50)
DETAIL_EXTENT = shapely.box(93, -12, 143, 8)
DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / 'public/basemap/regional-context.geojson'


def read_frame(path, **kwargs):
    data = pyogrio.read_dataframe(path, bbox=EXTENT, **kwargs)
    if data.crs.to_epsg() != 4326:
        raise ValueError(f'Expected WGS 84 coordinates in {path}')
    return data


def point_label(name, point, kind, priority, detail=False):
    return {
        'type': 'Feature',
        'properties': {'label': name, 'kind': kind, 'priority': priority, 'detail': detail},
        'geometry': {'type': 'Point', 'coordinates': [round(point.x, 3), round(point.y, 3)]},
    }


def make_basemap(countries, regions, marine):
    bounds = shapely.box(*EXTENT)
    land = read_frame(countries, layer='countries', columns=['NAME', 'ISO_A3'])
    clipped = shapely.intersection(land.geometry, bounds)
    features = []
    # Dissolve country boundaries before generalizing the coast. Country names and
    # physical labels are cartographic context, independent of the asset records.
    for polygon in shapely.get_parts(shapely.union_all(clipped)):
        if polygon.geom_type != 'Polygon' or polygon.area < 0.002:
            continue
        tolerance = 0.019 if polygon.intersects(DETAIL_EXTENT) else 0.065
        simple = shapely.orient_polygons(shapely.set_precision(polygon.simplify(tolerance), 0.001))
        for part in shapely.get_parts(simple):
            if part.is_empty:
                continue
            rings = [part.exterior, *part.interiors]
            coordinates = [[[round(x, 3), round(y, 3)] for x, y in ring.coords] for ring in rings]
            features.append({
                'type': 'Feature', 'properties': {},
                'geometry': {'type': 'Polygon', 'coordinates': coordinates},
            })

    # Keep a country label inside its largest visible land area. The islands
    # in the Indonesian archipelago have individual physical labels below.
    for name, code, area in zip(land.NAME, land.ISO_A3, clipped):
        if not isinstance(name, str) or code == 'IDN' or area.area < 0.5:
            continue
        largest = max(shapely.get_parts(area), key=lambda part: part.area)
        features.append(point_label(name, largest.representative_point(), 'country', 6, area.area < 5))

    for source, kind in ((regions, 'island'), (marine, 'water')):
        labels = read_frame(source)
        labels.columns = labels.columns.str.lower()
        for row in labels.itertuples():
            if kind == 'island' and row.featurecla.lower() != 'island':
                continue
            if kind == 'water' and row.featurecla.lower() not in {'ocean', 'sea', 'bay', 'gulf', 'strait'}:
                continue
            anchor = row.geometry.representative_point()
            if bounds.contains(anchor):
                rank = int(row.scalerank)
                label = row.name_en if isinstance(row.name_en, str) else row.name
                features.append(point_label(label, anchor, kind, rank, rank >= 4))

    for feature in features:
        geometry = shape(feature['geometry'])
        if geometry.is_empty or not geometry.is_valid:
            raise ValueError('Generated invalid cartographic geometry')
    return {
        'type': 'FeatureCollection', 'attribution': 'Made with Natural Earth',
        'license': 'https://www.naturalearthdata.com/about/terms-of-use/', 'features': features,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for name in ('countries', 'regions', 'marine'):
        parser.add_argument(name, type=Path)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    collection = make_basemap(args.countries, args.regions, args.marine)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(json.dumps(collection, ensure_ascii=False, separators=(',', ':')).encode('utf-8'))
