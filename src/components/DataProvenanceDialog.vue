<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import type { InventorySummary } from '../types/assets'
import type { PlanningCatalog } from '../types/planning'
import { formatNumber } from '../utils/formatAssets'
const props = defineProps<{ summary: InventorySummary | null; catalog: PlanningCatalog | null }>()
const planTotals = computed(() => {
  if (!props.catalog) return null
  const datasets = Object.values(props.catalog.datasets)
  return {
    records: datasets.reduce((total, dataset) => total + dataset.count, 0),
    mapped: datasets.reduce((total, dataset) => total + dataset.mapped, 0),
  }
})
const emit = defineEmits<{ close: [] }>()
const dialog = ref<HTMLDialogElement>()
onMounted(() => dialog.value?.showModal())
</script>
<template>
  <dialog ref="dialog" class="provenance-dialog" aria-labelledby="about-title" @close="emit('close')" @click="event => { if (event.target === dialog) dialog?.close() }">
    <div class="dialog-inner">
      <div class="drawer-heading"><h2 id="about-title">About the data</h2><button class="icon-button" aria-label="Close about data" @click="dialog?.close()">×</button></div>
      <h3>Mapped inventory</h3>
      <p>MENTARI Grids shows Indonesian transmission segments, substation polygons and power-plant footprints from an OpenInfraMap export. Its OSM snapshot date is unknown. The default map shows records without construction or disused flags. Operation remains unverified.</p>
      <p v-if="summary">{{ formatNumber(summary.datasets.primary.count) }} substation polygons carry a transmission tag and a maximum voltage of 70, 150, 275 or 500 kV. The review layer contains {{ summary.datasets.review.count }} additional polygons. {{ summary.datasets.point_candidates.count }} source points have unknown voltage and can be inspected separately.</p>
      <p>At national scale, one symbol represents each selected footprint. Zoom in to see its boundary. Plant output units and official OSM asset identities remain unverified.</p>
      <p>© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a> · <a href="https://openinframap.org/">OpenInfraMap</a> · <a href="https://opendatacommons.org/licenses/odbl/1-0/">ODbL 1.0</a></p>
      <h3>Planning projects</h3>
      <p>The three supplied Indonesia Power Map files cite RUPTL 2025–2034 and RUKN 2025–2060. Each row describes a project or work item. Locations and routes are mapped by IPM. The details show the reported stage, target year, location confidence or route status, and source page when supplied.</p>
      <p v-if="planTotals">Map geometry is available for {{ formatNumber(planTotals.mapped) }} of {{ formatNumber(planTotals.records) }} projects. The register also lists transmission projects whose route has coincident vertices or is marked unavailable by the source.</p>
      <p><a href="https://indonesiapowermap.com/#data">Indonesia Power Map</a> · <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a>. The dashboard adds map identifiers and withholds unusable route geometries.</p>
      <h3>Comparison with Indonesia Power Map</h3>
      <p>IPM’s 15 November 2026 release lists 1,947 existing transmission entries, 1,158 substations and 3,199 generation entries. MENTARI counts OSM segments and footprints. For planning, the three supplied files match the IPM downloads byte for byte.</p>
      <p><a href="https://indonesiapowermap.com/#data">IPM open data</a> · <a href="https://indonesiapowermap.com/docs/publication_policy.md">IPM publication policy</a></p>
    </div>
  </dialog>
</template>
