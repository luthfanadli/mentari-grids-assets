<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref } from 'vue'
import type { InventorySummary } from '../types/assets'
import { formatNumber } from '../utils/formatAssets'
defineProps<{ summary: InventorySummary | null }>()
const emit = defineEmits<{ close: [] }>()
const dialog = ref<HTMLDialogElement | null>(null)
onMounted(() => dialog.value?.showModal())
onBeforeUnmount(() => dialog.value?.close())
</script>
<template>
  <dialog ref="dialog" class="provenance-dialog" aria-labelledby="about-title" @close="emit('close')" @click="event => { if (event.target === dialog) dialog?.close() }">
    <div class="drawer-heading"><span class="eyebrow">PROVENANCE & COVERAGE</span><button class="icon-button" aria-label="Close about data" @click="dialog?.close()"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true" focusable="false"><path d="m6 6 12 12M18 6 6 18"/></svg></button></div>
    <h2 id="about-title">A starting point for the grid inventory.</h2>
    <p>This Deliverable 2 workspace presents a preliminary inventory from <a href="https://openinframap.org/" target="_blank" rel="noopener">OpenInfraMap</a> / <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a></p>
    <div class="about-callout"><strong>Not flagged does not mean operational.</strong><p>Construction and disused flags reflect the source export. Primary substations have explicit transmission tags; candidate polygons need manual validation.</p></div>
    <p v-if="summary">The published subsets contain {{ formatNumber(summary.datasets.lines.count) }} mapped line segments, {{ formatNumber(summary.datasets.primary.count) }} primary polygons and {{ formatNumber(summary.datasets.review.count) }} separate review candidates. Lines are selected by their numeric maximum voltage, in volts, at 70 / 150 / 275 / 500 kV.</p>
    <p v-if="summary">Point matching compared all {{ formatNumber(summary.raw_counts.power_substation_point ?? 0) }} source points against all {{ formatNumber(summary.raw_counts.power_substation_polygon ?? 0) }} polygons: {{ summary.substation_point_matching.classifications.matched }} supported matches, {{ summary.substation_point_matching.classifications.uncertain }} uncertain records and {{ summary.substation_point_matching.classifications.distinct_point_only_candidate }} distinct candidates under the screening policy. {{ summary.datasets.point_candidates.count }} eligible point-only candidates are available separately, off by default; their voltage, function and physical identity are unverified. Intersection alone never establishes duplication.</p>
    <p>At overview scales, representative symbols locate polygon records; at zoom 10 and above, the original footprints are shown. Symbols add no inventory records. Matched and uncertain source points are withheld from the separate point layer to avoid counting possible shared locations again.</p>
    <p v-if="summary">Power plants add {{ formatNumber(summary.datasets.power_plants.count) }} original source footprints as generation context, separate from transmission assets. Diamonds represent the same footprints below zoom 10; local zoom shows original boundaries. Source energy/method/output/start-date tags are unverified. The export supplies no voltage or output unit; output is not assumed MW, and start dates are not verified COD.</p>
    <h3>What is still missing</h3><p>Authoritative RUPTL 2025–2034 / RUKN 2025–2060 planned projects, official region and power-system grouping, verified HVDC and converter stations, COD, MVA, official circuit-km, thermal ratings and AIS/GIS classification. No planned spatial records have been created. All point-only candidate voltages remain unknown in this source.</p>
    <p>Source data vintage: <strong>unknown</strong>. Counts represent mapped features; cross-layer duplicates, network topology and national completeness have not been verified.</p>
  </dialog>
</template>
