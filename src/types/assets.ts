import type { Feature, FeatureCollection, LineString, MultiLineString, Polygon, MultiPolygon, Point } from 'geojson'

export type OsmStatus = 'not_flagged_in_osm' | 'tagged_construction' | 'tagged_disused' | 'conflicting_tags'
export type ReviewReason = 'transmission_missing_voltage' | 'high_voltage_unknown_type' | 'high_voltage_distribution_tag' | 'point_only_unvalidated'
export type AssetGeometry = LineString | MultiLineString | Polygon | MultiPolygon | Point
export interface AssetProperties {
  feature_id: string
  source_layer: string
  source_id: string
  asset_type: 'transmission_line' | 'substation_polygon' | 'substation_point' | 'power_plant'
  display_name: string
  display_name_is_fallback: boolean
  name: string | null
  ref: string | null
  operator: string | null
  max_voltage_v: number | null
  max_voltage_kv: number | null
  voltages_raw: string | null
  all_voltages_kv: number[]
  construction: boolean | null
  disused: boolean | null
  osm_tag_status: OsmStatus
  source_status_verified: false
  substation_type: string | null
  review_reason: ReviewReason | null
  location: string | null
  circuits: number | null
  mapped_geometry_length_km: number | null
  geometry_role?: 'original_point' | 'original_power_plant_footprint'
  plant_source?: string | null
  plant_method?: string | null
  plant_output_raw?: number | null
  plant_output_unit?: null
  plant_start_date_raw?: string | null
  plant_name_en?: string | null
  plant_description?: string | null
  plant_wikidata?: string | null
  plant_representative_point?: [number, number]
  matching_classification?: 'distinct_point_only_candidate'
  matching_reason?: string
  matching_version?: string
  nearest_polygon_feature_id?: string
  nearest_polygon_distance_m?: number
  counts_as_inventory?: false
}
export type AssetFeature = Feature<AssetGeometry, AssetProperties>
export type AssetCollection = FeatureCollection<AssetGeometry, AssetProperties>
export interface DisplayPointProperties {
  feature_id: string
  represented_feature_id: string
  source_id: string
  inventory_group: 'primary' | 'review'
  geometry_role: 'derived_polygon_representative_point'
  counts_as_inventory: false
  method: string
}
export type DisplayPointCollection = FeatureCollection<Point, DisplayPointProperties>
export interface AssetFilters {
  query: string
  voltages: number[]
  statuses: OsmStatus[]
  lines: boolean
  primary: boolean
  powerPlants: boolean
  review: boolean
  pointCandidates: boolean
  unknownVoltage: boolean
}
export interface DatasetSummary {
  count: number
  statuses: Record<OsmStatus, number>
  voltage_kv: Record<string, number>
  missing_values: Record<string, number>
  fallback_names: number
}
export interface InventorySummary {
  schema_version: number
  data_version: string
  source_data_vintage: string
  source_sha256: string
  raw_counts: Record<string, number>
  datasets: Record<'lines' | 'primary' | 'review' | 'point_candidates' | 'power_plants', DatasetSummary>
  review_reasons: Record<ReviewReason, number>
  default_selection: Record<'lines' | 'primary' | 'review' | 'points' | 'plants', number>
  output_bytes: Record<string, number>
  substation_point_matching: {
    matching_version: string
    classifications: Record<'matched' | 'uncertain' | 'distinct_point_only_candidate', number>
    eligible_point_candidates: number
    held_distinct_candidates: number
    pair_comparisons: number
  }
  substation_presentation: { representative_symbol_count: number; footprint_min_zoom: number; counts_as_inventory: false }
  power_plant_presentation: { representative_symbol_count: number; footprint_min_zoom: number; counts_as_inventory: false; coordinates_field: string }
}
