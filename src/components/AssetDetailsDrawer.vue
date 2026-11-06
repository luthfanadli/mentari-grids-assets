<script setup lang="ts">
import { computed, nextTick, onMounted, onBeforeUnmount, ref, watch } from 'vue'
import type { AssetFeature } from '../types/assets'
import { STATUS_LABELS, REVIEW_LABELS, formatValue, formatVoltage } from '../utils/formatAssets'
const props = defineProps<{ feature: AssetFeature }>()
const emit = defineEmits<{ close: [] }>()
const closeButton = ref<HTMLButtonElement | null>(null)
const content = ref<HTMLElement | null>(null)
const previousFocus = document.activeElement as HTMLElement | null
const p = computed(() => props.feature.properties)
watch(() => props.feature, async () => {
  await nextTick()
  if (content.value) content.value.scrollTop = 0
  closeButton.value?.focus()
}, { immediate: true })
function onEscape(event: KeyboardEvent) { if (event.key === 'Escape') emit('close') }
onMounted(() => document.addEventListener('keydown', onEscape))
onBeforeUnmount(() => { document.removeEventListener('keydown', onEscape); previousFocus?.focus() })
</script>
<template>
  <aside class="details-drawer" role="region" aria-labelledby="detail-title" data-testid="asset-details">
    <div class="drawer-heading"><span class="eyebrow">ASSET DETAILS</span><button ref="closeButton" class="icon-button" aria-label="Close feature details" @click="$emit('close')"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true" focusable="false"><path d="m6 6 12 12M18 6 6 18"/></svg></button></div>
    <div ref="content" class="details-content" role="region" aria-label="Asset attributes" tabindex="0">
    <span class="asset-kind">{{ p.asset_type === 'power_plant' ? 'Power plant footprint' : p.asset_type === 'substation_point' ? 'Unvalidated point-only candidate' : p.review_reason ? 'Review polygon candidate' : p.asset_type === 'transmission_line' ? 'Transmission line segment' : 'Primary substation polygon' }}</span>
    <h2 id="detail-title">{{ p.display_name }}</h2><p v-if="p.display_name_is_fallback" class="filter-note">Interface fallback label. No source name is available.</p>
    <div class="detail-badges"><span v-if="p.asset_type !== 'power_plant'" class="badge">{{ formatVoltage(p.max_voltage_kv) }}</span><span v-else class="badge">{{ p.plant_source || 'Energy source unavailable' }}</span><span class="badge muted-badge">Unverified operation</span></div>
    <p v-if="p.review_reason" class="review-callout"><strong>Manual validation required</strong>{{ REVIEW_LABELS[p.review_reason] }}. Not included in the primary inventory.</p>
    <p v-if="p.asset_type === 'substation_polygon'" class="filter-note">Overview symbols represent this same polygon record. Zooming changes its display, not the inventory count.</p>
    <dl class="detail-fields">
      <div><dt>Original name</dt><dd>{{ formatValue(p.name) }}</dd></div><div><dt>Reference</dt><dd>{{ formatValue(p.ref) }}</dd></div>
      <div><dt>OSM source ID</dt><dd class="mono">{{ p.source_id }}</dd></div><div><dt>Source layer</dt><dd class="mono">{{ p.source_layer }}</dd></div>
      <div><dt>Original geometry</dt><dd>{{ feature.geometry.type }}{{ p.asset_type === 'substation_point' ? ' · original source location' : '' }}</dd></div>
      <div><dt>Operator</dt><dd>{{ formatValue(p.operator) }}</dd></div>
      <template v-if="p.asset_type === 'power_plant'">
        <div><dt>Energy source tag</dt><dd>{{ formatValue(p.plant_source) }}</dd></div>
        <div><dt>Generation method tag</dt><dd>{{ formatValue(p.plant_method) }}</dd></div>
        <div><dt>Source output</dt><dd>{{ formatValue(p.plant_output_raw) }}<small>Unit unspecified in this export; not assumed MW or verified capacity.</small></dd></div>
        <div><dt>Source start date</dt><dd>{{ formatValue(p.plant_start_date_raw) }}<small>Original source string; not verified COD.</small></dd></div>
        <div><dt>English name tag</dt><dd>{{ formatValue(p.plant_name_en) }}</dd></div>
        <div><dt>Description</dt><dd>{{ formatValue(p.plant_description) }}</dd></div>
        <div><dt>Wikidata tag</dt><dd>{{ formatValue(p.plant_wikidata) }}</dd></div>
      </template>
      <template v-else>
      <div><dt>Maximum source voltage</dt><dd>{{ formatValue(p.max_voltage_v) }}{{ p.max_voltage_v === null ? '' : ' V' }}</dd></div>
      <div><dt>Raw voltage tags</dt><dd>{{ formatValue(p.voltages_raw) }}</dd></div><div><dt>Parsed voltage tags</dt><dd>{{ p.all_voltages_kv.length ? p.all_voltages_kv.join(' / ') + ' kV' : 'Not available' }}</dd></div>
      <div><dt>Original substation type</dt><dd>{{ formatValue(p.substation_type) }}</dd></div><div><dt>Location tag</dt><dd>{{ formatValue(p.location) }}</dd></div><div><dt>Circuits</dt><dd>{{ formatValue(p.circuits) }}</dd></div>
      </template>
      <div><dt>OSM tag status</dt><dd>{{ STATUS_LABELS[p.osm_tag_status] }}</dd></div><div><dt>Construction / disused</dt><dd>{{ formatValue(p.construction) }} / {{ formatValue(p.disused) }}</dd></div>
      <template v-if="p.asset_type === 'substation_point'">
        <div><dt>Matching QA</dt><dd>No plausible polygon correspondence under the matching policy. Physical-station identity remains unverified.</dd></div>
        <div><dt>Nearest source polygon</dt><dd class="mono">{{ p.nearest_polygon_feature_id }}</dd></div>
        <div><dt>QA distance to polygon</dt><dd>{{ p.nearest_polygon_distance_m?.toFixed(1) }} m<small>Screening distance; proximity does not establish a connection or shared voltage.</small></dd></div>
        <div><dt>Matching policy version</dt><dd>{{ p.matching_version }}</dd></div>
      </template>
      <div v-if="p.asset_type === 'transmission_line'"><dt>Mapped geometry length</dt><dd>{{ p.mapped_geometry_length_km === null ? 'Not available' : p.mapped_geometry_length_km.toFixed(2) + ' km' }}<small>WGS84 geodesic measurement; not official circuit-km.</small></dd></div>
      <div><dt>Official region / power system</dt><dd>Not available</dd></div><div><dt>Verified COD / capacity / AIS–GIS</dt><dd>Not available</dd></div>
    </dl>
    </div>
  </aside>
</template>
