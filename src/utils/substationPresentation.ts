import type { AssetFeature, DisplayPointCollection } from '../types/assets'

export const FOOTPRINT_MIN_ZOOM = 10

export function selectedDisplayPoints(symbols: DisplayPointCollection, selected: AssetFeature[]): DisplayPointCollection {
  const ids = new Set(selected.filter(feature => feature.properties.asset_type === 'substation_polygon').map(feature => feature.properties.feature_id))
  return { ...symbols, features: symbols.features.filter(feature => ids.has(feature.properties.represented_feature_id)) }
}

export function renderedRecordCount(features: Array<{ properties: { feature_id?: unknown; represented_feature_id?: unknown } }>): number {
  return new Set(features.map(feature => feature.properties.represented_feature_id ?? feature.properties.feature_id).filter(id => typeof id === 'string')).size
}
