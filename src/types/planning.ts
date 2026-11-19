import type { Feature, FeatureCollection, LineString, MultiLineString, Point } from 'geojson'

export const planningKinds = ['transmission', 'substations', 'generators'] as const
export type PlanningKind = typeof planningKinds[number]
export const planningLabels: Record<PlanningKind, string> = {
  transmission: 'Transmission projects',
  substations: 'Substation projects',
  generators: 'Generation projects',
}

interface ProjectProperties {
  id: string
  name: string
  source: string
  status: string
  province: string | null
  system: string | null
  target_cod_year?: number | null
  cod_re_base?: number | null
  cod_ared?: number | null
  scope?: string
  voltage_kv?: number | null
  voltage_label?: string
  capacity_mw?: number | null
  capacity_mva?: number | null
  storage_mwh?: number | null
  type?: string
  technology?: string
  technology_label?: string
  developer?: string
  site_id?: string | null
  from_substation?: string
  to_substation?: string
  route_status?: string
  geometry_source?: string
  location_source?: string
  location_confidence?: string
  circuits?: number | null
  length_km?: number | null
  circuit_km?: number | null
  line_type?: string | null
  hvdc?: boolean
  ruptl_page?: string | null
  ruptl_row?: string | null
}
export type ProjectGeometry = Point | LineString | MultiLineString
export interface ProjectFeature extends Feature<ProjectGeometry | null, ProjectProperties> { id: string }
export interface ProjectCollection extends FeatureCollection<ProjectGeometry | null, ProjectProperties> { features: ProjectFeature[] }
export interface PlanningCatalog {
  datasets: Record<PlanningKind, { count: number; mapped: number; bytes: number; sha256: string }>
  filters: { sources: string[]; statuses: string[]; target_years: number[]; unknown_year: boolean }
}
export interface PlanFilters { source: string; year: string; status: string }
