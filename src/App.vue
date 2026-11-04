<script setup lang="ts">
import { onMounted, ref, shallowRef, watch } from 'vue'
import AppHeader from './components/AppHeader.vue'
import FilterSidebar from './components/FilterSidebar.vue'
import InventorySummary from './components/InventorySummary.vue'
import MapCanvas from './components/MapCanvas.vue'
import AssetTable from './components/AssetTable.vue'
import AssetDetailsDrawer from './components/AssetDetailsDrawer.vue'
import DataProvenanceDialog from './components/DataProvenanceDialog.vue'
import { useAssetFilters } from './composables/useAssetFilters'
import type { AssetFeature } from './types/assets'
const { filters, summary, loading, error, reviewLoading, reviewError, pointLoading, pointError, selectedFeatures, selectedSymbols, counts, load, loadReview, loadPointCandidates, reset } = useAssetFilters()
const aboutOpen = ref(false), filtersOpen = ref(false), viewportCount = ref<number | null>(null)
const selected = shallowRef<AssetFeature | null>(null)
watch(() => filters.value.review, enabled => { if (enabled) void loadReview() })
watch(() => filters.value.pointCandidates, enabled => { if (enabled) void loadPointCandidates() })
watch(selectedFeatures, features => {
  viewportCount.value = null
  if (selected.value && !features.some(f => f.properties.feature_id === selected.value?.properties.feature_id)) selected.value = null
})
onMounted(load)
</script>
<template>
  <a class="skip-link" href="#main">Skip to inventory</a><AppHeader @about="aboutOpen = true"/>
  <main id="main" tabindex="-1">
    <section class="page-intro"><div><h1>Transmission asset inventory</h1></div></section>
    <div class="inventory-notice"><span class="notice-icon" aria-hidden="true">i</span><p><strong>Source tags, unverified operation.</strong> “Not flagged in OSM” does not confirm existing or operational status. Review candidates are separate.</p></div>
    <InventorySummary :counts="counts" :loading="loading"/>
    <div class="workspace-heading"><div><span class="eyebrow">EXPLORE THE INVENTORY</span><span class="workspace-rule"></span></div></div>
    <div class="search-toolbar"><label class="search-box"><svg width="19" height="19" viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="10" cy="10" r="6.5" stroke="currentColor" stroke-width="1.6"/><path d="m15 15 6 6" stroke="currentColor" stroke-width="1.6"/></svg><span class="sr-only">Search assets by name, reference, operator or OSM ID</span><input v-model="filters.query" type="search" placeholder="Search by name, reference, operator or OSM ID…"/></label><button class="outline-button mobile-filter-toggle" :aria-expanded="filtersOpen" aria-controls="filters" @click="filtersOpen = !filtersOpen">Filters {{ filtersOpen ? '−' : '+' }}</button><span class="search-hint">Search applies to the map and record list</span></div>
    <div v-if="loading" class="loading-state" role="status"><span class="loading-spinner"></span>Loading the published inventory…</div>
    <div v-else-if="error" class="error-state" role="alert"><h2>Inventory unavailable</h2><p>{{ error }}</p><button class="outline-button" @click="load">Retry inventory</button></div>
    <div v-else class="workspace"><FilterSidebar id="filters" v-model="filters" :class="{ 'filters-open': filtersOpen }" :summary="summary" :review-loading="reviewLoading" :review-error="reviewError" :point-loading="pointLoading" :point-error="pointError" @reset="reset" @retry-review="loadReview" @retry-points="loadPointCandidates"/><div class="workspace-main"><MapCanvas :features="selectedFeatures" :display-points="selectedSymbols" :selected-id="selected?.properties.feature_id ?? null" @select="feature => selected = feature" @viewport="count => viewportCount = count"/><AssetTable :features="selectedFeatures" :selected-id="selected?.properties.feature_id ?? null" :viewport-count="viewportCount" @select="feature => selected = feature" @reset="reset"/></div></div>
    <footer class="app-footer"><span>MENTARI Grids <span class="muted">/ Deliverable 2</span></span><p>Data: © <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap contributors</a> · <a href="https://openinframap.org/" target="_blank" rel="noopener">OpenInfraMap</a> · <a href="https://opendatacommons.org/licenses/odbl/1-0/" target="_blank" rel="noopener">ODbL 1.0</a></p><button class="text-button" @click="aboutOpen = true">Coverage & limitations ↗</button></footer>
  </main>
  <AssetDetailsDrawer v-if="selected" :feature="selected" @close="selected = null"/><DataProvenanceDialog v-if="aboutOpen" :summary="summary" @close="aboutOpen = false"/>
</template>
