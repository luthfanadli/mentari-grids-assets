import type { StyleSpecification } from 'maplibre-gl'

export type BasemapId = 'osm' | 'google_satellite' | 'plain' | 'custom'

export const BASEMAP_LABELS: Record<BasemapId, string> = {
  osm: 'OpenStreetMap',
  google_satellite: 'Google Satellite',
  plain: 'Plain background',
  custom: 'Custom basemap',
}

const GOOGLE_SATELLITE_TILE_URL = 'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}'
export const OSM_ATTRIBUTION = '© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap contributors</a>'
const GEOGRAPHY_SOURCE = 'regional-context'

type BasemapTileEvent = { sourceId: string; source: { type: string }; tile: { state?: string } }
export function isBasemapTileEvent(event: unknown): event is BasemapTileEvent {
  if (!event || typeof event !== 'object') return false
  const data = event as Partial<BasemapTileEvent>
  return typeof data.sourceId === 'string' && !['inventory', 'substation-symbols', 'plant-symbols', 'planning-projects', GEOGRAPHY_SOURCE].includes(data.sourceId) &&
    ['raster', 'raster-dem', 'vector'].includes(data.source?.type ?? '') && !!data.tile && typeof data.tile === 'object'
}

function addGeographicContext(style: StyleSpecification) {
  style.sources[GEOGRAPHY_SOURCE] = {
    type: 'geojson', data: `${import.meta.env?.BASE_URL ?? '/'}basemap/regional-context.geojson`, maxzoom: 8,
    attribution: '<a href="https://www.naturalearthdata.com/" target="_blank" rel="noopener">Natural Earth</a>',
  }
  style.layers.push({
    id: 'regional-land', type: 'fill', source: GEOGRAPHY_SOURCE, filter: ['==', ['geometry-type'], 'Polygon'],
    paint: { 'fill-color': '#f7f8f1', 'fill-outline-color': '#b2c5bf' },
  })
  for (const detail of [false, true]) {
    style.layers.push({
      id: detail ? 'local-place-labels' : 'regional-place-labels', type: 'symbol', source: GEOGRAPHY_SOURCE,
      minzoom: detail ? 5 : 2, maxzoom: 9, filter: ['==', ['get', 'detail'], detail],
      layout: {
        'text-field': ['get', 'label'], 'text-font': ['Arial', 'sans-serif'],
        'text-transform': ['case', ['==', ['get', 'kind'], 'island'], 'none', 'uppercase'],
        'text-size': ['interpolate', ['linear'], ['zoom'], 2, 10, 5, 12.5, 8, 14],
        'text-letter-spacing': 0.075, 'text-max-width': 11, 'text-padding': 8,
        'symbol-sort-key': ['get', 'priority'],
      },
      paint: {
        'text-color': ['case', ['==', ['get', 'kind'], 'water'], '#597d8c', '#53665f'],
        'text-halo-color': ['case', ['==', ['get', 'kind'], 'water'], '#dfebef', '#f8f9f4'],
        'text-halo-width': 1.3,
      },
    })
  }
}

export function basemapStyle(id: BasemapId, customStyleUrl?: string): StyleSpecification | string {
  if (id === 'custom' && customStyleUrl) return customStyleUrl
  const style: StyleSpecification = {
    version: 8,
    sources: {},
    layers: [{ id: 'background', type: 'background', paint: { 'background-color': id === 'osm' ? '#dae8ed' : '#edf2f8' } }],
  }
  if (id === 'google_satellite') {
    style.sources['google-satellite'] = {
      type: 'raster', tiles: [GOOGLE_SATELLITE_TILE_URL], tileSize: 256, maxzoom: 19,
      attribution: '© <a href="https://maps.google.com/" target="_blank" rel="noopener">Google Maps</a>',
    }
    style.layers.push({ id: 'basemap', type: 'raster', source: 'google-satellite', paint: { 'raster-opacity': 1 } })
  } else if (id === 'osm') {
    addGeographicContext(style)
    style.sources.osm = {
      type: 'raster', tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'], tileSize: 256, maxzoom: 19,
      attribution: OSM_ATTRIBUTION,
    }
    // Each arriving tile replaces the small-scale coastline and names underneath it.
    style.layers.push({ id: 'basemap', type: 'raster', source: 'osm', paint: { 'raster-saturation': -0.85, 'raster-contrast': -0.12 } })
  }
  return style
}
