import type { AssetFeature, DisplayPointCollection } from '../types/assets'

export const FOOTPRINT_MIN_ZOOM = 10

export function polygonStyleState(features: AssetFeature[]) {
  const styles = { primary: false, constructionPrimary: false, plants: false, constructionPlants: false }
  for (const { properties: p } of features) {
    if (p.counts_as_inventory === false) continue
    if (p.asset_type === 'power_plant') {
      if (p.osm_tag_status === 'tagged_construction') styles.constructionPlants = true
      else styles.plants = true
    } else if (p.asset_type === 'substation_polygon' && !p.review_reason) {
      if (p.osm_tag_status === 'tagged_construction') styles.constructionPrimary = true
      else styles.primary = true
    }
  }
  return styles
}

export function selectedDisplayPoints(symbols: DisplayPointCollection, selected: AssetFeature[]): DisplayPointCollection {
  const ids = new Set(selected.filter(feature => feature.properties.asset_type === 'substation_polygon').map(feature => feature.properties.feature_id))
  return { ...symbols, features: symbols.features.filter(feature => ids.has(feature.properties.represented_feature_id)) }
}

export function renderedRecordCount(features: Array<{ properties: { feature_id?: unknown; represented_feature_id?: unknown } }>): number {
  return new Set(features.map(feature => feature.properties.represented_feature_id ?? feature.properties.feature_id).filter(id => typeof id === 'string')).size
}
