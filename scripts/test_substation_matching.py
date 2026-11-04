import json
import hashlib
import unittest

import geopandas as gpd
from shapely.geometry import Point, Polygon

from prepare_data import ROOT, TARGET_V, feature, validate_publication
from substation_matching import pair_evidence, classify_pairs, eligibility, name_tokens, representative_features, match_substations


def record(id=1, name=None, **values):
    return dict(id=id, name=name, ref=None, operator=None, max_voltage=None, substation_type=None, **values)


class MatchingRulesTests(unittest.TestCase):
    def test_point_cannot_enter_primary_even_with_voltage_and_transmission_tags(self):
        point = feature(dict(id=1, name='GI test', max_voltage=150000, substation_type='transmission', construction=False, geometry=Point(110, 0)), 'power_substation_point')
        with self.assertRaisesRegex(ValueError, 'require polygon geometry'):
            validate_publication({'primary': [point]})

    def test_intersection_alone_and_generic_names_remain_uncertain(self):
        for name in (None, 'PLN', 'Gardu Induk', 'Gardu Listrik'):
            pair = pair_evidence(record(1, name), record(2, name), 0, True)
            self.assertFalse(pair['supported'])
            self.assertEqual(classify_pairs([pair])[0], 'uncertain')

    def test_distinctive_names_support_correspondence_without_voltage_inheritance(self):
        left, right = record(1, 'PLN Gardu induk 150 kV Sandai'), record(2, 'Gardu Induk Sandai')
        right['max_voltage'] = 150000
        pair = pair_evidence(left, right, 0, True)
        self.assertEqual(classify_pairs([pair])[:2], ('matched', 'power_substation_polygon:2'))
        self.assertIsNone(left['max_voltage'])
        self.assertEqual(name_tokens('Gardu Induk PLN Bukit Kemuning'), ['bukit', 'kemuning'])
        self.assertNotEqual(name_tokens('PK 276'), name_tokens('PK 277'))
        self.assertEqual(name_tokens('GI 150kV Sandai'), ['sandai'])
        left['name'] = right['name'] = None
        left['ref'] = right['ref'] = 'SND01'
        self.assertEqual(classify_pairs([pair_evidence(left, right, 85, False)])[0], 'matched')
        left['ref'] = right['ref'] = 'GARDU PLN'
        self.assertEqual(classify_pairs([pair_evidence(left, right, 85, False)])[0], 'uncertain')

    def test_conflicts_ambiguity_and_numeric_ids_do_not_certify_duplicates(self):
        left, right = record(1, 'GI Sandai'), record(2, 'GI Sandai')
        left['operator'], right['operator'] = 'EDF', 'PLN'
        self.assertEqual(classify_pairs([pair_evidence(left, right, 0, True)])[0], 'uncertain')
        pair = pair_evidence(record(1, 'GI Sandai'), record(2, 'GI Sandai'), 20, False)
        other = pair_evidence(record(1, 'GI Sandai'), record(3, None), 60, False)
        self.assertEqual(classify_pairs([pair, other])[0], 'uncertain')
        same_id = pair_evidence(record(-3, None), record(-3, None), 10000, False)
        self.assertFalse(same_id['osm_element_identity_verified'])
        self.assertEqual(classify_pairs([same_id])[0], 'uncertain')
        different_status = pair_evidence(record(1, 'GI Sandai', construction=False), record(2, 'GI Sandai', construction=True), 0, True)
        self.assertEqual(classify_pairs([different_status])[0], 'uncertain')

    def test_proximity_boundaries_and_candidate_eligibility(self):
        near = pair_evidence(record(), record(2), 500, False)
        far = pair_evidence(record(), record(2), 500.01, False)
        self.assertEqual(classify_pairs([near])[0], 'uncertain')
        self.assertEqual(classify_pairs([far])[0], 'distinct_point_only_candidate')
        candidate = record(1, 'GI Hittu')
        self.assertTrue(eligibility(candidate, 'distinct_point_only_candidate', TARGET_V)[0])
        for kind in ('distribution', 'generation', 'minor_distribution'):
            candidate['substation_type'] = kind
            self.assertFalse(eligibility(candidate, 'distinct_point_only_candidate', TARGET_V)[0])
        self.assertFalse(eligibility(record(1, 'Kantor PLN'), 'distinct_point_only_candidate', TARGET_V)[0])
        self.assertFalse(eligibility(record(), 'matched', TARGET_V)[0])

    def test_representative_point_stays_in_concave_polygon_and_reuses_parent_id(self):
        polygon = Polygon([(0, 0), (4, 0), (4, 1), (1, 1), (1, 3), (4, 3), (4, 4), (0, 4), (0, 0)])
        self.assertFalse(polygon.covers(polygon.centroid))
        feature = {'id': 'power_substation_polygon:-1', 'properties': {'source_id': '-1'}, 'geometry': polygon.__geo_interface__}
        [representative] = representative_features({'primary': [feature], 'review': []})
        self.assertTrue(polygon.covers(Point(representative['geometry']['coordinates'])))
        self.assertEqual(representative['id'], feature['id'])
        self.assertFalse(representative['properties']['counts_as_inventory'])


@unittest.skipUnless((ROOT / 'data/raw/IDN.gpkg').is_file(), 'Real source missing')
class RealMatchingTests(unittest.TestCase):
    def test_all_real_source_pairs_are_audited_and_classifications_are_exhaustive(self):
        points = gpd.read_file(ROOT / 'data/raw/IDN.gpkg', layer='power_substation_point')
        polygons = gpd.read_file(ROOT / 'data/raw/IDN.gpkg', layer='power_substation_polygon')
        report = match_substations(points, polygons, 'test-source', TARGET_V)
        self.assertEqual(report['pair_comparisons'], 68 * 2753)
        self.assertEqual(sum(report['classifications'].values()), 68)
        self.assertEqual(report['classifications'], {'matched': 2, 'uncertain': 25, 'distinct_point_only_candidate': 41})
        self.assertEqual(report['eligible_point_candidates'], 32)
        self.assertTrue(all(row['compared_polygon_count'] == 2753 for row in report['records']))
        self.assertEqual(sum(row['intersecting_polygon_count'] for row in report['records']), 6)
        self.assertTrue(all(row['original_attributes']['max_voltage'] is None for row in report['records']))
        self.assertTrue(all(not row['duplicate_identity_verified'] for row in report['records']))
        self.assertEqual(report['records'], sorted(report['records'], key=lambda row: row['source_id']))
        matched = [row for row in report['records'] if row['classification'] == 'matched']
        self.assertTrue(all(any(e['supported'] for e in row['polygon_evidence']) for row in matched))
        self.assertTrue(all(not row['eligible_for_point_candidate_layer'] for row in report['records'] if row['classification'] != 'distinct_point_only_candidate'))

    def test_original_exports_and_point_geometry_are_preserved_and_symbols_are_uncounted(self):
        directory = ROOT / 'public/data'
        preserved = {
            'transmission-lines.geojson': '1eed102bced3ca67d00660f764ee83eb608ba32239f5ba4e11ca06f6b3858c98',
            'substations-primary.geojson': '930c23abd342797b27fd71435a3c7d32c5b838f06619206a7159df8bfaf6613f',
            'substations-review.geojson': 'e14432b41e7ce80def0f8edb3c5e0ac25b80ef6860129096cee071631522f038',
        }
        for name, expected in preserved.items():
            self.assertEqual(hashlib.sha256((directory / name).read_bytes()).hexdigest(), expected, name)
        from shapely.geometry import shape
        points = gpd.read_file(ROOT / 'data/raw/IDN.gpkg', layer='power_substation_point')
        originals = {str(int(row['id'])): row['geometry'] for row in points.to_dict('records')}
        candidates = json.loads((directory / 'substations-point-candidates.geojson').read_text(encoding='utf-8'))['features']
        self.assertEqual(len(candidates), 32)
        for feature in candidates:
            p = feature['properties']
            self.assertEqual(feature['geometry']['coordinates'], list(originals[p['source_id']].coords[0]))
            self.assertIsNone(p['max_voltage_v'])
            self.assertIsNone(p['max_voltage_kv'])
            self.assertEqual(p['matching_classification'], 'distinct_point_only_candidate')
        polygons = {}
        for filename in ('substations-primary.geojson', 'substations-review.geojson'):
            polygons.update({f['id']: shape(f['geometry']) for f in json.loads((directory / filename).read_text(encoding='utf-8'))['features']})
        symbols = json.loads((directory / 'substation-display-points.geojson').read_text(encoding='utf-8'))['features']
        self.assertEqual(len(symbols), 1070)
        self.assertEqual({f['id'] for f in symbols}, set(polygons))
        for feature in symbols:
            self.assertTrue(polygons[feature['id']].covers(shape(feature['geometry'])))
            self.assertFalse(feature['properties']['counts_as_inventory'])


if __name__ == '__main__':
    unittest.main()
