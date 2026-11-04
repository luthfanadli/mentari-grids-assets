import type { OsmStatus, ReviewReason } from '../types/assets'
export const STATUS_LABELS: Record<OsmStatus, string> = {
  not_flagged_in_osm: 'Not flagged in OSM', tagged_construction: 'Tagged construction',
  tagged_disused: 'Tagged disused', conflicting_tags: 'Conflicting tags — review required',
}
export const REVIEW_LABELS: Record<ReviewReason, string> = {
  transmission_missing_voltage: 'Transmission tag; voltage missing', high_voltage_unknown_type: 'Target voltage; substation type missing',
  high_voltage_distribution_tag: 'Target voltage; tagged distribution',
  point_only_unvalidated: 'Point-only candidate; voltage, function and physical-station identity unverified',
}
export const VOLTAGE_COLORS: Record<number, string> = { 500: '#8050bd', 275: '#277bb9', 150: '#168577', 70: '#bd7416' }
export const formatNumber = (value: number) => new Intl.NumberFormat('en-GB').format(value)
export const formatValue = (value: unknown): string => value === null || value === undefined || value === '' ? 'Not available' : String(value)
export const formatVoltage = (value: number | null): string => value === null ? 'Not available' : `${value} kV`
