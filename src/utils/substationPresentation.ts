import type { AssetFeature, DisplayPointCollection } from '../types/assets'
import { VOLTAGES } from './filterAssets.ts'

export const FOOTPRINT_MIN_ZOOM = 10

export function selectedMapLegend(features: AssetFeature[]) {
  const voltages = new Set<number>()
  const key = { lineVoltages: [] as number[], baselineLines: false, constructionLines: false, disusedLines: false,
    primary: false, constructionPrimary: false, review: false, points: false, plants: false, constructionPlants: false }
  for (const { properties: p } of features) {
    if (p.counts_as_inventory === false) continue
    if (p.asset_type === 'transmission_line') {
      if (p.max_voltage_kv !== null) voltages.add(p.max_voltage_kv)
      if (p.osm_tag_status === 'tagged_construction') key.constructionLines = true
      else if (p.osm_tag_status === 'tagged_disused') key.disusedLines = true
      else if (p.osm_tag_status === 'not_flagged_in_osm') key.baselineLines = true
    } else if (p.asset_type === 'power_plant') {
      if (p.osm_tag_status === 'tagged_construction') key.constructionPlants = true
      else key.plants = true
    } else if (p.asset_type === 'substation_point') key.points = true
    else if (p.review_reason) key.review = true
    else if (p.osm_tag_status === 'tagged_construction') key.constructionPrimary = true
    else key.primary = true
  }
  key.lineVoltages = VOLTAGES.filter(voltage => voltages.has(voltage))
  return key
}

export function selectedDisplayPoints(symbols: DisplayPointCollection, selected: AssetFeature[]): DisplayPointCollection {
  const ids = new Set(selected.filter(feature => feature.properties.asset_type === 'substation_polygon').map(feature => feature.properties.feature_id))
  return { ...symbols, features: symbols.features.filter(feature => ids.has(feature.properties.represented_feature_id)) }
}

export function renderedRecordCount(features: Array<{ properties: { feature_id?: unknown; represented_feature_id?: unknown } }>): number {
  return new Set(features.map(feature => feature.properties.represented_feature_id ?? feature.properties.feature_id).filter(id => typeof id === 'string')).size
}
