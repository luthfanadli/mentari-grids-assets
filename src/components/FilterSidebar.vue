<script setup lang="ts">
import type { AssetFilters, OsmStatus } from '../types/assets'
import { VOLTAGES } from '../utils/filterAssets'
import { STATUS_LABELS, VOLTAGE_COLORS } from '../utils/formatAssets'
const filters = defineModel<AssetFilters>({ required: true })
defineProps<{ reviewLoading: boolean; reviewError: string; pointLoading: boolean; pointError: string }>()
defineEmits<{ reset: []; retryReview: []; retryPoints: [] }>()
const statuses: OsmStatus[] = ['not_flagged_in_osm', 'tagged_construction', 'tagged_disused']
</script>
<template>
  <aside class="filter-panel" aria-label="Inventory filters">
    <div class="panel-title"><h2>Filters</h2><button class="text-button" @click="$emit('reset')">Reset</button></div>
    <fieldset><legend>Layers</legend>
      <label class="check-row"><input v-model="filters.lines" type="checkbox"/><span>Transmission lines</span></label>
      <label class="check-row"><input v-model="filters.primary" type="checkbox"/><span>Primary substations</span></label>
      <label class="check-row"><input v-model="filters.powerPlants" type="checkbox"/><span>Power plants</span></label>
      <div class="candidate-options">
        <p class="candidate-heading">Optional candidates</p>
        <label class="check-row"><input v-model="filters.review" type="checkbox"/><i class="candidate-key review-key" aria-hidden="true"></i><span>Review polygons</span></label>
        <p v-if="reviewLoading" role="status" class="filter-note">Loading review polygons…</p><div v-if="reviewError && filters.review" class="inline-error" role="alert">{{ reviewError }} <button class="text-button" @click="$emit('retryReview')">Retry review polygons</button></div>
        <label class="check-row"><input v-model="filters.pointCandidates" type="checkbox"/><i class="candidate-key point-key" aria-hidden="true"></i><span>Point-only candidates</span></label>
        <p v-if="pointLoading" role="status" class="filter-note">Loading point candidates…</p><div v-if="pointError && filters.pointCandidates" class="inline-error" role="alert">{{ pointError }} <button class="text-button" @click="$emit('retryPoints')">Retry point candidates</button></div>
        <p class="filter-note">Unvalidated. Point voltages are unknown.</p>
      </div>
    </fieldset>
    <fieldset><legend>Voltage <span>kV</span></legend>
      <label v-for="voltage in VOLTAGES" :key="voltage" class="check-row"><input v-model="filters.voltages" type="checkbox" :value="voltage" :aria-label="`${voltage} kV`"/><span class="voltage-swatch" :style="{ background: VOLTAGE_COLORS[voltage] }"></span><span>{{ voltage }} kV</span></label>
      <label v-if="filters.review || filters.pointCandidates" class="check-row"><input v-model="filters.unknownVoltage" type="checkbox"/><span>Unknown voltage</span></label>
      <p class="filter-note">Lines and substations only.</p>
    </fieldset>
    <fieldset><legend>OSM status</legend><label v-for="status in statuses" :key="status" class="check-row"><input v-model="filters.statuses" type="checkbox" :value="status"/><span>{{ STATUS_LABELS[status] }}</span></label><p class="filter-note">Tags do not verify operation.</p></fieldset>
  </aside>
</template>
