<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, watch } from 'vue'
import type { Map as LibreMap, GeoJSONSource, ExpressionSpecification } from 'maplibre-gl'
import type { AssetFeature, AssetCollection, DisplayPointCollection } from '../types/assets'
import { featureBounds } from '../utils/filterAssets'
import { VOLTAGE_COLORS } from '../utils/formatAssets'
import workerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url'
import { FOOTPRINT_MIN_ZOOM, renderedRecordCount } from '../utils/substationPresentation'
import MapLegend from './MapLegend.vue'
import MapBasemapPicker from './MapBasemapPicker.vue'
import { BASEMAP_LABELS, basemapStyle } from '../utils/basemaps'
import type { BasemapId } from '../utils/basemaps'
const props = defineProps<{ features: AssetFeature[]; displayPoints: DisplayPointCollection; selectedId: string | null }>()
const emit = defineEmits<{ select: [feature: AssetFeature]; viewport: [count: number | null] }>()
const container = ref<HTMLElement | null>(null)
const ready = ref(false), mapError = ref(''), basemapError = ref(false), zoom = ref(4)
const customStyleUrl = import.meta.env.VITE_BASEMAP_STYLE_URL || undefined
const basemap = ref<BasemapId>(customStyleUrl ? 'custom' : 'osm'), mapAvailable = ref(false)
const renderedSymbols = ref(0), renderedPoints = ref(0), center = ref({ lng: 118, lat: -2 })
let map: LibreMap | undefined, resize: ResizeObserver | undefined, disposed = false
let viewportDirty = true
let basemapTimeout: ReturnType<typeof setTimeout> | undefined
let basemapHasError = false
const clickable = ['point-candidates', 'primary-symbols', 'review-symbols', 'primary-fill', 'primary-outline', 'construction-polygon-outline', 'review-fill', 'review-outline', 'line-hit']
const voltageColor: ExpressionSpecification = ['match', ['get', 'max_voltage_kv'], 500, VOLTAGE_COLORS[500]!, 275, VOLTAGE_COLORS[275]!, 150, VOLTAGE_COLORS[150]!, 70, VOLTAGE_COLORS[70]!, '#6c7883']
const isLine: ExpressionSpecification = ['==', ['get', 'asset_type'], 'transmission_line']
const isPolygon: ExpressionSpecification = ['==', ['get', 'asset_type'], 'substation_polygon']
const isPrimary: ExpressionSpecification = ['all', isPolygon, ['==', ['get', 'review_reason'], null]]
const isReview: ExpressionSpecification = ['all', isPolygon, ['!=', ['get', 'review_reason'], null]]
const isPoint: ExpressionSpecification = ['==', ['get', 'asset_type'], 'substation_point']
function data(): AssetCollection { return { type: 'FeatureCollection', features: props.features } }
function symbolData() {
  const parents = new Map(props.features.map(feature => [feature.properties.feature_id, feature]))
  return { ...props.displayPoints, features: props.displayPoints.features.flatMap(symbol => {
    const parent = parents.get(symbol.properties.represented_feature_id)
    return parent ? [{ ...symbol, properties: { ...parent.properties, ...symbol.properties } }] : []
  }) }
}
function syncSelected() {
  const selected: ExpressionSpecification = ['==', ['get', 'feature_id'], props.selectedId ?? '']
  for (const [id, kind] of [['selection-line', isLine], ['selection-polygon', isPolygon], ['selection-point', isPoint]] as const) {
    if (map?.getLayer(id)) map.setFilter(id, ['all', kind, selected])
  }
  if (map?.getLayer('selection-symbol')) map.setFilter('selection-symbol', selected)
}
function addInventory() {
  if (!map || map.getSource('inventory')) return
  map.addSource('inventory', { type: 'geojson', data: data(), attribution: 'Inventory: © <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap contributors</a> · <a href="https://openinframap.org/" target="_blank" rel="noopener">OpenInfraMap</a> · <a href="https://opendatacommons.org/licenses/odbl/1-0/" target="_blank" rel="noopener">ODbL</a>' })
  map.addSource('substation-symbols', { type: 'geojson', data: symbolData() })
  if (basemap.value === 'google_satellite') {
    map.addLayer({ id: 'satellite-line-casing', type: 'line', source: 'inventory', filter: isLine,
      paint: { 'line-color': '#fff', 'line-width': ['interpolate', ['linear'], ['zoom'], 4, 2.8, 10, 4.5, 15, 6.5], 'line-opacity': 0.55 } })
  }
  map.addLayer({ id: 'selection-line', type: 'line', source: 'inventory', filter: ['==', ['get', 'feature_id'], ''], paint: { 'line-color': '#ffd04d', 'line-width': 9, 'line-opacity': 0.9 } })
  const lineWidth: ExpressionSpecification = ['interpolate', ['linear'], ['zoom'], 4, 1.4, 10, 3, 15, 5]
  for (const [id, status, dash] of [['baseline-lines', 'not_flagged_in_osm', null], ['construction-lines', 'tagged_construction', [3, 2]], ['disused-lines', 'tagged_disused', [1, 3]]] as const) {
    map.addLayer({ id, type: 'line', source: 'inventory', filter: ['all', isLine, ['==', ['get', 'osm_tag_status'], status]], paint: { 'line-color': voltageColor, 'line-width': lineWidth, 'line-opacity': status === 'tagged_disused' ? 0.55 : 0.9, ...(dash ? { 'line-dasharray': [...dash] } : {}) } })
  }
  map.addLayer({ id: 'primary-fill', type: 'fill', source: 'inventory', minzoom: FOOTPRINT_MIN_ZOOM, filter: isPrimary, paint: { 'fill-color': '#086e66', 'fill-opacity': 0.4 } })
  map.addLayer({ id: 'primary-outline', type: 'line', source: 'inventory', minzoom: FOOTPRINT_MIN_ZOOM, filter: ['all', isPrimary, ['!=', ['get', 'osm_tag_status'], 'tagged_construction']], paint: { 'line-color': '#075c55', 'line-width': 2 } })
  map.addLayer({ id: 'construction-polygon-outline', type: 'line', source: 'inventory', minzoom: FOOTPRINT_MIN_ZOOM, filter: ['all', isPrimary, ['==', ['get', 'osm_tag_status'], 'tagged_construction']], paint: { 'line-color': '#ac6910', 'line-width': 3, 'line-dasharray': [3, 2] } })
  map.addLayer({ id: 'review-fill', type: 'fill', source: 'inventory', minzoom: FOOTPRINT_MIN_ZOOM, filter: isReview, paint: { 'fill-color': '#d08614', 'fill-opacity': 0.2 } })
  map.addLayer({ id: 'review-outline', type: 'line', source: 'inventory', minzoom: FOOTPRINT_MIN_ZOOM, filter: isReview, paint: { 'line-color': '#b46c00', 'line-width': 2.5, 'line-dasharray': [2, 2] } })
  map.addLayer({ id: 'selection-polygon', type: 'line', source: 'inventory', minzoom: FOOTPRINT_MIN_ZOOM, filter: ['==', ['get', 'feature_id'], ''], paint: { 'line-color': '#f7bf27', 'line-width': 5 } })
  map.addLayer({ id: 'line-hit', type: 'line', source: 'inventory', filter: isLine, paint: { 'line-color': '#000', 'line-width': 12, 'line-opacity': 0 } })
  map.addLayer({ id: 'primary-symbols', type: 'circle', source: 'substation-symbols', maxzoom: FOOTPRINT_MIN_ZOOM, filter: isPrimary,
    paint: { 'circle-radius': ['interpolate', ['linear'], ['zoom'], 3, 3.5, 9, 6], 'circle-color': ['case', ['==', ['get', 'osm_tag_status'], 'tagged_construction'], '#ac6910', '#086e66'], 'circle-stroke-color': '#fff', 'circle-stroke-width': 1.2 } })
  map.addLayer({ id: 'review-symbols', type: 'circle', source: 'substation-symbols', maxzoom: FOOTPRINT_MIN_ZOOM, filter: isReview,
    paint: { 'circle-radius': 4.5, 'circle-color': '#fff7df', 'circle-stroke-color': '#b46c00', 'circle-stroke-width': 2 } })
  map.addLayer({ id: 'point-candidates', type: 'circle', source: 'inventory', filter: isPoint,
    paint: { 'circle-radius': 5.5, 'circle-color': '#fff', 'circle-stroke-color': '#b8406a', 'circle-stroke-width': 2.5 } })
  map.addLayer({ id: 'selection-symbol', type: 'circle', source: 'substation-symbols', maxzoom: FOOTPRINT_MIN_ZOOM, filter: ['==', ['get', 'feature_id'], ''],
    paint: { 'circle-radius': 9, 'circle-color': '#000', 'circle-opacity': 0, 'circle-stroke-width': 3, 'circle-stroke-color': '#f7bf27' } })
  map.addLayer({ id: 'selection-point', type: 'circle', source: 'inventory', filter: ['==', ['get', 'feature_id'], ''],
    paint: { 'circle-radius': 10, 'circle-color': '#000', 'circle-opacity': 0, 'circle-stroke-width': 3, 'circle-stroke-color': '#f7bf27' } })
  syncSelected(); ready.value = true; viewportDirty = true
}
function updateViewport() {
  if (!map || !ready.value) return
  const rendered = map.queryRenderedFeatures(undefined, { layers: clickable })
  renderedSymbols.value = renderedRecordCount(rendered.filter(feature => feature.source === 'substation-symbols'))
  renderedPoints.value = renderedRecordCount(rendered.filter(feature => feature.properties.asset_type === 'substation_point'))
  center.value = map.getCenter()
  zoom.value = map.getZoom(); emit('viewport', renderedRecordCount(rendered))
}
function fitFeatures(features: AssetFeature[]) {
  const bounds = featureBounds(features)
  if (map && bounds) map.fitBounds([[bounds[0], bounds[1]], [bounds[2], bounds[3]]], { padding: 45, maxZoom: 15, ...cameraTransition() })
}
function cameraTransition() {
  return { duration: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : 700, linear: true, easing: (t: number) => t * t * (3 - 2 * t) }
}
function home() { map?.fitBounds([[94.5, -11.4], [141.7, 6.7]], { padding: 25, ...cameraTransition() }) }
function watchBasemapAvailability() {
  clearTimeout(basemapTimeout)
  if (basemap.value !== 'plain') basemapTimeout = setTimeout(() => { if (map && !map.areTilesLoaded()) basemapError.value = true }, 12000)
}
function changeBasemap(next: BasemapId) {
  if (!map || disposed || basemap.value === next) return
  basemap.value = next
  basemapError.value = false; basemapHasError = false; ready.value = false; viewportDirty = true
  emit('viewport', null)
  map.setStyle(basemapStyle(next, customStyleUrl), { diff: false })
  watchBasemapAvailability()
}
function usePlainBackground() { changeBasemap('plain') }
watch([() => props.features, () => props.displayPoints], () => {
  viewportDirty = true
  emit('viewport', null)
  const source = map?.getSource('inventory') as GeoJSONSource | undefined
  source?.setData(data())
  const symbols = map?.getSource('substation-symbols') as GeoJSONSource | undefined
  symbols?.setData(symbolData())
})
watch(() => props.selectedId, () => {
  syncSelected()
  const selected = props.features.find(f => f.properties.feature_id === props.selectedId)
  if (selected) fitFeatures([selected])
})
onMounted(async () => {
  try {
    const libre = await import('maplibre-gl')
    if (disposed || !container.value) return
    libre.setWorkerUrl(workerUrl)
    map = new libre.Map({ container: container.value, style: basemapStyle(basemap.value, customStyleUrl), bounds: [[94.5, -11.4], [141.7, 6.7]], fitBoundsOptions: { padding: 25 }, maxZoom: 19, minZoom: 2, renderWorldCopies: false, attributionControl: false })
    mapAvailable.value = true
    map.addControl(new libre.NavigationControl({ showCompass: false }), 'top-right')
    map.addControl(new libre.ScaleControl({ unit: 'metric' }), 'bottom-left')
    map.addControl(new libre.AttributionControl({ compact: false }), 'bottom-right')
    map.on('style.load', addInventory)
    map.on('idle', () => { updateViewport(); if (map?.areTilesLoaded()) { if (!basemapHasError) basemapError.value = false; clearTimeout(basemapTimeout) } })
    // Inventory counts must not wait for slow or unavailable external raster tiles.
    map.on('render', () => {
      if (viewportDirty && ready.value && map?.getSource('inventory') && map.getSource('substation-symbols') && map.isSourceLoaded('inventory') && map.isSourceLoaded('substation-symbols') && !map.isMoving()) {
        updateViewport(); viewportDirty = false
      }
    })
    map.on('movestart', () => { viewportDirty = true; emit('viewport', null) })
    map.on('error', () => { basemapHasError = true; basemapError.value = true })
    watchBasemapAvailability()
    map.on('click', event => {
      if (!ready.value || !map) return
      const hits = map.queryRenderedFeatures([[event.point.x - 4, event.point.y - 4], [event.point.x + 4, event.point.y + 4]], { layers: clickable })
      const hit = hits.find(feature => feature.source === 'substation-symbols' || feature.properties.asset_type === 'substation_point') ?? hits[0]
      const selected = props.features.find(f => f.properties.feature_id === (hit?.properties.represented_feature_id ?? hit?.properties.feature_id))
      if (selected) emit('select', selected)
    })
    map.on('mousemove', event => { if (ready.value && map) map.getCanvas().style.cursor = map.queryRenderedFeatures(event.point, { layers: clickable }).length ? 'pointer' : '' })
    resize = new ResizeObserver(() => map?.resize()); resize.observe(container.value)
  } catch (cause) { mapError.value = `Map unavailable. ${cause instanceof Error ? cause.message : 'WebGL could not start'}. You can still search and inspect records below.` }
})
onBeforeUnmount(() => { disposed = true; clearTimeout(basemapTimeout); resize?.disconnect(); map?.remove() })
</script>
<template>
  <section class="map-card" aria-label="Spatial asset inventory">
    <div class="map-toolbar"><div><span class="live-dot" aria-hidden="true"></span><strong>Spatial inventory</strong><span class="muted"> / Indonesia</span></div><div class="map-actions">
      <button class="map-tool-button" :disabled="!ready" aria-label="Zoom to Indonesia" title="Zoom to Indonesia" @click="home"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c5 5 5 12 0 17-5-5-5-12 0-17Z"/></svg></button>
      <button class="map-tool-button" :disabled="!ready || !features.length" aria-label="Fit filtered records" title="Fit filtered records" @click="fitFeatures(features)"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><path d="M9 4H4v5m11-5h5v5M4 15v5h5m11-5v5h-5"/><circle cx="12" cy="12" r="2.5"/></svg></button>
      <span class="map-tools-divider" aria-hidden="true"></span>
      <MapBasemapPicker :selected="basemap" :custom-available="!!customStyleUrl" :disabled="!mapAvailable" @change="changeBasemap"/>
    </div></div>
    <div class="map-body"><div ref="container" class="map-container" role="region" aria-label="Interactive map of selected line segments, substation footprints and point-only candidates" data-testid="map" :data-ready="ready" :data-basemap="basemap" :data-substation-mode="zoom < FOOTPRINT_MIN_ZOOM ? 'representative-symbols' : 'footprints'" :data-rendered-symbols="renderedSymbols" :data-rendered-point-candidates="renderedPoints" :data-zoom="zoom" :data-center-lng="center.lng" :data-center-lat="center.lat"></div>
      <div v-if="mapError" class="map-failure" role="alert">{{ mapError }}</div><div v-else-if="!ready" class="map-loading" role="status">Loading map…</div>
      <div v-if="basemapError" class="basemap-error" role="status">{{ BASEMAP_LABELS[basemap] }} is unavailable or taking too long. <button @click="usePlainBackground">Use plain background</button><span>Inventory overlays and records remain available.</span></div>
      <MapLegend :overview="zoom < FOOTPRINT_MIN_ZOOM"/>
      <span v-if="ready" class="zoom-label">ZOOM {{ zoom.toFixed(1) }}</span>
    </div>
  </section>
</template>
