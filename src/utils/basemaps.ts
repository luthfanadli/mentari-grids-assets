import type { StyleSpecification } from 'maplibre-gl'

export type BasemapId = 'osm' | 'google_satellite' | 'plain' | 'custom'

export const BASEMAP_LABELS: Record<BasemapId, string> = {
  osm: 'OpenStreetMap',
  google_satellite: 'Google Satellite',
  plain: 'Plain background',
  custom: 'Custom basemap',
}

export const GOOGLE_SATELLITE_TILE_URL = 'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}'
export const OSM_ATTRIBUTION = '© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap contributors</a>'

export function basemapStyle(id: BasemapId, customStyleUrl?: string): StyleSpecification | string {
  if (id === 'custom' && customStyleUrl) return customStyleUrl
  const style: StyleSpecification = {
    version: 8,
    sources: {},
    layers: [{ id: 'background', type: 'background', paint: { 'background-color': '#edf2f8' } }],
  }
  if (id === 'google_satellite') {
    style.sources['google-satellite'] = {
      type: 'raster', tiles: [GOOGLE_SATELLITE_TILE_URL], tileSize: 256, maxzoom: 19,
      attribution: '© <a href="https://maps.google.com/" target="_blank" rel="noopener">Google Maps</a>',
    }
    style.layers.push({ id: 'basemap', type: 'raster', source: 'google-satellite', paint: { 'raster-opacity': 1 } })
  } else if (id === 'osm') {
    style.sources.osm = {
      type: 'raster', tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'], tileSize: 256, maxzoom: 19,
      attribution: OSM_ATTRIBUTION,
    }
    style.layers.push({ id: 'basemap', type: 'raster', source: 'osm', paint: { 'raster-saturation': -0.85, 'raster-contrast': -0.12, 'raster-opacity': 0.75 } })
  }
  return style
}
