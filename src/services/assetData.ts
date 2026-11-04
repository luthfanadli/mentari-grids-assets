import type { AssetCollection, DisplayPointCollection, InventorySummary } from '../types/assets'
export function createAssetRepository(fetcher: typeof fetch = fetch, base = import.meta.env?.BASE_URL ?? '/') {
  const requests = new Map<string, Promise<unknown>>()
  function load<T>(filename: string, validate: (value: unknown) => boolean): Promise<T> {
    const cached = requests.get(filename)
    if (cached) return cached as Promise<T>
    const request = (async () => {
      try {
        const response = await fetcher(`${base}data/${filename}`)
        if (!response.ok) throw new Error(`HTTP ${response.status}`)
        const data: unknown = await response.json()
        if (!validate(data)) throw new Error('Unexpected data format')
        return data as T
      } catch (error) {
        requests.delete(filename)
        throw new Error(`Could not load ${filename}. ${error instanceof Error ? error.message : 'Request failed'}. Check that the generated public/data files are deployed.`)
      }
    })()
    requests.set(filename, request)
    return request
  }
  const validCollection = (value: unknown) => {
    const data = value as AssetCollection | null
    return data?.type === 'FeatureCollection' && Array.isArray(data.features) && data.features.every(f =>
      f.type === 'Feature' && typeof f.properties?.feature_id === 'string' && typeof f.properties?.display_name === 'string' &&
      f.properties.source_status_verified === false && f.geometry && ['LineString', 'MultiLineString', 'Polygon', 'MultiPolygon', 'Point'].includes(f.geometry.type))
  }
  return {
    loadBase: async () => {
      const [lines, primary, summary, displayPoints] = await Promise.all([
        load<AssetCollection>('transmission-lines.geojson', validCollection), load<AssetCollection>('substations-primary.geojson', validCollection),
        load<InventorySummary>('summary.json', v => (v as InventorySummary)?.schema_version === 2 && !!(v as InventorySummary).datasets),
        load<DisplayPointCollection>('substation-display-points.geojson', v => {
          const data = v as DisplayPointCollection
          return data?.type === 'FeatureCollection' && Array.isArray(data.features) && data.features.every(feature =>
            feature.geometry?.type === 'Point' && feature.properties?.counts_as_inventory === false &&
            feature.properties.geometry_role === 'derived_polygon_representative_point' && feature.id === feature.properties.represented_feature_id)
        }),
      ])
      if (lines.features.length !== summary.datasets.lines.count || primary.features.length !== summary.datasets.primary.count || displayPoints.features.length !== summary.substation_presentation.representative_symbol_count) throw new Error('Dataset counts differ from summary.json. Use all eight files from the same preprocessing run.')
      return { lines, primary, summary, displayPoints }
    },
    loadReview: () => load<AssetCollection>('substations-review.geojson', validCollection),
    loadPointCandidates: () => load<AssetCollection>('substations-point-candidates.geojson', v => validCollection(v) && (v as AssetCollection).features.every(feature =>
      feature.properties.asset_type === 'substation_point' && feature.properties.matching_classification === 'distinct_point_only_candidate' && feature.geometry.type === 'Point')),
  }
}
