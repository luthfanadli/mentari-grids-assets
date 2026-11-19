<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import type { AssetFeature, AssetFilters, InventorySummary, OsmStatus } from '../types/assets'
import type { PlanningCatalog, PlanningKind, PlanFilters, ProjectFeature } from '../types/planning'
import { VOLTAGES } from '../utils/filterAssets'
import { STATUS_LABELS, VOLTAGE_COLORS, formatNumber } from '../utils/formatAssets'
import { polygonStyleState } from '../utils/substationPresentation'
import { isProject } from '../utils/planning'
import PlanFilterFields from './PlanFilterFields.vue'

const filters = defineModel<AssetFilters>({ required: true })
const planningLayers = defineModel<PlanningKind[]>('planningLayers', { required: true })
const planFilters = defineModel<PlanFilters>('planFilters', { required: true })
const props = defineProps<{
  summary: InventorySummary | null; catalog: PlanningCatalog | null; catalogError: string
  features: AssetFeature[]; projects: ProjectFeature[]; mappedProjectCount: number; overview: boolean; busy: boolean
  reviewLoading: boolean; reviewError: string; pointLoading: boolean; pointError: string
  planLoading: Partial<Record<PlanningKind, boolean>>; planErrors: Partial<Record<PlanningKind, string>>
}>()
const emit = defineEmits<{
  reset: []; retryReview: []; retryPoints: []; retryProject: [kind: PlanningKind]; retryCatalog: []
  select: [record: AssetFeature | ProjectFeature]; summary: []; plans: []
}>()
const sections = [
  { title: 'Transmission', kind: 'transmission', key: 'lines', dataset: 'lines', label: 'Mapped lines', plan: 'Line projects' },
  { title: 'Substations', kind: 'substations', key: 'primary', dataset: 'primary', label: 'Primary substations', plan: 'Substation projects' },
  { title: 'Generation', kind: 'generators', key: 'powerPlants', dataset: 'power_plants', label: 'Power-plant footprints', plan: 'Generation projects' },
] as const
const statuses: OsmStatus[] = ['not_flagged_in_osm', 'tagged_construction', 'tagged_disused']
const desktop = window.matchMedia('(min-width: 761px)')
const opened = ref(desktop.matches)
const toggleButton = ref<HTMLButtonElement>()
const searchInput = ref<HTMLInputElement>()
const styles = computed(() => polygonStyleState(props.features))
const resultCount = computed(() => props.features.length + props.projects.length)
const suggestions = computed(() => filters.value.query.trim() ? [...props.features.slice(0, 4), ...props.projects.slice(0, 4)].slice(0, 4) : [])
function adapt(event: MediaQueryListEvent) { opened.value = event.matches }
function close(restoreFocus = false) {
  opened.value = false
  if (restoreFocus) void nextTick(() => toggleButton.value?.focus({ preventScroll: true }))
}
function open() {
  opened.value = true
  void nextTick(() => searchInput.value?.focus({ preventScroll: true }))
}
function escape(event: KeyboardEvent) {
  if (!opened.value || event.key !== 'Escape' || event.isComposing || !event.target) return
  if (!(event.target instanceof Element) || !event.target.closest('.map-frame') || event.target.closest('.map-details, .basemap-picker')) return
  if (event.target === searchInput.value && filters.value.query) return
  event.preventDefault()
  close(true)
}
function closeOnMobile() { if (!desktop.matches) close() }
function select(record: AssetFeature | ProjectFeature) { closeOnMobile(); emit('select', record) }
defineExpose({ closeOnMobile, open })
onMounted(() => { desktop.addEventListener('change', adapt); document.addEventListener('keydown', escape) })
onBeforeUnmount(() => { desktop.removeEventListener('change', adapt); document.removeEventListener('keydown', escape) })
</script>

<template>
  <aside class="map-layers" :class="{ expanded: opened }" aria-label="Layer sidebar">
    <button v-if="!opened" ref="toggleButton" class="reopen-layers" aria-label="Open map layers" aria-controls="map-layers-panel" :aria-expanded="false" @click="open">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round" aria-hidden="true"><path d="m3 8 9-5 9 5-9 5zM3 12l9 5 9-5M3 16l9 5 9-5"/></svg>Layers
    </button>
    <div v-show="opened" id="map-layers-panel" class="layers-panel" role="region" aria-label="Map layers">
      <div class="layers-heading">
        <h2>Map layers</h2>
        <div class="layers-heading-actions">
          <button type="button" class="outline-button" @click="emit('reset')">Reset filters</button>
          <button type="button" class="icon-button" aria-label="Collapse map layers" aria-controls="map-layers-panel" :aria-expanded="opened" @click="close(true)">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><rect x="3.5" y="4" width="17" height="16" rx="2"/><path d="M9 4v16m7-11-3 3 3 3"/></svg>
          </button>
        </div>
      </div>
      <div class="layers-body">
        <div class="sidebar-search">
          <label class="search-box"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><circle cx="10" cy="10" r="6"/><path d="m15 15 5 5"/></svg>
            <span class="sr-only">Search visible layers</span><input ref="searchInput" v-model="filters.query" type="search" placeholder="Search by name or ID…"/>
          </label>
          <div v-if="suggestions.length" class="search-results">
            <button v-for="record in suggestions" :key="record.id" @click="select(record)">
              <strong>{{ isProject(record) ? record.properties.name : record.properties.display_name }}</strong>
              <small>{{ isProject(record) ? record.properties.source : record.properties.source_layer.replaceAll('_', ' ') }} · {{ isProject(record) ? record.properties.id : record.properties.source_id }}</small>
            </button>
            <button v-if="features.length > 4" class="text-button" @click="emit('summary')">Browse inventory results</button>
            <button v-if="projects.length && resultCount > 4" class="text-button" @click="emit('plans')">Browse project results</button>
          </div>
          <p v-if="!busy && !resultCount" class="layers-empty" role="status">No records match these filters.</p>
          <p v-else-if="!busy && !features.length && !mappedProjectCount" class="layers-empty" role="status">The matching projects have no drawable route.</p>
        </div>
        <details v-for="section in sections" :key="section.kind" class="asset-group" open>
          <summary><span>{{ section.title }}</span><i class="chevron" aria-hidden="true"></i></summary>
          <div class="group-rows">
            <label class="layer-row"><input v-model="filters[section.key]" type="checkbox"/>
              <span class="layer-key" :class="[section.key, { round: section.key === 'primary' && overview, overview, construction: section.key === 'primary' ? styles.constructionPrimary && !styles.primary : section.key === 'powerPlants' && styles.constructionPlants && !styles.plants }]" aria-hidden="true"></span>
              <span>{{ section.label }}</span><small aria-hidden="true">{{ summary ? formatNumber(summary.datasets[section.dataset].count) : '…' }}</small>
            </label>
            <label class="layer-row"><input v-model="planningLayers" type="checkbox" :value="section.kind"/>
              <span class="layer-key planned" :class="section.kind" aria-hidden="true"></span><span>{{ section.plan }}</span><small aria-hidden="true">{{ catalog ? formatNumber(catalog.datasets[section.kind].count) : '…' }}</small>
            </label>
            <p v-if="planningLayers.includes(section.kind) && planLoading[section.kind]" class="layers-note" role="status">Loading projects…</p>
            <p v-if="planningLayers.includes(section.kind) && planErrors[section.kind]" class="layers-error" role="alert">{{ planErrors[section.kind] }} <button class="text-button" @click="emit('retryProject', section.kind)">Retry projects</button></p>
            <details v-if="section.kind === 'substations'" class="candidate-group">
              <summary>Review candidates<i class="chevron" aria-hidden="true"></i></summary>
              <label class="layer-row"><input v-model="filters.review" type="checkbox"/><i class="layer-key review" :class="{ round: overview }" aria-hidden="true"></i><span>Review polygons</span><small aria-hidden="true">{{ summary?.datasets.review.count }}</small></label>
              <p v-if="reviewLoading && filters.review" class="layers-note" role="status">Loading polygons…</p>
              <p v-if="reviewError && filters.review" class="layers-error" role="alert">{{ reviewError }} <button class="text-button" @click="emit('retryReview')">Retry polygons</button></p>
              <label class="layer-row"><input v-model="filters.pointCandidates" type="checkbox"/><i class="layer-key point" aria-hidden="true"></i><span>Point-only candidates</span><small aria-hidden="true">{{ summary?.datasets.point_candidates.count }}</small></label>
              <p v-if="pointLoading && filters.pointCandidates" class="layers-note" role="status">Loading points…</p>
              <p v-if="pointError && filters.pointCandidates" class="layers-error" role="alert">{{ pointError }} <button class="text-button" @click="emit('retryPoints')">Retry point candidates</button></p>
              <p class="layers-note">Review required. Point voltages are unknown.</p>
            </details>
          </div>
        </details>
        <details class="asset-group" open><summary>Grid voltage<i class="chevron" aria-hidden="true"></i></summary>
          <div class="voltage-options">
            <label v-for="v in VOLTAGES" :key="v"><input v-model="filters.voltages" type="checkbox" :value="v"/><i class="voltage-key" :style="{ background: VOLTAGE_COLORS[v] }" aria-hidden="true"></i>{{ v }} kV</label>
          </div>
          <label v-if="filters.review || filters.pointCandidates" class="layer-row unknown-voltage"><input v-model="filters.unknownVoltage" type="checkbox"/>Unknown voltage</label>
        </details>
        <details class="asset-group"><summary>OSM status<i class="chevron" aria-hidden="true"></i></summary>
          <div class="group-rows"><label v-for="status in statuses" :key="status" class="layer-row"><input v-model="filters.statuses" type="checkbox" :value="status"/><i class="status-key" :class="status" aria-hidden="true"></i>{{ STATUS_LABELS[status] }}</label><p class="layers-note">Operation is unverified.</p></div>
        </details>
        <details class="asset-group"><summary>Plan filters<i class="chevron" aria-hidden="true"></i></summary>
          <PlanFilterFields v-if="catalog" v-model="planFilters" :options="catalog.filters"/>
          <p v-else-if="catalogError" class="layers-error" role="alert">{{ catalogError }} <button class="text-button" @click="emit('retryCatalog')">Retry catalogue</button></p>
          <p v-else class="layers-note">Loading plan filters…</p>
        </details>
      </div>
      <div class="layers-footer"><span v-if="busy" role="status">Loading layers…</span><span v-else>{{ formatNumber(features.length) }} OSM · {{ formatNumber(mappedProjectCount) }} mapped {{ mappedProjectCount === 1 ? 'project' : 'projects' }}</span></div>
    </div>
  </aside>
</template>
