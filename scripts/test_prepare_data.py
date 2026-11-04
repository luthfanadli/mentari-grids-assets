import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from prepare_data import (ROOT, TARGET_V, normalize_voltage, parse_voltages, osm_status,
                          polygon_bucket, line_bucket, feature, validate_publication, prepare, write_json)
from shapely.geometry import LineString


class SerializationTests(unittest.TestCase):
    def test_json_bytes_preserve_publication_crlf_on_every_platform(self):
        value = {"label": "Mentari ©", "note": "first\nsecond"}
        expected = {
            True: '{"label":"Mentari ©","note":"first\\nsecond"}\r\n',
            False: '{\r\n  "label": "Mentari ©",\r\n  "note": "first\\nsecond"\r\n}\r\n',
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "export.json"
            for compact, text in expected.items():
                with self.subTest(compact=compact):
                    write_json(path, value, compact=compact)
                    self.assertEqual(path.read_bytes(), text.encode("utf-8"))
                    self.assertEqual(json.loads(path.read_bytes()), value)
                    self.assertFalse(path.with_suffix(".json.tmp").exists())


class ClassificationTests(unittest.TestCase):
    def test_numeric_volts_only(self):
        self.assertEqual(normalize_voltage(150000), 150)
        self.assertEqual(normalize_voltage(150), 0.15)
        for value in (None, float("nan"), float("inf"), 0, -70000, "150000", True):
            self.assertIsNone(normalize_voltage(value))
        self.assertEqual(parse_voltages("500000;150000;invalid;150000;0;nan"), [500, 150])

    def test_status_flags_and_quarantine(self):
        for construction, disused, expected in ((False, False, "not_flagged_in_osm"),
                                               (True, False, "tagged_construction"),
                                               (False, True, "tagged_disused"),
                                               (True, True, "conflicting_tags")):
            self.assertEqual(osm_status(dict(construction=construction, disused=disused)), expected)
        with self.assertRaisesRegex(ValueError, "Malformed boolean"):
            osm_status(dict(construction="false"))

    def test_candidates_and_exact_maximum(self):
        cases = [("transmission", 150000, "primary"), ("transmission", None, "transmission_missing_voltage"),
                 (None, 70000, "high_voltage_unknown_type"),
                 ("distribution", 500000, "high_voltage_distribution_tag"),
                 ("generation", 150000, "polygon_target_other_type"),
                 ("transmission", 115000, "transmission_non_target_voltage"),
                 ("distribution", None, "polygon_outside_selection")]
        for kind, voltage, expected in cases:
            self.assertEqual(polygon_bucket(dict(substation_type=kind, max_voltage=voltage)), expected)
        self.assertEqual(line_bucket(dict(max_voltage=20000, voltages="150000")), "line_20_kv")
        self.assertEqual(line_bucket(dict(max_voltage=None, voltages="150000")), "line_missing_voltage")

    def test_negative_ids_unknowns_fallback_and_geodesic_length(self):
        item = feature(dict(id=-123, name=None, max_voltage=70000, construction=False,
                            geometry=LineString([(110, 0), (111, 0)])), "power_line")
        props = item["properties"]
        self.assertEqual(props["source_id"], "-123")
        self.assertEqual(item["id"], "power_line:-123")
        self.assertTrue(props["display_name_is_fallback"])
        self.assertIn("OSM ID -123", props["display_name"])
        self.assertIsNone(props["circuits"])
        self.assertFalse(props["source_status_verified"])
        self.assertAlmostEqual(props["mapped_geometry_length_km"], 111.31949, places=4)


@unittest.skipUnless((ROOT / "data/raw/IDN.gpkg").is_file(), "Real source GeoPackage not present")
class RealSourceTests(unittest.TestCase):
    def test_source_version_mismatch_reports_exact_difference_without_publishing(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            with patch('prepare_data.sha256', return_value='changed-source-fingerprint'):
                with self.assertRaisesRegex(ValueError, 'Source-version mismatch'):
                    prepare(ROOT / 'data/raw/IDN.gpkg', base / 'public', base / 'qa')
            self.assertFalse((base / 'public').exists())
            qa = json.loads((base / 'qa/qa-report.json').read_text(encoding='utf-8'))
            self.assertEqual(qa['audit_comparison']['differences'], [{
                'metric': 'source_sha256',
                'expected': '6ea22caaae9ef62a32e91d65b79cf972d4aaedeec372d58f49af2f71c22307ba',
                'actual': 'changed-source-fingerprint',
            }])

    def test_pipeline_against_real_source_and_deterministic_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            first = prepare(ROOT / "data/raw/IDN.gpkg", base / "a", base / "qa-a")
            second = prepare(ROOT / "data/raw/IDN.gpkg", base / "b", base / "qa-b")
            self.assertEqual(first["audit_differences"], [])
            self.assertEqual(first["counts"], {"lines": 4374, "primary": 622, "review": 448, "point_candidates": 32, "power_plants": 643})
            self.assertEqual(first, second)
            for path in (base / "a").iterdir():
                self.assertEqual(path.read_bytes(), (base / "b" / path.name).read_bytes(), path.name)
            for name in ('substation-matching-report.json', 'substation-matching-report.csv'):
                self.assertEqual((base / 'qa-a' / name).read_bytes(), (base / 'qa-b' / name).read_bytes(), name)


@unittest.skipUnless((ROOT / "public/data/summary.json").is_file(), "Run preprocessing first")
class PublicationTests(unittest.TestCase):
    def test_real_exports_match_audit_and_contract(self):
        expected = json.loads((ROOT / "scripts/expected-audit.json").read_text())
        qa = json.loads((ROOT / "public/data/qa-report.json").read_text(encoding="utf-8"))
        for key, value in expected.items():
            self.assertEqual(qa["audit_actual"][key], value, key)
        datasets = {key: json.loads((ROOT / "public/data" / filename).read_text(encoding="utf-8"))["features"]
                    for key, filename in (("lines", "transmission-lines.geojson"), ("primary", "substations-primary.geojson"), ("review", "substations-review.geojson"))}
        self.assertEqual(validate_publication(datasets)["features_validated"], 5444)
        for item in datasets["lines"]:
            self.assertIn(item["properties"]["max_voltage_v"], TARGET_V)
        self.assertTrue(qa["source_unchanged"])
        self.assertTrue(qa["audit_comparison"]["matches"])


if __name__ == "__main__":
    unittest.main()
