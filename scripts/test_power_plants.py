import json
import unittest

import geopandas as gpd
import shapely
from shapely.geometry import Polygon, Point, shape
from prepare_data import ROOT, feature, validate_publication, scalar


class PlantFeatureTests(unittest.TestCase):
    def test_source_attributes_precision_and_unknown_units_are_preserved(self):
        polygon = Polygon([(110.12345678912, -7), (110.2, -7), (110.2, -7.1), (110.12345678912, -7)])
        item = feature(dict(id=-8, name=None, construction=True, source='solar', method='photovoltaic',
                            output=200000.0, start_date='~1995', geometry=polygon), 'power_plant')
        p = item['properties']
        self.assertEqual(item['id'], 'power_plant:-8')
        self.assertIn('Unnamed power plant', p['display_name'])
        self.assertEqual(p['asset_type'], 'power_plant')
        self.assertEqual(p['plant_output_raw'], 200000.0)
        self.assertIsNone(p['plant_output_unit'])
        self.assertIsNone(p['max_voltage_kv'])
        self.assertIsNone(p['disused'])
        self.assertEqual(p['plant_start_date_raw'], '~1995')
        self.assertEqual(p['osm_tag_status'], 'tagged_construction')
        self.assertTrue(shapely.equals_exact(shape(item['geometry']), shapely.orient_polygons(polygon), 0))
        self.assertTrue(shape(item['geometry']).covers(Point(p['plant_representative_point'])))
        self.assertEqual(validate_publication({'power_plants': [item]})['features_validated'], 1)
        with self.assertRaises(ValueError):
            validate_publication({'primary': [item]})

    def test_invalid_output_or_inferred_unit_is_rejected(self):
        record = dict(id=1, name='Fixture', construction=False, geometry=Polygon([(110, -7), (111, -7), (111, -8), (110, -7)]))
        for output in (-1, float('inf'), '200 MW', True):
            with self.subTest(output=output), self.assertRaises(ValueError):
                feature({**record, 'output': output}, 'power_plant')
        item = feature(record, 'power_plant')
        item['properties']['plant_output_unit'] = 'MW'
        with self.assertRaisesRegex(ValueError, 'must not be inferred'):
            validate_publication({'power_plants': [item]})


@unittest.skipUnless((ROOT / 'public/data/power-plants.geojson').is_file() and (ROOT / 'data/raw/IDN.gpkg').is_file(), 'Run real-source power-plant preprocessing first')
class PlantPublicationTests(unittest.TestCase):
    def test_every_plant_matches_original_geometry_and_source_attributes(self):
        frame = gpd.read_file(ROOT / 'data/raw/IDN.gpkg', layer='power_plant')
        originals = {str(int(r['id'])): r for r in frame.to_dict('records')}
        data = json.loads((ROOT / 'public/data/power-plants.geojson').read_bytes())
        self.assertEqual(len(data['features']), 643)
        self.assertEqual({f['properties']['source_id'] for f in data['features']}, set(originals))
        for item in data['features']:
            p = item['properties']; raw = originals[p['source_id']]
            for key, source in (('source', 'source'), ('method', 'method'), ('output_raw', 'output'), ('start_date_raw', 'start_date'), ('name_en', 'name_en'), ('description', 'description'), ('wikidata', 'wikidata')):
                self.assertEqual(p['plant_' + key], scalar(raw[source]))
            self.assertTrue(shapely.equals_exact(shape(item['geometry']), shapely.orient_polygons(raw['geometry']), 0))
            self.assertTrue(shape(item['geometry']).covers(Point(p['plant_representative_point'])))
            self.assertIsNone(p['plant_output_unit']); self.assertIsNone(p['max_voltage_v'])
            self.assertFalse(p['source_status_verified'])
        self.assertEqual(sum(f['properties']['construction'] for f in data['features']), 10)
        self.assertEqual(validate_publication({'power_plants': data['features']})['geometry_errors'], 0)


if __name__ == '__main__':
    unittest.main()
