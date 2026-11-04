<script setup lang="ts">
import type { AssetFilters, InventorySummary, OsmStatus } from '../types/assets'
import { VOLTAGES } from '../utils/filterAssets'
import { STATUS_LABELS, VOLTAGE_COLORS, formatNumber } from '../utils/formatAssets'
const filters = defineModel<AssetFilters>({ required: true })
defineProps<{ summary: InventorySummary | null; reviewLoading: boolean; reviewError: string; pointLoading: boolean; pointError: string }>()
defineEmits<{ reset: []; retryReview: []; retryPoints: [] }>()
const statuses: OsmStatus[] = ['not_flagged_in_osm', 'tagged_construction', 'tagged_disused']
</script>
<template>
  <aside class="filter-panel" aria-label="Inventory filters">
    <div class="panel-title"><h2>Refine inventory</h2><button class="text-button" @click="$emit('reset')">Reset</button></div>
    <fieldset><legend>Asset layers</legend>
      <label class="check-row"><input v-model="filters.lines" type="checkbox"/><span>Transmission lines</span><small>{{ summary ? formatNumber(summary.datasets.lines.count) : '—' }}</small></label>
      <label class="check-row"><input v-model="filters.primary" type="checkbox"/><span>Primary substations</span><small>{{ summary ? formatNumber(summary.datasets.primary.count) : '—' }}</small></label>
      <div class="candidate-control"><label class="check-row"><input v-model="filters.review" type="checkbox"/><span>Review candidates</span><small>{{ summary ? formatNumber(summary.datasets.review.count) : '—' }}</small></label><p>Unvalidated polygons. Excluded from primary inventory.</p></div>
      <p v-if="reviewLoading" role="status" class="filter-note">Loading review candidates…</p><div v-if="reviewError && filters.review" class="inline-error" role="alert">{{ reviewError }} <button class="text-button" @click="$emit('retryReview')">Retry candidates</button></div>
      <div class="candidate-control point-control"><label class="check-row"><input v-model="filters.pointCandidates" type="checkbox"/><span>Point-only candidates</span><small>{{ summary ? formatNumber(summary.datasets.point_candidates.count) : '—' }}</small></label><p>Separate source locations. Voltage, function and identity unverified.</p></div>
      <p v-if="pointLoading" role="status" class="filter-note">Loading point-only candidates…</p><div v-if="pointError && filters.pointCandidates" class="inline-error" role="alert">{{ pointError }} <button class="text-button" @click="$emit('retryPoints')">Retry point candidates</button></div>
    </fieldset>
    <fieldset><legend>Voltage level <span>kV</span></legend>
      <label v-for="voltage in VOLTAGES" :key="voltage" class="check-row"><input v-model="filters.voltages" type="checkbox" :value="voltage" :aria-label="`${voltage} kV`"/><span class="voltage-swatch" :style="{ background: VOLTAGE_COLORS[voltage] }"></span><span>{{ voltage }} kV</span><small>{{ summary ? formatNumber(summary.datasets.lines.voltage_kv[String(voltage)] ?? 0) : '—' }}</small></label>
      <label v-if="filters.review || filters.pointCandidates" class="check-row"><input v-model="filters.unknownVoltage" type="checkbox"/><span>Unknown voltage</span><small>Review only</small></label><p v-if="filters.pointCandidates" class="filter-note">Point-only candidates retain unknown voltage. Clear “Unknown voltage” to hide them.</p><p class="filter-note">Counts show all in-scope line segments, across OSM flags.</p>
    </fieldset>
    <fieldset><legend>OSM status tags</legend><label v-for="status in statuses" :key="status" class="check-row status-row"><input v-model="filters.statuses" type="checkbox" :value="status"/><span>{{ STATUS_LABELS[status] }}</span></label><p class="filter-note">“Not flagged” means no construction or disused flag. Operation is unverified.</p></fieldset>
  </aside>
</template>
