<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import type { AssetFeature, AssetFilters, OsmStatus } from '../types/assets'
import { VOLTAGES } from '../utils/filterAssets'
import { STATUS_LABELS, VOLTAGE_COLORS } from '../utils/formatAssets'
import { polygonStyleState } from '../utils/substationPresentation'

const filters = defineModel<AssetFilters>({ required: true })
const props = defineProps<{
  overview: boolean; features: AssetFeature[]
  reviewLoading: boolean; reviewError: string; pointLoading: boolean; pointError: string
}>()
const emit = defineEmits<{ reset: []; retryReview: []; retryPoints: [] }>()
const root = ref<HTMLElement | null>(null), button = ref<HTMLButtonElement | null>(null)
const opened = ref(false)
const styles = computed(() => polygonStyleState(props.features))
const statuses: OsmStatus[] = ['not_flagged_in_osm', 'tagged_construction', 'tagged_disused']

async function toggle() {
  if (opened.value) { close(true); return }
  opened.value = true
  await nextTick()
  root.value?.querySelector<HTMLInputElement>('input')?.focus({ preventScroll: true })
}
function close(restoreFocus = false) {
  opened.value = false
  if (restoreFocus) button.value?.focus({ preventScroll: true })
}
function isMapTarget(target: EventTarget | null) {
  return target instanceof Node && !!root.value?.closest('.map-card')?.contains(target)
}
function dismissOutsideMap(event: PointerEvent | FocusEvent) {
  if (!opened.value) return
  const basemap = event.target instanceof Element && event.target.closest('.basemap-picker')
  // Map gestures and navigation keep Layers available; opening another map menu dismisses it.
  if (!isMapTarget(event.target) || basemap) close()
}
function escape(event: KeyboardEvent) {
  if (!opened.value || event.key !== 'Escape' || event.isComposing) return
  if (event.target instanceof Element && event.target.closest('.map-details, dialog, .basemap-picker')) return
  event.preventDefault()
  event.stopPropagation()
  close(true)
}
function focusWithinPanel(event: PointerEvent) {
  const target = event.target as Element
  if (target.closest('input, button, summary, a')) return
  // A label's text otherwise focuses the outer <main> before native activation.
  event.preventDefault()
  const input = target.closest('label')?.querySelector<HTMLInputElement>('input')
  const control = input ?? event.currentTarget as HTMLElement
  control.focus({ preventScroll: true })
}
onMounted(() => {
  document.addEventListener('pointerdown', dismissOutsideMap)
  document.addEventListener('focusin', dismissOutsideMap)
  document.addEventListener('keydown', escape, true)
})
onBeforeUnmount(() => {
  document.removeEventListener('pointerdown', dismissOutsideMap)
  document.removeEventListener('focusin', dismissOutsideMap)
  document.removeEventListener('keydown', escape, true)
})
</script>

<template>
  <section ref="root" class="map-layers" aria-label="Map layer controls">
    <button ref="button" class="layers-toggle" aria-label="Layers" aria-haspopup="dialog" aria-controls="map-layers-panel" :aria-expanded="opened" :title="opened ? 'Close layers' : 'Show layers'" @click="toggle">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" aria-hidden="true"><path d="m3 8 9-5 9 5-9 5zM3 12l9 5 9-5M3 16l9 5 9-5"/></svg>
      <span>Layers</span>
      <svg class="layers-chevron" :class="{ rotated: opened }" width="13" height="13" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="m5 8 5 5 5-5"/></svg>
    </button>

    <div v-if="opened" id="map-layers-panel" class="layers-panel" role="dialog" aria-label="Map layers" tabindex="-1" @pointerdown="focusWithinPanel" @wheel.stop>
      <div class="layers-heading">
        <strong>Map layers</strong>
        <button class="text-button" @click="emit('reset')">Reset</button>
        <button class="icon-button" aria-label="Close layers" title="Close layers" @click="close(true)"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18"/></svg></button>
      </div>
      <div class="layers-body">
        <p v-if="!features.length" class="layers-empty" role="status">No matching records. Adjust layers or filters.</p>
        <fieldset class="asset-layer-list">
          <legend class="sr-only">Asset layers</legend>
          <label class="layer-row"><input v-model="filters.lines" type="checkbox"/><span class="symbol-pair" aria-hidden="true"><i class="layer-key line-key"></i></span><span>Transmission lines</span></label>
          <label class="layer-row"><input v-model="filters.primary" type="checkbox" :aria-description="styles.constructionPrimary ? 'Amber symbols mark construction-tagged substations.' : undefined"/><span class="symbol-pair" aria-hidden="true"><i class="layer-key primary-key" :class="{ round: overview, 'construction-primary-sample': styles.constructionPrimary && !styles.primary }"></i><i v-if="styles.constructionPrimary && styles.primary" class="layer-key primary-key extra-key construction-primary-sample" :class="{ round: overview }" title="Construction-tagged substation"></i></span><span>Primary substations</span></label>
          <label class="layer-row"><input v-model="filters.powerPlants" type="checkbox"/><span class="symbol-pair" aria-hidden="true"><i class="layer-key plant-key" :class="{ diamond: overview, 'construction-plant-key': styles.constructionPlants && !styles.plants }"></i><i v-if="styles.constructionPlants && styles.plants" class="layer-key plant-key extra-key construction-plant-key" :class="{ diamond: overview }" title="Construction-tagged plant"></i></span><span>Power plants</span></label>
          <p class="candidate-label">Optional candidates</p>
          <label class="layer-row"><input v-model="filters.review" type="checkbox"/><span class="symbol-pair" aria-hidden="true"><i class="layer-key review-key" :class="{ round: overview }"></i></span><span>Review polygons</span></label>
          <p v-if="reviewLoading && filters.review" class="layers-note" role="status">Loading review polygons…</p>
          <div v-if="reviewError && filters.review" class="layers-error" role="alert">{{ reviewError }} <button class="text-button" @click="emit('retryReview')">Retry review polygons</button></div>
          <label class="layer-row"><input v-model="filters.pointCandidates" type="checkbox"/><span class="symbol-pair" aria-hidden="true"><i class="layer-key point-key"></i></span><span>Point-only candidates</span></label>
          <p v-if="pointLoading && filters.pointCandidates" class="layers-note" role="status">Loading point candidates…</p>
          <div v-if="pointError && filters.pointCandidates" class="layers-error" role="alert">{{ pointError }} <button class="text-button" @click="emit('retryPoints')">Retry point candidates</button></div>
          <p class="layers-note candidate-note">Unvalidated. Point voltages are unknown.</p>
        </fieldset>

        <details class="layer-filter-group">
          <summary><span>Voltage</span><span class="group-value">{{ filters.voltages.length === VOLTAGES.length ? 'All levels' : `${filters.voltages.length} levels` }}</span><span class="group-chevron" aria-hidden="true">›</span></summary>
          <fieldset>
            <legend class="sr-only">Voltage</legend>
            <label v-for="voltage in VOLTAGES" :key="voltage" class="filter-row"><input v-model="filters.voltages" type="checkbox" :value="voltage" :aria-label="`${voltage} kV`"/><i class="voltage-key" :style="{ background: VOLTAGE_COLORS[voltage] }" aria-hidden="true"></i><span>{{ voltage }} kV</span></label>
            <label v-if="filters.review || filters.pointCandidates" class="filter-row"><input v-model="filters.unknownVoltage" type="checkbox"/><span>Unknown voltage</span></label>
            <p class="layers-note">Lines and substations. Colors apply to lines.</p>
          </fieldset>
        </details>
        <details class="layer-filter-group">
          <summary><span>OSM status</span><span class="group-value">{{ filters.statuses.length }} selected</span><span class="group-chevron" aria-hidden="true">›</span></summary>
          <fieldset>
            <legend class="sr-only">OSM status</legend>
            <label v-for="status in statuses" :key="status" class="filter-row"><input v-model="filters.statuses" type="checkbox" :value="status"/><i class="status-key" :class="status" aria-hidden="true"></i><span>{{ STATUS_LABELS[status] }}</span></label>
            <p class="layers-note">Source tags; operation unverified.</p>
          </fieldset>
        </details>
      </div>
    </div>
  </section>
</template>

<style scoped>
.map-layers { position: absolute; z-index: 5; top: 14px; bottom: 36px; left: 14px; width: 288px; max-width: calc(100% - 28px); display: flex; flex-direction: column; align-items: flex-start; gap: 8px; pointer-events: none; color: var(--ink) }
.layers-toggle { flex: none; display: flex; align-items: center; gap: 8px; min-height: 38px; padding: 8px 11px; border: 1px solid var(--border); border-radius: 7px; background: #fffffff5; box-shadow: var(--shadow-soft); color: var(--ink-strong); font-size: 11px; font-weight: 650; pointer-events: auto }
.layers-toggle:hover, .layers-toggle[aria-expanded=true] { background: var(--surface-blue); border-color: var(--border-strong) }
.layers-chevron { transition: transform 150ms var(--ease); margin-left: 3px }
.layers-chevron.rotated { transform: rotate(180deg) }
.layers-panel { flex: 0 1 auto; min-height: 0; width: 100%; display: flex; flex-direction: column; border: 1px solid var(--border); border-radius: 10px; background: var(--surface); box-shadow: 0 10px 30px #123b6826, 0 2px 6px #123b6810; overflow: hidden; pointer-events: auto; animation: surface-in 150ms var(--ease) }
.layers-heading { flex: none; display: flex; align-items: center; gap: 12px; padding: 9px 11px; border-bottom: 1px solid var(--border) }
.layers-heading strong { font-size: 12px; margin-right: auto }
.layers-heading .text-button { font-size: 11px; min-height: 30px }
.layers-heading .icon-button { width: 28px; height: 28px }
.layers-body { min-height: 0; padding: 6px 10px 8px; overflow-y: auto; overscroll-behavior: contain; scrollbar-gutter: stable }
fieldset { border: 0; padding: 0; margin: 0; min-width: 0 }
.layer-row, .filter-row { display: flex; align-items: center; gap: 9px; min-height: 32px; padding: 4px 6px; border-radius: 5px; font-size: 11px; line-height: 1.45; cursor: pointer }
.layer-row:hover, .filter-row:hover { background: var(--surface-soft) }
.layer-row:has(input:checked) { background: #edf3fb80 }
input { width: 15px; height: 15px; margin: 0; flex: none; accent-color: var(--brand-blue) }
.symbol-pair { position: relative; display: grid; place-items: center; width: 18px; height: 18px; flex: none }
.layer-key { display: block; width: 10px; height: 10px; flex: none }
.line-key { width: 16px; height: 2px; background: var(--muted); transform: rotate(-30deg) }
.primary-key { background: #086e66; border: 1px solid #075c55 }
.construction-primary-sample { background: #086e6666; border: 1px dashed #ac6910 }
.construction-primary-sample.round { background: #ac6910; border-style: solid }
.extra-key { position: absolute; right: -3px; bottom: -1px; width: 8px; height: 8px; box-shadow: 0 0 0 1px white }
.review-key { background: #fff7df; border: 1px dashed #b46c00 }
.review-key.round { border-style: solid }
.round, .point-key { border-radius: 50% }
.point-key { background: white; border: 2px solid #b8406a }
.plant-key { background: #d0203033; border: 1px solid #b72236 }
.plant-key.diamond { transform: rotate(45deg); background: #b72236; border-color: #fff }
.plant-styles.construction-plant-key { background: #fff9f0; border-color: #b72236; border-style: dashed }
.candidate-label { margin: 8px 6px 3px; padding-top: 8px; border-top: 1px solid var(--border); color: var(--muted); font-size: 10px; font-weight: 650 }
.layers-note { margin: 5px 6px 7px; color: var(--muted); font-size: 10px; line-height: 1.5 }
.candidate-note { margin-bottom: 10px }
.layers-empty { margin: 5px 6px 8px; padding: 8px; border-radius: 5px; background: var(--surface-blue); font-size: 11px; line-height: 1.5 }
.layers-error { margin: 4px 6px 8px; color: #9c592d; font-size: 11px; line-height: 1.6; overflow-wrap: anywhere }
.layers-error .text-button { font-size: 11px }
.layer-filter-group { border-top: 1px solid var(--border) }
summary { display: flex; align-items: center; gap: 8px; min-height: 38px; padding: 6px; list-style: none; cursor: pointer; font-size: 11px; font-weight: 650; border-radius: 4px }
summary::-webkit-details-marker { display: none }
summary:hover { background: var(--surface-soft) }
summary:focus-visible { outline: 2px solid #3271bc; outline-offset: -2px }
.group-value { margin-left: auto; font-size: 10px; font-weight: 400; color: var(--muted) }
.group-chevron { color: var(--muted); font-size: 20px; line-height: 1; transform: rotate(90deg); transition: transform 150ms var(--ease) }
details[open] .group-chevron { transform: rotate(-90deg) }
.layer-filter-group fieldset { padding-bottom: 5px }
.voltage-key { width: 18px; height: 3px; flex: none; border-radius: 1px }
.status-key { width: 18px; height: 0; flex: none; border-top: 2px solid var(--muted) }
.status-key.tagged_construction { border-top-style: dashed }
.status-key.tagged_disused { border-top-style: dotted }
@media(max-width:720px) { .map-layers { top: 10px; left: 10px; max-width: calc(100% - 20px) } .layer-row, .filter-row { min-height: 34px; font-size: 12px } }
@media(prefers-reduced-motion:reduce) { .layers-chevron, .group-chevron { transition: none } .layers-panel { animation: none } }
</style>
