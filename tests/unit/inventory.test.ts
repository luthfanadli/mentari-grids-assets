import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { defaultFilters, filterAssets, selectionCounts, featureBounds } from '../../src/utils/filterAssets.ts'
import { formatValue, formatVoltage } from '../../src/utils/formatAssets.ts'
import { createAssetRepository } from '../../src/services/assetData.ts'
import { selectedDisplayPoints, renderedRecordCount, selectedMapLegend } from '../../src/utils/substationPresentation.ts'
import type { AssetCollection, InventorySummary, DisplayPointCollection, AssetFeature } from '../../src/types/assets.ts'

const read = (filename: string) => JSON.parse(readFileSync(new URL(`../../public/data/${filename}`, import.meta.url), 'utf8'))
const lines = read('transmission-lines.geojson') as AssetCollection
const primary = read('substations-primary.geojson') as AssetCollection
const review = read('substations-review.geojson') as AssetCollection
const points = read('substations-point-candidates.geojson') as AssetCollection
const symbols = read('substation-display-points.geojson') as DisplayPointCollection
const summary = read('summary.json') as InventorySummary
const all = [...lines.features, ...primary.features, ...review.features, ...points.features]

test('actual export counts and default selection match the generated summary', () => {
  assert.equal(lines.features.length, summary.datasets.lines.count)
  assert.equal(primary.features.length, summary.datasets.primary.count)
  assert.equal(review.features.length, summary.datasets.review.count)
  assert.deepEqual(selectionCounts(filterAssets(all, defaultFilters())), { ...summary.default_selection, total: 4966 })
})
test('optional source flags add exactly 25 construction lines, one polygon and four disused lines', () => {
  const filters = defaultFilters()
  filters.statuses = ['tagged_construction']
  assert.deepEqual(selectionCounts(filterAssets(all, filters)), { lines: 25, primary: 1, review: 0, points: 0, total: 26 })
  filters.statuses = ['tagged_disused']
  assert.deepEqual(selectionCounts(filterAssets(all, filters)), { lines: 4, primary: 0, review: 0, points: 0, total: 4 })
  filters.statuses = ['not_flagged_in_osm', 'tagged_construction', 'tagged_disused']
  assert.equal(filterAssets(all, filters).length, lines.features.length + primary.features.length)
})
test('review is independent from primary, unknown voltages remain explicit and all reasons are disjoint', () => {
  const filters = defaultFilters()
  filters.review = true; filters.lines = false; filters.primary = false
  assert.equal(filterAssets(all, filters).length, 448)
  filters.unknownVoltage = false
  assert.equal(filterAssets(all, filters).length, 411)
  filters.voltages = []; filters.unknownVoltage = true
  assert.equal(filterAssets(all, filters).length, 37)
  assert.ok(filterAssets(all, filters).every(f => f.properties.review_reason === 'transmission_missing_voltage'))
  assert.equal(new Set(all.map(f => f.properties.feature_id)).size, all.length)
})
test('voltage filtering uses maximum value only, once per feature', () => {
  const filters = defaultFilters(); filters.voltages = [500]
  const result = filterAssets(all, filters)
  assert.ok(result.length > 0)
  assert.ok(result.every(f => f.properties.max_voltage_v === 500000 && f.properties.max_voltage_kv === 500))
  filters.voltages = []
  assert.equal(filterAssets(all, filters).length, 0)
})
test('search preserves negative IDs and supports name, reference and operator case-insensitively', () => {
  const filters = defaultFilters(); filters.query = '-18678451'
  const [pedan] = filterAssets(all, filters)
  assert.equal(pedan?.properties.name, 'GITET Pedan')
  for (const query of ['gitet pedan', 'PDN', 'perusahaan listrik negara']) {
    filters.query = `  ${query.toUpperCase()}  `
    assert.ok(filterAssets(all, filters).some(f => f.properties.feature_id === pedan?.properties.feature_id))
  }
  filters.query = 'not a real mapped asset xyz'
  assert.equal(filterAssets(all, filters).length, 0)
})
test('fallback labels, missing values, geodesic values and bounds retain their meaning', () => {
  const unnamed = lines.features.find(f => f.properties.name === null)!
  assert.ok(unnamed.properties.display_name_is_fallback)
  assert.match(unnamed.properties.display_name, /Unnamed line.*OSM ID/)
  assert.equal(formatValue(null), 'Not available'); assert.equal(formatValue(0), '0')
  assert.equal(formatVoltage(null), 'Not available'); assert.equal(formatVoltage(150), '150 kV')
  assert.equal(featureBounds([]), null)
  const bounds = featureBounds(all)!
  assert.ok(bounds[0] > 90 && bounds[2] < 142 && bounds[1] > -12 && bounds[3] < 7)
  assert.ok(lines.features.every(f => f.properties.mapped_geometry_length_km! > 0))
})
test('repository fetches base once and does not request review until explicitly enabled', async () => {
  const calls: string[] = []
  const fetcher = (async (url: string) => {
    calls.push(url)
    const filename = url.split('/').pop()!
    return new Response(JSON.stringify(read(filename)), { headers: { 'Content-Type': 'application/json' } })
  }) as typeof fetch
  const repo = createAssetRepository(fetcher, '/')
  await repo.loadBase(); await repo.loadBase()
  assert.equal(calls.length, 4); assert.ok(!calls.some(c => c.includes('review') || c.includes('point-candidates')))
  await repo.loadReview(); await repo.loadReview()
  assert.equal(calls.filter(c => c.includes('review')).length, 1)
  await repo.loadPointCandidates(); await repo.loadPointCandidates()
  assert.equal(calls.filter(c => c.includes('point-candidates')).length, 1)
})

test('point-only candidates stay separate from both polygon groups and retain unknown voltage', () => {
  const filters = defaultFilters()
  filters.pointCandidates = true
  assert.deepEqual(selectionCounts(filterAssets(all, filters)), { lines: 4345, primary: 621, review: 0, points: 32, total: 4998 })
  filters.lines = false; filters.primary = false
  assert.equal(filterAssets(all, filters).length, summary.datasets.point_candidates.count)
  assert.ok(filterAssets(all, filters).every(feature => feature.properties.max_voltage_v === null && feature.properties.max_voltage_kv === null))
  filters.unknownVoltage = false
  assert.equal(filterAssets(all, filters).length, 0)
  const pointIds = new Set(points.features.map(feature => feature.properties.source_id))
  for (const heldId of ['14305665334', '7973241708', '11078010994', '11078010995', '12730004982', '4145890616']) assert.ok(!pointIds.has(heldId))
})

test('representative symbols follow parent filters and never inflate inventory or viewport counts', () => {
  const filtered = filterAssets(all, defaultFilters())
  const selected = selectedDisplayPoints(symbols, filtered)
  assert.equal(selected.features.length, 621)
  assert.ok(selected.features.every(symbol => symbol.properties.counts_as_inventory === false))
  const original = primary.features[0]!
  const symbol = symbols.features.find(f => f.id === original.id)!
  const display = { ...symbol, properties: { ...original.properties, counts_as_inventory: false as const } } as AssetFeature
  assert.deepEqual(selectionCounts([original, original, display]), { lines: 0, primary: 1, review: 0, points: 0, total: 1 })
  assert.equal(selectionCounts([display]).total, 0)
  assert.equal(renderedRecordCount([original, symbol, symbol]), 1)
  assert.equal(renderedRecordCount([original, symbol, points.features[0]!]), 2)
  const filters = defaultFilters(); filters.primary = false; filters.review = true
  assert.equal(selectedDisplayPoints(symbols, filterAssets(all, filters)).features.length, 448)
})
test('missing files produce a useful error and failed requests can be retried', async () => {
  let fail = true
  const repo = createAssetRepository((async () => fail ? new Response('missing', { status: 404 }) : new Response(JSON.stringify(review))) as typeof fetch, '/')
  await assert.rejects(repo.loadReview(), /substations-review.geojson.*HTTP 404/)
  fail = false
  assert.equal((await repo.loadReview()).features.length, 448)
})

test('legend includes only selected original features and keeps unknown-voltage candidates separate', () => {
  const filters = defaultFilters()
  assert.deepEqual(selectedMapLegend(filterAssets(all, filters)), {
    lineVoltages: [500, 275, 150, 70], baselineLines: true, constructionLines: false, disusedLines: false,
    primary: true, constructionPrimary: false, review: false, points: false,
  })
  filters.lines = false; filters.primary = false; filters.review = true; filters.pointCandidates = true; filters.voltages = []
  const selected = filterAssets(all, filters)
  assert.equal(selected.length, 69) // 37 unknown-voltage review polygons + 32 source points.
  const key = selectedMapLegend(selected)
  assert.deepEqual(key.lineVoltages, [])
  assert.equal(key.review, true); assert.equal(key.points, true); assert.equal(key.primary, false)
  filters.unknownVoltage = false
  assert.ok(Object.values(selectedMapLegend(filterAssets(all, filters))).every(value => Array.isArray(value) ? value.length === 0 : value === false))
})

test('legend distinguishes construction lines from construction-tagged polygon substations', () => {
  const filters = defaultFilters(); filters.statuses = ['tagged_construction']
  const construction = selectedMapLegend(filterAssets(all, filters))
  assert.deepEqual(construction.lineVoltages, [500, 275, 150])
  assert.equal(construction.constructionLines, true); assert.equal(construction.constructionPrimary, true)
  assert.equal(construction.primary, false); assert.equal(construction.baselineLines, false)
  filters.lines = false
  const polygonOnly = selectedMapLegend(filterAssets(all, filters))
  assert.deepEqual(polygonOnly.lineVoltages, [])
  assert.equal(polygonOnly.constructionLines, false); assert.equal(polygonOnly.constructionPrimary, true)
  filters.lines = true; filters.statuses = ['tagged_disused']
  const disused = selectedMapLegend(filterAssets(all, filters))
  assert.deepEqual(disused.lineVoltages, [500, 70])
  assert.equal(disused.disusedLines, true); assert.equal(disused.primary, false)
})

test('legend excludes derived representatives and clears every key for an empty search', () => {
  const original = primary.features[0]!
  const representative = { ...original, properties: { ...original.properties, counts_as_inventory: false as const } }
  const filters = defaultFilters(); filters.query = 'no matching source asset xyz'
  assert.deepEqual(selectedMapLegend([representative]), selectedMapLegend(filterAssets(all, filters)))
  assert.deepEqual(selectedMapLegend([representative]), selectedMapLegend([]))
})
