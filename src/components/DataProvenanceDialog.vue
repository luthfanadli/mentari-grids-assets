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
    <div class="drawer-heading"><span class="eyebrow">PROVENANCE & COVERAGE</span><button class="icon-button" aria-label="Close about data" @click="dialog?.close()">×</button></div>
    <h2 id="about-title">A starting point for the grid inventory.</h2>
    <p>This Deliverable 2 workspace presents a preliminary inventory from <a href="https://openinframap.org/" target="_blank" rel="noopener">OpenInfraMap</a> / <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a>. It is not an approved PLN or DJK ESDM asset registry.</p>
    <div class="about-callout"><strong>Not flagged does not mean operational.</strong><p>Construction and disused flags reflect the source export. Primary substations have explicit transmission tags; candidate polygons need manual validation.</p></div>
    <p v-if="summary">The published subsets contain {{ formatNumber(summary.datasets.lines.count) }} mapped line segments, {{ formatNumber(summary.datasets.primary.count) }} primary polygons and {{ formatNumber(summary.datasets.review.count) }} separate review candidates. Lines are selected by their numeric maximum voltage, in volts, at 70 / 150 / 275 / 500 kV.</p>
    <p v-if="summary">Point matching compared all {{ formatNumber(summary.raw_counts.power_substation_point ?? 0) }} source points against all {{ formatNumber(summary.raw_counts.power_substation_polygon ?? 0) }} polygons: {{ summary.substation_point_matching.classifications.matched }} supported matches, {{ summary.substation_point_matching.classifications.uncertain }} uncertain records and {{ summary.substation_point_matching.classifications.distinct_point_only_candidate }} distinct candidates under the screening policy. {{ summary.datasets.point_candidates.count }} eligible point-only candidates are available separately, off by default; their voltage, function and physical identity are unverified. Intersection alone never establishes duplication.</p>
    <p>At overview scales, representative symbols locate polygon records; at zoom 10 and above, the original footprints are shown. Symbols add no inventory records. Matched and uncertain source points are withheld from the separate point layer to avoid counting possible shared locations again.</p>
    <h3>What is still missing</h3><p>Authoritative RUPTL 2025–2034 / RUKN 2025–2060 planned projects, official region and power-system grouping, verified HVDC and converter stations, COD, MVA, official circuit-km, thermal ratings and AIS/GIS classification. No planned spatial records have been created. All point-only candidate voltages remain unknown in this source.</p>
    <p>Source data vintage: <strong>unknown</strong>. Counts represent mapped features; cross-layer duplicates, network topology and national completeness have not been verified.</p>
    <h3>Download the published derivative database</h3>
    <p>Contains information from OpenStreetMap, made available under the <a href="https://opendatacommons.org/licenses/odbl/1-0/" target="_blank" rel="noopener">Open Database License (ODbL) 1.0</a>. The complete published derivative is available below, without a login. Retain the attribution and ODbL notices when reusing it.</p>
    <div class="download-links"><a href="/data/transmission-lines.geojson" download>Line segments ↗</a><a href="/data/substations-primary.geojson" download>Primary polygons ↗</a><a href="/data/substations-review.geojson" download>Review polygons ↗</a><a href="/data/substations-point-candidates.geojson" download>Point-only candidates ↗</a><a href="/data/substation-display-points.geojson" download>Representative symbols (display only) ↗</a><a href="/data/data-catalog.json" target="_blank" rel="noopener">Data catalog ↗</a><a href="/data/qa-report.json" target="_blank" rel="noopener">QA report ↗</a><a href="/data/summary.json" target="_blank" rel="noopener">Summary ↗</a></div>
    <p class="filter-note">Processing: exact tag filters, stable original IDs, seven decimal coordinate precision, no dissolve or geometry simplification. Geodesic lengths describe mapped line geometry only. Basemap choices include OpenStreetMap, Google Satellite and a plain background. Imagery provides visual context; the inventory remains OSM-based with unverified operational status. Basemap and inventory attribution are shown separately.</p>
    <p v-if="summary" class="version-label">VERSION {{ summary.data_version }}</p>
  </dialog>
</template>
