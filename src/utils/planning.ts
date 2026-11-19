import type { AssetFeature, AssetFilters } from '../types/assets'
import type { ProjectFeature, PlanningKind, PlanFilters } from '../types/planning'

export function defaultPlanFilters(): PlanFilters { return { source: '', year: '', status: '' } }
export function isProject(record: AssetFeature | ProjectFeature): record is ProjectFeature {
  return 'source' in record.properties
}
export function projectKind(project: ProjectFeature): PlanningKind {
  return project.id.split(':')[1] as PlanningKind
}
export function matchesProject(project: ProjectFeature, filters: Pick<AssetFilters, 'query' | 'voltages' | 'unknownVoltage'>, plan: PlanFilters) {
  const p = project.properties
  if (plan.source && p.source !== plan.source) return false
  if (plan.year && String(p.target_cod_year ?? 'unknown') !== plan.year) return false
  if (plan.status && p.status !== plan.status) return false
  if (projectKind(project) !== 'generators') {
    if (p.voltage_kv == null ? !filters.unknownVoltage : !filters.voltages.includes(p.voltage_kv)) return false
  }
  const query = filters.query.trim().toLowerCase()
  return !query || [p.name, p.id, project.id, p.site_id, p.province, p.system, p.from_substation,
    p.to_substation, p.technology, p.type, p.technology_label, p.source].some(value => value?.toLowerCase().includes(query))
}
