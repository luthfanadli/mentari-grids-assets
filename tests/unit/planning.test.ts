import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { createAssetRepository } from '../../src/services/assetData.ts'
import { defaultFilters, featureBounds } from '../../src/utils/filterAssets.ts'
import { defaultPlanFilters, matchesProject } from '../../src/utils/planning.ts'
import type { ProjectCollection } from '../../src/types/planning.ts'

const read = (name: string) => JSON.parse(readFileSync('public/data/planning/' + name, 'utf8'))
const transmission: ProjectCollection = read('transmission.geojson')
const substations: ProjectCollection = read('substations.geojson')
const generators: ProjectCollection = read('generators.geojson')

test('planning search, source, stage and target years filter source rows, independent of OSM status', () => {
  const map = defaultFilters(), plan = defaultPlanFilters()
  map.statuses = []
  const all = [...transmission.features, ...substations.features, ...generators.features]
  const select = () => all.filter(f => matchesProject(f, map, plan))
  assert.equal(select().length, 4057)
  plan.source = 'RUKN 2025-2060'
  plan.status = 'Study'
  assert.equal(select().length, 8)
  plan.year = '2045'
  assert.equal(select().length, 3)
  map.voltages = []
  assert.equal(select().length, 1)
  const study = select()[0]!
  assert.equal(study.properties.capacity_mw, 2000)
  map.query = study.properties.id.toLowerCase()
  assert.equal(select()[0]?.id, study.id)
  map.query = 'absent project name xyz'
  assert.equal(select().length, 0)
})

test('missing target years and geometry remain searchable without generating a fit or location', () => {
  const missing = substations.features.filter(f => matchesProject(f, defaultFilters(), { ...defaultPlanFilters(), year: 'unknown' }))
  assert.equal(missing.length, 1)
  assert.equal(missing[0]!.properties.target_cod_year ?? null, null)
  const noRoute = transmission.features.filter(f => f.geometry === null)
  assert.equal(noRoute.length, 10)
  assert.equal(featureBounds(noRoute), null)
  const sample = generators.features.find(f => f.geometry?.type === 'Point')!
  const position = sample.geometry!.coordinates as number[]
  assert.deepEqual(featureBounds([...noRoute, sample]), [...position, ...position])
})

test('parallel planning requests share a catalogue and reject and evict incomplete layer responses', async () => {
  const catalog = read('catalog.json'), calls: string[] = []
  let broken = true
  const repository = createAssetRepository((async (url: string) => {
    const name = url.split('/').pop()!
    calls.push(name)
    const data = name === 'catalog.json' ? catalog : broken ? { ...generators, features: [] } : generators
    return new Response(JSON.stringify(data))
  }) as typeof fetch, '/')
  await Promise.all([repository.loadPlanningCatalog(), assert.rejects(repository.loadProjects('generators'), /Unexpected data format/)])
  broken = false
  const [one, two] = await Promise.all([repository.loadProjects('generators'), repository.loadProjects('generators')])
  assert.equal(one.features.length, 1059)
  assert.equal(one, two)
  assert.deepEqual(calls, ['catalog.json', 'generators.geojson', 'generators.geojson'])
})
