import { readFileSync, readdirSync, statSync } from 'node:fs'
import { createHash } from 'node:crypto'
import { fileURLToPath } from 'node:url'
import { resolve, join } from 'node:path'
import assert from 'node:assert/strict'

const root = fileURLToPath(new URL('../', import.meta.url))
const directory = resolve(root, 'public/data')
const read = name => JSON.parse(readFileSync(join(directory, name), 'utf8'))
const summary = read('summary.json'), catalog = read('data-catalog.json'), qa = read('qa-report.json')
const files = ['transmission-lines.geojson', 'substations-primary.geojson', 'substations-review.geojson', 'substations-point-candidates.geojson', 'substation-display-points.geojson', 'summary.json', 'data-catalog.json', 'qa-report.json']
assert.deepEqual(readdirSync(directory).sort(), [...files].sort(), 'Only the eight intended data exports may be published')
assert.equal(summary.schema_version, 2)
assert.equal(summary.data_version, catalog.data_version, 'Metadata versions differ')
assert.equal(summary.data_version, qa.data_version, 'QA version differs')
assert.equal(summary.source_sha256, catalog.source_sha256)
assert.equal(summary.source_sha256, qa.source_sha256)
assert.equal(qa.source_unchanged, true)
assert.equal(qa.publication_validation.geometry_errors, 0)
const ids = new Set(), target = new Set([70000, 150000, 275000, 500000])
const polygonIds = new Set(), symbolIds = new Set()
for (const entry of catalog.datasets) {
  const name = entry.url.split('/').pop(), bytes = readFileSync(join(directory, name))
  assert.equal(bytes.length, entry.bytes, `${name}: byte count differs from catalog`)
  assert.equal(createHash('sha256').update(bytes).digest('hex'), entry.sha256, `${name}: checksum mismatch; rerun preprocessing`)
  const data = JSON.parse(bytes)
  assert.equal(data.type, 'FeatureCollection')
  assert.equal(data.license, catalog.license_url)
  if (entry.role === 'inventory') assert.equal(data.features.length, summary.datasets[entry.key].count)
  assert.equal(data.features.length, entry.count)
  for (const feature of data.features) {
    const p = feature.properties
    if (entry.role === 'presentation') {
      assert.equal(p.counts_as_inventory, false)
      assert.equal(p.geometry_role, 'derived_polygon_representative_point')
      assert.equal(p.represented_feature_id, feature.id)
      assert.equal(p.feature_id, feature.id)
      assert.equal(feature.geometry.type, 'Point')
      assert.ok(!symbolIds.has(feature.id)); symbolIds.add(feature.id)
      continue
    }
    assert.equal(feature.id, `${p.source_layer}:${p.source_id}`)
    assert.equal(p.feature_id, feature.id)
    assert.ok(!ids.has(feature.id), `Duplicate ID: ${feature.id}`); ids.add(feature.id)
    assert.equal(p.source_status_verified, false)
    assert.notEqual(p.osm_tag_status, 'conflicting_tags')
    if (entry.key === 'lines') {
      assert.equal(p.asset_type, 'transmission_line')
      assert.ok(['LineString', 'MultiLineString'].includes(feature.geometry.type))
    }
    if (entry.key === 'primary' || entry.key === 'review') {
      assert.equal(p.asset_type, 'substation_polygon')
      assert.ok(['Polygon', 'MultiPolygon'].includes(feature.geometry.type), 'Source points cannot enter polygon inventory')
    }
    if (entry.key === 'lines' || entry.key === 'primary') assert.ok(target.has(p.max_voltage_v))
    if (entry.key === 'primary' || entry.key === 'review') polygonIds.add(feature.id)
    if (entry.key === 'primary') assert.equal(p.substation_type, 'transmission')
    if (entry.key === 'point_candidates') {
      assert.equal(p.asset_type, 'substation_point')
      assert.equal(p.geometry_role, 'original_point')
      assert.equal(p.matching_classification, 'distinct_point_only_candidate')
      assert.equal(p.review_reason, 'point_only_unvalidated')
      assert.equal(feature.geometry.type, 'Point')
    } else if (entry.key === 'review') assert.ok(p.review_reason)
    else assert.equal(p.review_reason, null)
  }
}
assert.deepEqual([...symbolIds].sort(), [...polygonIds].sort(), 'Representative symbols must correspond one-to-one with published polygons')
assert.equal(ids.size, qa.publication_validation.features_validated)
assert.equal(symbolIds.size, summary.substation_presentation.representative_symbol_count)
assert.equal(summary.datasets.point_candidates.count, qa.substation_point_matching.eligible_point_candidates)
assert.equal(Object.values(qa.substation_point_matching.classifications).reduce((sum, n) => sum + n, 0), qa.substation_point_matching.point_count)
function checkAssets(path) {
  for (const entry of readdirSync(path, { withFileTypes: true })) {
    const full = join(path, entry.name)
    if (entry.isDirectory()) checkAssets(full)
    else assert.ok(!/\.(gpkg|pdf|docx?|xlsx?|env)$/i.test(entry.name), `Nonpublic source/reference file found: ${full}`)
  }
}
checkAssets(resolve(root, 'public'))
console.log(`Publication checks passed: ${ids.size.toLocaleString('en-GB')} inventory/review records; ${symbolIds.size} uncounted display symbols; eight files; matching versions, checksums and counts.`)
console.log(`Published GeoJSON bytes: ${catalog.datasets.reduce((n, entry) => n + statSync(join(directory, entry.url.split('/').pop())).size, 0).toLocaleString('en-GB')}`)
