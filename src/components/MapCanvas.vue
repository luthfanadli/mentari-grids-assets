<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, watch } from 'vue'
import type { Map as LibreMap, GeoJSONSource, ExpressionSpecification } from 'maplibre-gl'
import type { AssetFeature, AssetCollection, DisplayPointCollection } from '../types/assets'
import type { ProjectFeature } from '../types/planning'
import { featureBounds } from '../utils/filterAssets'
import { VOLTAGE_COLORS } from '../utils/formatAssets'
import workerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url'
import { FOOTPRINT_MIN_ZOOM, renderedRecordCount } from '../utils/substationPresentation'
import MapBasemapPicker from './MapBasemapPicker.vue'
import { OSM_ATTRIBUTION, basemapStyle, isBasemapTileEvent } from '../utils/basemaps'
import type { BasemapId } from '../utils/basemaps'
import { addProjectLayers, projectHitLayers, projectMapData, projectSource } from '../utils/planningMap'
type MapRecord = AssetFeature | ProjectFeature
const props = defineProps<{ features: AssetFeature[]; projects: ProjectFeature[]; displayPoints: DisplayPointCollection; selectedId: string | null }>()
const emit = defineEmits<{ select: [feature: MapRecord]; viewport: [inventory: number | null, projects: number | null] }>()
const container = ref<HTMLElement | null>(null)
const detailsPopup = ref<HTMLElement | null>(null)
const ready = ref(false), mapError = ref(''), basemapError = ref(false), zoom = ref(4)
const customStyleUrl = import.meta.env.VITE_BASEMAP_STYLE_URL || undefined
const basemap = ref<BasemapId>(customStyleUrl ? 'custom' : 'osm'), mapAvailable = ref(false)
const renderedSymbols = ref(0), renderedPoints = ref(0), center = ref({ lng: 118, lat: -2 })
const renderedPlantSymbols = ref(0)
let map: LibreMap | undefined, resize: ResizeObserver | undefined, disposed = false
let viewportDirty = true
let basemapTileFailures = 0
let pendingFit: MapRecord[] | undefined
let measuredWidth = 0, measuredHeight = 0
const clickable = [...projectHitLayers, 'plant-symbols', 'plant-fill', 'plant-outline', 'construction-plant-outline', 'point-candidates', 'primary-symbols', 'review-symbols', 'primary-fill', 'primary-outline', 'construction-polygon-outline', 'review-fill', 'review-outline', 'line-hit']
const inventorySources = ['inventory', 'substation-symbols', 'plant-symbols', projectSource]
function findRecord(id?: string | null) {
  return props.features.find(f => f.properties.feature_id === id) ?? props.projects.find(f => f.id === id)
}
const voltageColor: ExpressionSpecification = ['match', ['get', 'max_voltage_kv'], 500, VOLTAGE_COLORS[500]!, 275, VOLTAGE_COLORS[275]!, 150, VOLTAGE_COLORS[150]!, 70, VOLTAGE_COLORS[70]!, '#6c7883']
const isLine: ExpressionSpecification = ['==', ['get', 'asset_type'], 'transmission_line']
const isPolygon: ExpressionSpecification = ['==', ['get', 'asset_type'], 'substation_polygon']
const isPrimary: ExpressionSpecification = ['all', isPolygon, ['==', ['get', 'review_reason'], null]]
const isReview: ExpressionSpecification = ['all', isPolygon, ['!=', ['get', 'review_reason'], null]]
const isPoint: ExpressionSpecification = ['==', ['get', 'asset_type'], 'substation_point']
const isPlant: ExpressionSpecification = ['==', ['get', 'asset_type'], 'power_plant']
const isArea: ExpressionSpecification = ['any', isPolygon, isPlant]
function data(): AssetCollection { return { type: 'FeatureCollection', features: props.features } }
function symbolData() {
  const parents = new Map(props.features.map(feature => [feature.properties.feature_id, feature]))
  return { ...props.displayPoints, features: props.displayPoints.features.flatMap(symbol => {
    const parent = parents.get(symbol.properties.represented_feature_id)
    return parent ? [{ ...symbol, properties: { ...parent.properties, ...symbol.properties } }] : []
  }) }
}
function plantSymbolData() {
  return { type: 'FeatureCollection' as const, features: props.features.filter(f => f.properties.asset_type === 'power_plant').map(feature => ({
    type: 'Feature' as const, id: feature.id,
    properties: { ...feature.properties, represented_feature_id: feature.properties.feature_id, counts_as_inventory: false,
      geometry_role: 'derived_power_plant_representative_point' },
    geometry: { type: 'Point' as const, coordinates: feature.properties.plant_representative_point! },
  })) }
}
function addPlantIcons() {
  if (!map) return
  for (const construction of [false, true]) {
    const canvas = document.createElement('canvas'); canvas.width = 32; canvas.height = 32
    const context = canvas.getContext('2d')!
    context.beginPath(); context.moveTo(16, 3); context.lineTo(29, 16); context.lineTo(16, 29); context.lineTo(3, 16); context.closePath()
    context.fillStyle = construction ? '#fff9f0' : '#b72236'; context.fill()
    context.strokeStyle = construction ? '#b72236' : '#fff'; context.lineWidth = 3
    if (construction) context.setLineDash([4, 3])
    context.stroke()
    map.addImage(construction ? 'plant-construction-icon' : 'plant-icon', context.getImageData(0, 0, 32, 32), { pixelRatio: 2 })
  }
}
function syncSelected() {
  const selected: ExpressionSpecification = ['==', ['get', 'feature_id'], props.selectedId ?? '']
  for (const [id, kind] of [['selection-line', isLine], ['selection-polygon', isArea], ['selection-point', isPoint]] as const) {
    if (map?.getLayer(id)) map.setFilter(id, ['all', kind, selected])
  }
  if (map?.getLayer('selection-symbol')) map.setFilter('selection-symbol', selected)
  if (map?.getLayer('selection-plant-symbol')) map.setFilter('selection-plant-symbol', selected)
  if (map?.getLayer('project-highlight-line')) map.setFilter('project-highlight-line', ['all', ['==', ['geometry-type'], 'LineString'], selected])
  if (map?.getLayer('project-highlight-point')) map.setFilter('project-highlight-point', ['all', ['==', ['geometry-type'], 'Point'], selected])
}
function addInventory() {
  if (!map || map.getSource('inventory')) return
  map.addSource('inventory', { type: 'geojson', data: data(), attribution: OSM_ATTRIBUTION + ' · <a href="https://openinframap.org/">OpenInfraMap</a> · <a href="https://opendatacommons.org/licenses/odbl/1-0/">ODbL</a>' })
  map.addSource('substation-symbols', { type: 'geojson', data: symbolData() })
  map.addSource('plant-symbols', { type: 'geojson', data: plantSymbolData() })
  addPlantIcons()
  map.addLayer({ id: 'plant-fill', type: 'fill', source: 'inventory', minzoom: FOOTPRINT_MIN_ZOOM, filter: isPlant,
    paint: { 'fill-color': '#d02030', 'fill-opacity': 0.2 } })
  map.addLayer({ id: 'plant-outline', type: 'line', source: 'inventory', minzoom: FOOTPRINT_MIN_ZOOM,
    filter: ['all', isPlant, ['!=', ['get', 'osm_tag_status'], 'tagged_construction']], paint: { 'line-color': '#b72236', 'line-width': 2 } })
  map.addLayer({ id: 'construction-plant-outline', type: 'line', source: 'inventory', minzoom: FOOTPRINT_MIN_ZOOM,
    filter: ['all', isPlant, ['==', ['get', 'osm_tag_status'], 'tagged_construction']], paint: { 'line-color': '#b72236', 'line-width': 2.5, 'line-dasharray': [3, 2] } })
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
  map.addLayer({ id: 'plant-symbols', type: 'symbol', source: 'plant-symbols', maxzoom: FOOTPRINT_MIN_ZOOM,
    layout: { 'icon-image': ['case', ['==', ['get', 'osm_tag_status'], 'tagged_construction'], 'plant-construction-icon', 'plant-icon'],
      'icon-allow-overlap': true, 'icon-ignore-placement': true, 'icon-size': 0.85 } })
  map.addLayer({ id: 'selection-symbol', type: 'circle', source: 'substation-symbols', maxzoom: FOOTPRINT_MIN_ZOOM, filter: ['==', ['get', 'feature_id'], ''],
    paint: { 'circle-radius': 9, 'circle-color': '#000', 'circle-opacity': 0, 'circle-stroke-width': 3, 'circle-stroke-color': '#f7bf27' } })
  map.addLayer({ id: 'selection-point', type: 'circle', source: 'inventory', filter: ['==', ['get', 'feature_id'], ''],
    paint: { 'circle-radius': 10, 'circle-color': '#000', 'circle-opacity': 0, 'circle-stroke-width': 3, 'circle-stroke-color': '#f7bf27' } })
  map.addLayer({ id: 'selection-plant-symbol', type: 'circle', source: 'plant-symbols', maxzoom: FOOTPRINT_MIN_ZOOM,
    filter: ['==', ['get', 'feature_id'], ''], paint: { 'circle-radius': 10, 'circle-color': '#000', 'circle-opacity': 0, 'circle-stroke-width': 3, 'circle-stroke-color': '#f7bf27' } })
  addProjectLayers(map, props.projects)
  syncSelected(); ready.value = true; viewportDirty = true
}
function updateViewport() {
  if (!map || !ready.value) return
  const selectedIds = new Set(props.features.map(feature => feature.properties.feature_id))
  const projectIds = new Set(props.projects.map(feature => feature.id))
  const rendered = map.queryRenderedFeatures(undefined, { layers: clickable }).filter(feature =>
    feature.source === projectSource ? projectIds.has(feature.properties.feature_id) :
      selectedIds.has(feature.properties.represented_feature_id ?? feature.properties.feature_id))
  renderedSymbols.value = renderedRecordCount(rendered.filter(feature => feature.source === 'substation-symbols'))
  renderedPoints.value = renderedRecordCount(rendered.filter(feature => feature.properties.asset_type === 'substation_point'))
  renderedPlantSymbols.value = renderedRecordCount(rendered.filter(feature => feature.source === 'plant-symbols'))
  center.value = map.getCenter()
  zoom.value = map.getZoom()
  emit('viewport', renderedRecordCount(rendered.filter(f => f.source !== projectSource)), renderedRecordCount(rendered.filter(f => f.source === projectSource)))
}
function fitFeatures(features: MapRecord[]) {
  const bounds = featureBounds(features)
  if (map && bounds) {
    const canvas = container.value?.getBoundingClientRect()
    const popup = detailsPopup.value?.getBoundingClientRect()
    const padding = canvas && popup ? canvas.width <= 760
      ? { top: 45, right: 30, bottom: Math.ceil(canvas.bottom - popup.top) + 20, left: 30 }
      : { top: 45, right: Math.ceil(canvas.right - popup.left) + 20, bottom: 45, left: 45 }
      : 45
    map.fitBounds([[bounds[0], bounds[1]], [bounds[2], bounds[3]]], { padding, maxZoom: 15, ...cameraTransition() })
    pendingFit = map.isMoving() ? features : undefined
  }
}
function resizeMap() {
  if (!map || !container.value) return
  const width = container.value.clientWidth, height = container.value.clientHeight
  if (!width || !height) return
  // MapLibre may resize its canvas first through its own window listener.
  if (measuredWidth === width && measuredHeight === height) return
  measuredWidth = width; measuredHeight = height
  // Restart an active fit after resizing so its destination uses the new canvas center.
  const selected = findRecord(props.selectedId)
  const interruptedFit = pendingFit ?? (selected ? [selected] : undefined)
  map.stop()
  map.resize()
  if (interruptedFit) fitFeatures(interruptedFit)
}
function cameraTransition() {
  return { duration: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : 700, linear: true, easing: (t: number) => t * t * (3 - 2 * t) }
}
function resetBasemapStatus() {
  basemapTileFailures = 0
  basemapError.value = false
}
function changeBasemap(next: BasemapId) {
  if (!map || disposed || basemap.value === next) return
  basemap.value = next
  resetBasemapStatus(); ready.value = false; viewportDirty = true
  emit('viewport', null, null)
  map.setStyle(basemapStyle(next, customStyleUrl), { diff: false })
}
watch([() => props.features, () => props.displayPoints], () => {
  viewportDirty = true
  emit('viewport', null, null)
  const source = map?.getSource('inventory') as GeoJSONSource | undefined
  source?.setData(data())
  const symbols = map?.getSource('substation-symbols') as GeoJSONSource | undefined
  symbols?.setData(symbolData())
  const plants = map?.getSource('plant-symbols') as GeoJSONSource | undefined
  plants?.setData(plantSymbolData())
})
watch(() => props.projects, projects => {
  viewportDirty = true
  emit('viewport', null, null)
  const source = map?.getSource(projectSource) as GeoJSONSource | undefined
  source?.setData(projectMapData(projects))
})
watch(() => props.selectedId, (selectedId, previousId) => {
  syncSelected()
  // Keep the selected geometry clear of the floating card; closing recenters it.
  resizeMap()
  const selected = findRecord(selectedId ?? previousId)
  if (selected) fitFeatures([selected])
}, { flush: 'post' })
onMounted(async () => {
  try {
    const libre = await import('maplibre-gl')
    if (disposed || !container.value) return
    libre.setWorkerUrl(workerUrl)
    map = new libre.Map({ container: container.value, style: basemapStyle(basemap.value, customStyleUrl), bounds: [[94.5, -11.4], [141.7, 6.7]], fitBoundsOptions: { padding: 25 }, maxZoom: 19, minZoom: 2, renderWorldCopies: false, attributionControl: false, fadeDuration: 0 })
    center.value = map.getCenter()
    zoom.value = map.getZoom()
    mapAvailable.value = true
    map.addControl(new libre.NavigationControl({ showCompass: false }), 'top-right')
    map.addControl(new libre.ScaleControl({ unit: 'metric', maxWidth: 80 }), 'bottom-left')
    map.addControl(new libre.AttributionControl(), 'bottom-right')
    map.on('style.load', addInventory)
    map.on('idle', updateViewport)
    map.on('sourcedata', event => {
      if (inventorySources.includes(event.sourceId)) viewportDirty = true
      if (isBasemapTileEvent(event) && event.tile.state === 'loaded' && map?.getSource(event.sourceId)) resetBasemapStatus()
    })
    // Inventory counts must not wait for slow or unavailable external raster tiles.
    map.on('render', () => {
      if (viewportDirty && ready.value && map && !map.isMoving() && inventorySources.every(id => map!.getSource(id) && map!.isSourceLoaded(id))) {
        updateViewport(); viewportDirty = false
      }
    })
    map.on('movestart', () => { resetBasemapStatus(); viewportDirty = true; emit('viewport', null, null) })
    map.on('moveend', () => { pendingFit = undefined })
    map.on('error', event => {
      if (basemap.value === 'plain' || !isBasemapTileEvent(event) || !map?.getSource(event.sourceId)) return
      basemapError.value = ++basemapTileFailures >= 2
    })
    map.on('click', event => {
      if (!ready.value || !map) return
      const hits = map.queryRenderedFeatures([[event.point.x - 4, event.point.y - 4], [event.point.x + 4, event.point.y + 4]], { layers: clickable })
      const hit = hits.find(feature => feature.geometry.type === 'Point') ?? hits[0]
      const selected = findRecord(hit?.properties.represented_feature_id ?? hit?.properties.feature_id)
      if (selected) emit('select', selected)
    })
    map.on('mousemove', event => { if (ready.value && map) map.getCanvas().style.cursor = map.queryRenderedFeatures(event.point, { layers: clickable }).length ? 'pointer' : '' })
    resize = new ResizeObserver(resizeMap); resize.observe(container.value)
  } catch (cause) { mapError.value = `Map unavailable. ${cause instanceof Error ? cause.message : 'WebGL could not start'}. Open Summary or RUPTL plans to browse records.` }
})
onBeforeUnmount(() => { disposed = true; resize?.disconnect(); map?.remove() })
defineExpose({ fitFeatures })
</script>
<template>
  <section class="map-card" aria-label="Spatial asset inventory">
    <div class="map-frame">
    <slot name="layers" :overview="zoom < FOOTPRINT_MIN_ZOOM"/>
    <div class="map-body"><div ref="container" class="map-container" role="region" aria-label="Interactive map of Indonesia’s electricity network and planning projects" data-testid="map" :data-ready="ready" :data-basemap="basemap" :data-substation-mode="zoom < FOOTPRINT_MIN_ZOOM ? 'representative-symbols' : 'footprints'" :data-rendered-symbols="renderedSymbols" :data-rendered-point-candidates="renderedPoints" :data-rendered-plant-symbols="renderedPlantSymbols" :data-zoom="zoom" :data-center-lng="center.lng" :data-center-lat="center.lat"></div>
      <div class="map-actions" role="group" aria-label="Map tools">
      <button class="map-tool-button" :disabled="!ready || !(features.length || projects.some(f => f.geometry))" aria-label="Fit filtered records" title="Fit filtered records" @click="fitFeatures([...features, ...projects])"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><path d="M9 4H4v5m11-5h5v5M4 15v5h5m11-5v5h-5"/><circle cx="12" cy="12" r="2.5"/></svg></button>
      <span class="map-tools-divider" aria-hidden="true"></span>
      <MapBasemapPicker :selected="basemap" :custom-available="!!customStyleUrl" :disabled="!mapAvailable" :tile-error="basemapError" @change="changeBasemap"/>
      </div>
      <div v-if="mapError" class="map-failure" role="alert">{{ mapError }}</div><div v-else-if="!ready" class="map-loading" role="status">Loading map…</div>
      <slot name="status"/>
      <div v-if="selectedId" ref="detailsPopup" class="map-details"><slot name="details"/></div>
    </div>
    </div>
  </section>
</template>
