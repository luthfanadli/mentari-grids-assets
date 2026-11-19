<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, shallowRef, watch } from 'vue'
import AppHeader, { type PageName } from './components/AppHeader.vue'
import MapLayersControl from './components/MapLayersControl.vue'
import InventorySummary from './components/InventorySummary.vue'
import MapCanvas from './components/MapCanvas.vue'
import AssetTable from './components/AssetTable.vue'
import AssetDetailsDrawer from './components/AssetDetailsDrawer.vue'
import DataProvenanceDialog from './components/DataProvenanceDialog.vue'
import ProjectRegister from './components/ProjectRegister.vue'
import ReportDialog from './components/ReportDialog.vue'
import { useAssetFilters } from './composables/useAssetFilters'
import { usePlanning } from './composables/usePlanning'
import { createAssetRepository } from './services/assetData'
import { defaultPlanFilters, isProject, projectKind } from './utils/planning'
import { VOLTAGES } from './utils/filterAssets'
import type { AssetFeature } from './types/assets'
import type { PlanningKind, ProjectFeature } from './types/planning'

const repository = createAssetRepository()
const { filters, summary, loading, error, reviewLoading, reviewError, pointLoading, pointError,
  selectedFeatures, selectedSymbols, counts, load, loadReview, loadPointCandidates, reset: resetInventory } = useAssetFilters(repository)
const { catalog, catalogError, enabled, criteria, loading: planLoading, errors: planErrors,
  matching, visible: projects, loadCatalog, loadAll, loadLayer, reset: resetPlanning } = usePlanning(repository, filters)
const aboutOpen = ref(false)
const main = ref<HTMLElement>()
const viewportCount = ref<number | null>(null), planViewport = ref<number | null>(null)
const sidebar = ref<InstanceType<typeof MapLayersControl>>()
const mapCanvas = ref<InstanceType<typeof MapCanvas>>()
const assetDetails = ref<InstanceType<typeof AssetDetailsDrawer>>()
const selected = shallowRef<AssetFeature | ProjectFeature | null>(null)
const selectedId = computed(() => selected.value ? String(selected.value.id) : null)
const mappedProjectCount = computed(() => projects.value.filter(project => project.geometry).length)
const busy = computed(() => loading.value || (reviewLoading.value && filters.value.review) ||
  (pointLoading.value && filters.value.pointCandidates) || enabled.value.some(k => planLoading[k]))
const colocated = computed(() => {
  const record = selected.value
  if (!record || !isProject(record) || record.geometry?.type !== 'Point') return []
  const [x, y] = record.geometry.coordinates
  return projects.value.filter(f => f.geometry?.type === 'Point' && f.geometry.coordinates[0] === x && f.geometry.coordinates[1] === y)
})

function readPage(): PageName {
  const hash = window.location.hash.slice(1)
  return hash === 'plans' || hash === 'summary' ? hash : 'map'
}
const page = ref<PageName>(readPage())
const visited = ref({ summary: false, plans: false })
function onHashChange() { page.value = readPage() }
function navigate(next: PageName) {
  page.value = next
  if (window.location.hash !== '#' + next) window.location.hash = next
}
function reset() { resetInventory(); resetPlanning() }
function clearRegisterFilters() {
  criteria.value = defaultPlanFilters()
  filters.value.query = ''
  filters.value.voltages = [...VOLTAGES]
  filters.value.unknownVoltage = true
}
async function select(record: AssetFeature | ProjectFeature) {
  const sameRecord = record.id === selected.value?.id
  if (isProject(record)) {
    const kind = projectKind(record)
    if (!enabled.value.includes(kind)) enabled.value = [...enabled.value, kind]
  }
  navigate('map')
  sidebar.value?.closeOnMobile()
  await nextTick()
  selected.value = record
  await nextTick()
  assetDetails.value?.focus()
  if (sameRecord) mapCanvas.value?.fitFeatures([record])
}
async function showMapFilters() {
  navigate('map')
  await nextTick()
  sidebar.value?.open()
}
async function showPlans(kinds: PlanningKind[]) {
  enabled.value = [...kinds]
  selected.value = null
  navigate('map')
  sidebar.value?.closeOnMobile()
  await nextTick()
  mapCanvas.value?.fitFeatures(projects.value)
}
function updateViewport(inventory: number | null, plans: number | null) {
  viewportCount.value = inventory
  planViewport.value = plans
}
watch(() => filters.value.review, on => { if (on) void loadReview() })
watch(() => filters.value.pointCandidates, on => { if (on) void loadPointCandidates() })
watch([selectedFeatures, projects], ([assets, plans]) => {
  if (selected.value && !assets.some(f => f.id === selectedId.value) && !plans.some(f => f.id === selectedId.value)) selected.value = null
})
watch(page, next => {
  if (next !== 'map') visited.value[next] = true
  if (next === 'plans') loadAll()
}, { immediate: true })
onMounted(() => {
  void load()
  void loadCatalog()
  window.addEventListener('hashchange', onHashChange)
})
onBeforeUnmount(() => window.removeEventListener('hashchange', onHashChange))
</script>

<template>
  <a class="skip-link" href="#main" @click.prevent="main?.focus()">Skip to content</a>
  <AppHeader :page="page" @navigate="navigate" @about="aboutOpen = true"/>
  <main id="main" ref="main" tabindex="-1">
    <div class="map-workspace">
      <h1 class="sr-only">Indonesia power map</h1>
      <MapCanvas ref="mapCanvas" :features="selectedFeatures" :projects="projects" :display-points="selectedSymbols" :selected-id="selectedId" @select="select" @viewport="updateViewport">
        <template #layers="{ overview }">
          <MapLayersControl ref="sidebar" v-model="filters" v-model:planning-layers="enabled" v-model:plan-filters="criteria"
            :summary="summary" :catalog="catalog" :catalog-error="catalogError" :overview="overview" :features="selectedFeatures" :projects="projects" :mapped-project-count="mappedProjectCount" :busy="busy"
            :review-loading="reviewLoading" :review-error="reviewError" :point-loading="pointLoading" :point-error="pointError"
            :plan-loading="planLoading" :plan-errors="planErrors" @reset="reset" @retry-review="loadReview" @retry-points="loadPointCandidates" @retry-project="loadLayer"
            @retry-catalog="loadCatalog" @select="select" @summary="navigate('summary')" @plans="navigate('plans')"/>
        </template>
        <template #status>
          <div v-if="error" class="map-data-status load-error" role="alert">{{ error }} <button class="text-button" @click="load">Retry inventory</button></div>
          <div v-else-if="loading" class="map-data-status" role="status">Loading mapped inventory…</div>
        </template>
        <template #details><AssetDetailsDrawer v-if="selected" ref="assetDetails" :feature="selected" :colocated="colocated" @select="select" @close="selected = null"/></template>
      </MapCanvas>
    </div>
  </main>
  <ReportDialog :view="page" @close="navigate('map')">
    <section v-if="visited.summary" v-show="page === 'summary'" class="report-panel" aria-label="Inventory summary">
      <div class="page-content">
        <div class="page-heading"><p>Selected OpenStreetMap records across Indonesia. Map filters apply.</p><button class="outline-button" @click="showMapFilters">Map filters</button></div>
        <InventorySummary :counts="counts" :summary="summary" :loading="loading || !!error"/>
        <div v-if="error" role="alert" class="load-error">{{ error }} <button class="text-button" @click="load">Retry inventory</button></div>
        <p v-else-if="loading" role="status">Loading mapped inventory…</p>
        <template v-else>
          <label class="search-box summary-search"><span class="sr-only">Search inventory records</span><input v-model="filters.query" type="search" placeholder="Search by name, reference, operator or ID…"/></label>
          <AssetTable :features="selectedFeatures" :selected-id="selectedId" :viewport-count="viewportCount" @select="select" @reset="reset"/>
        </template>
      </div>
    </section>
    <section v-if="visited.plans" v-show="page === 'plans'" class="report-panel" aria-label="Planning register">
      <ProjectRegister v-model:query="filters.query" v-model:criteria="criteria" :catalog="catalog" :catalog-error="catalogError"
        :matches="matching" :loading="planLoading" :errors="planErrors" :selected-count="mappedProjectCount" :viewport-count="planViewport" :voltages="filters.voltages"
        @select="select" @show="showPlans" @retry="loadLayer" @retry-catalog="loadCatalog" @reset="clearRegisterFilters"/>
    </section>
  </ReportDialog>
  <DataProvenanceDialog v-if="aboutOpen" :summary="summary" :catalog="catalog" @close="aboutOpen = false"/>
</template>
