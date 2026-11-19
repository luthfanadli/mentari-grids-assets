import assert from 'node:assert/strict'
import { createHash } from 'node:crypto'
import { readFileSync, readdirSync } from 'node:fs'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'

const directory = fileURLToPath(new URL('../public/data/planning/', import.meta.url))
const expected = JSON.parse(readFileSync(new URL('./expected-planning-audit.json', import.meta.url)))
const catalog = JSON.parse(readFileSync(join(directory, 'catalog.json')))
const kinds = ['generators', 'substations', 'transmission']
assert.deepEqual(readdirSync(directory).sort(), ['catalog.json', ...kinds.map(kind => kind + '.geojson')])
assert.deepEqual(Object.keys(catalog.datasets).sort(), kinds)
assert.equal(catalog.schema_version, 1)
assert.equal(catalog.license, 'https://creativecommons.org/licenses/by-sa/4.0/')
assert.equal(catalog.osm_license, 'https://opendatacommons.org/licenses/odbl/1-0/')

function checkPosition(position) {
  assert.ok(Array.isArray(position) && position.length === 2 && position.every(Number.isFinite),
    'Source coordinates must be finite longitude/latitude pairs')
  assert.ok(Math.abs(position[0]) <= 180 && Math.abs(position[1]) <= 90)
}

function checkLine(coordinates) {
  assert.ok(Array.isArray(coordinates) && coordinates.length >= 2, 'Missing line vertices')
  coordinates.forEach(checkPosition)
  const [x, y] = coordinates[0]
  assert.ok(coordinates.some(([px, py]) => px !== x || py !== y), 'Zero-length planning line')
}

function addCount(counts, value) {
  counts[value] = (counts[value] ?? 0) + 1
}

const ids = new Set(), sources = new Set(), statuses = new Set(), years = new Set()
let unknownYear = false, mapTotal = 0
for (const kind of kinds) {
  const entry = catalog.datasets[kind]
  const name = kind + '.geojson'
  const bytes = readFileSync(join(directory, name))
  assert.equal(entry.url, '/data/planning/' + name)
  assert.equal(bytes.length, entry.bytes, name + ': byte count mismatch')
  assert.equal(createHash('sha256').update(bytes).digest('hex'), entry.sha256, name + ': checksum mismatch')
  for (const [key, value] of Object.entries(expected[kind])) {
    assert.deepEqual(entry[key], value, kind + ': unexpected source audit ' + key)
  }
  const data = JSON.parse(bytes)
  assert.equal(data.type, 'FeatureCollection')
  for (const key of ['attribution', 'license', 'source_url', 'osm_license', 'osm_notice', 'adaptation']) {
    assert.ok(catalog[key])
    assert.equal(data[key], catalog[key], name + ': source credit differs')
  }
  assert.equal(data.features.length, entry.count)
  const perSource = {}, perStatus = {}
  let mapped = 0
  for (const feature of data.features) {
    const p = feature.properties
    assert.equal(feature.type, 'Feature')
    assert.ok(p.id && p.name && p.source && p.status)
    assert.equal(feature.id, 'planning:' + kind + ':' + p.id)
    assert.ok(!ids.has(feature.id), 'Duplicate planning project ID ' + feature.id)
    ids.add(feature.id)
    sources.add(p.source)
    statuses.add(p.status)
    addCount(perSource, p.source)
    addCount(perStatus, p.status)
    if (p.target_cod_year == null) unknownYear = true
    else {
      assert.ok(Number.isInteger(p.target_cod_year))
      years.add(p.target_cod_year)
    }
    const geometry = feature.geometry
    if (geometry === null) continue
    if (kind === 'transmission') {
      assert.notEqual(p.route_status, 'none', 'Cannot display a route flagged as absent')
      assert.ok(['LineString', 'MultiLineString'].includes(geometry.type))
      const lines = geometry.type === 'LineString' ? [geometry.coordinates] : geometry.coordinates
      assert.ok(lines.length > 0)
      lines.forEach(checkLine)
    } else {
      assert.equal(geometry.type, 'Point')
      checkPosition(geometry.coordinates)
    }
    mapped++
  }
  assert.deepEqual(entry.source_counts, perSource)
  assert.deepEqual(entry.statuses, perStatus)
  assert.equal(entry.mapped, mapped)
  assert.equal(entry.count - mapped, Object.values(entry.geometry_issues).reduce((sum, n) => sum + n, 0))
  mapTotal += mapped
}
assert.deepEqual(catalog.filters, {
  sources: [...sources].sort(), statuses: [...statuses].sort(),
  target_years: [...years].sort((a, b) => a - b), unknown_year: unknownYear,
})
console.log(`Planning publication checks passed: ${ids.size.toLocaleString('en-GB')} project records, ${mapTotal.toLocaleString('en-GB')} mapped; three GeoJSONs and catalog.`)
