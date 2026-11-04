import type { AssetFeature, AssetFilters } from '../types/assets'

export const VOLTAGES = [500, 275, 150, 70] as const
export function defaultFilters(): AssetFilters {
  return { query: '', voltages: [...VOLTAGES], statuses: ['not_flagged_in_osm'], lines: true, primary: true, review: false, pointCandidates: false, unknownVoltage: true }
}
export function matchesFeature(feature: AssetFeature, filters: AssetFilters): boolean {
  const p = feature.properties
  if (p.osm_tag_status === 'conflicting_tags' || !filters.statuses.includes(p.osm_tag_status)) return false
  if (p.asset_type === 'substation_point') {
    if (!filters.pointCandidates || p.matching_classification !== 'distinct_point_only_candidate') return false
  } else if (p.review_reason ? !filters.review : p.asset_type === 'transmission_line' ? !filters.lines : !filters.primary) return false
  if (p.max_voltage_kv === null ? !filters.unknownVoltage : !filters.voltages.includes(p.max_voltage_kv)) return false
  const query = filters.query.trim().toLowerCase()
  return !query || [p.name, p.ref, p.operator, p.source_id, p.feature_id, p.display_name].some(value => value?.toLowerCase().includes(query))
}
export const filterAssets = (features: AssetFeature[], filters: AssetFilters) => features.filter(feature => matchesFeature(feature, filters))
export function selectionCounts(features: AssetFeature[]) {
  let lines = 0, primary = 0, review = 0, points = 0
  for (const feature of uniqueInventoryFeatures(features)) {
    if (feature.properties.asset_type === 'substation_point') points++
    else if (feature.properties.review_reason) review++
    else if (feature.properties.asset_type === 'transmission_line') lines++
    else primary++
  }
  return { lines, primary, review, points, total: lines + primary + review + points }
}
export function uniqueInventoryFeatures(features: AssetFeature[]): AssetFeature[] {
  return [...new Map(features.filter(feature => feature.properties.counts_as_inventory !== false).map(feature => [feature.properties.feature_id, feature])).values()]
}
export function featureBounds(features: AssetFeature[]): [number, number, number, number] | null {
  if (!features.length) return null
  let west = Infinity, south = Infinity, east = -Infinity, north = -Infinity
  const walk = (coords: unknown): void => {
    const values = coords as unknown[]
    if (typeof values[0] === 'number' && typeof values[1] === 'number') {
      west = Math.min(west, values[0]); east = Math.max(east, values[0])
      south = Math.min(south, values[1]); north = Math.max(north, values[1])
    } else values.forEach(walk)
  }
  for (const feature of features) {
    const bounds = feature.bbox
    if (bounds?.length === 4) {
      west = Math.min(west, bounds[0]!); south = Math.min(south, bounds[1]!)
      east = Math.max(east, bounds[2]!); north = Math.max(north, bounds[3]!)
    } else walk(feature.geometry.coordinates)
  }
  return [west, south, east, north]
}
