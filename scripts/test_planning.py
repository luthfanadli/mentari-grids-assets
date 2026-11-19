import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from shapely.geometry import shape

from prepare_planning import EXPECTED, FIELDS, ROOT, build_collection, prepare


def source_row(project_id, geometry, **attributes):
    return {
        "type": "Feature", "geometry": geometry,
        "properties": {"id": project_id, "name": "Fixture", "source": "RUPTL 2025-2034",
                       "status": "Planned", **attributes},
    }


class PlanningTests(unittest.TestCase):
    def test_unmapped_projects_are_queryable_with_the_original_route_tags(self):
        route = {"type": "LineString", "coordinates": [[100, 1], [100.24, 2]]}
        degenerate = {"type": "LineString", "coordinates": [[101, 1], [101, 1]]}
        rows = [source_row("001", route, route_status="none"),
                source_row("002", degenerate, route_status="drawn"),
                source_row("003", route, route_status="schematic", internal_review_note="private")]
        collection, metrics, withheld = build_collection("transmission", {"type": "FeatureCollection", "features": rows})
        self.assertEqual([row["geometry"] for row in collection["features"]], [None, None, route])
        self.assertEqual([row["properties"]["route_status"] for row in collection["features"]],
                         ["none", "drawn", "schematic"])
        self.assertNotIn("internal_review_note", collection["features"][2]["properties"])
        self.assertEqual(metrics["mapped"], 1)
        self.assertEqual(withheld, [{"source_id": "001", "reason": "route_status_none"},
                                    {"source_id": "002", "reason": "invalid_geometry"}])

    def test_duplicate_source_ids_fail_and_shared_sites_stay_separate(self):
        point = {"type": "Point", "coordinates": [103.123456789, 2]}
        one = source_row("job-1", point, site_id="same-site")
        two = source_row("job-2", point, site_id="same-site")
        collection, metrics, _ = build_collection("substations", {"type": "FeatureCollection", "features": [one, two]})
        self.assertEqual(metrics["mapped"], 2)
        self.assertEqual([row["id"] for row in collection["features"]],
                         ["planning:substations:job-1", "planning:substations:job-2"])
        with self.assertRaisesRegex(ValueError, "duplicate source ID"):
            build_collection("substations", {"type": "FeatureCollection", "features": [one, one]})

    def test_source_change_leaves_all_current_publications_intact(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            inputs, publication, qa = base / "input", base / "pub", base / "qa"
            inputs.mkdir()
            publication.mkdir()
            for kind in FIELDS:
                (inputs / f"ruptl_{kind}.geojson").write_text('{"type":"FeatureCollection","features":[]}')
            (publication / "transmission.geojson").write_bytes(b"prior publication")
            with self.assertRaisesRegex(ValueError, "Planning source-version mismatch"):
                prepare(inputs, publication, qa)
            self.assertEqual([p.name for p in publication.iterdir()], ["transmission.geojson"])
            self.assertEqual((publication / "transmission.geojson").read_bytes(), b"prior publication")
            report = json.loads((qa / "planning-qa.json").read_bytes())
            fingerprint = next(row for row in report["audit_differences"]
                               if row["dataset"] == "transmission" and row["metric"] == "source_sha256")
            self.assertEqual(fingerprint["expected"], json.loads(EXPECTED.read_bytes())["transmission"]["source_sha256"])
            self.assertNotEqual(fingerprint["actual"], fingerprint["expected"])

    @unittest.skipUnless(all((ROOT / f"data/raw/ruptl_{kind}.geojson").is_file() for kind in FIELDS),
                         "Supplied planning GeoJSONs are absent")
    def test_real_sources_keep_every_row_and_original_usable_coordinates(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            output = base / "planning"
            catalog = prepare(ROOT / "data/raw", output, base / "qa")
            for kind, entry in catalog["datasets"].items():
                source = json.loads((ROOT / "data/raw" / entry["input"]).read_bytes())["features"]
                exported = json.loads((output / f"{kind}.geojson").read_bytes())["features"]
                by_id = {f["properties"]["id"]: f for f in exported}
                self.assertEqual(len(source), len(exported))
                for row in source:
                    props = row["properties"]
                    item = by_id[props["id"]]
                    self.assertEqual(item["properties"], props)
                    is_mapped = shape(row["geometry"]).is_valid and props.get("route_status") != "none"
                    self.assertEqual(item["geometry"], row["geometry"] if is_mapped else None)
            self.assertTrue(catalog["filters"]["unknown_year"])
            self.assertIn(2045, catalog["filters"]["target_years"])
            qa = json.loads((base / "qa/planning-qa.json").read_bytes())
            self.assertTrue(qa["source_unchanged"])
            self.assertEqual(qa["audit_differences"], [])
            if sys.platform == "win32":
                # Generated files must inherit access from the project directory.
                # An atomic move from a private temp directory preserves its ACL.
                result = subprocess.run([
                    "powershell.exe", "-NoProfile", "-NonInteractive", "-Command",
                    "$directory = [Console]::In.ReadToEnd(); "
                    "@(Get-ChildItem -LiteralPath $directory -File | ForEach-Object { "
                    "(Get-Acl -LiteralPath $_.FullName).AreAccessRulesProtected "
                    "}) | ConvertTo-Json -Compress",
                ], input=str(output.resolve()), text=True, capture_output=True, check=True)
                self.assertEqual(json.loads(result.stdout), [False] * 4,
                                 "Published planning files must retain inherited access permissions")


if __name__ == "__main__":
    unittest.main()
