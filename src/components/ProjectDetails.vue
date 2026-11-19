<script setup lang="ts">
import { computed } from 'vue'
import { planningLabels, type ProjectFeature } from '../types/planning'
import { projectKind } from '../utils/planning'
import { formatValue } from '../utils/formatAssets'

const props = defineProps<{ feature: ProjectFeature; colocated: ProjectFeature[] }>()
const emit = defineEmits<{ select: [record: ProjectFeature] }>()
const p = computed(() => props.feature.properties)
const kind = computed(() => projectKind(props.feature))
function choose(event: Event) {
  const project = props.colocated.find(f => f.id === (event.target as HTMLSelectElement).value)
  if (project) emit('select', project)
}
</script>
<template>
  <span class="asset-kind">{{ planningLabels[kind] }} · {{ p.source }}</span>
  <h2 id="detail-title">{{ p.name }}</h2>
  <div class="detail-badges"><span class="badge plan-badge">{{ p.status }}</span><span v-if="p.scope" class="badge">{{ p.scope }}</span></div>
  <p v-if="!feature.geometry" class="review-callout">No drawable route is available for this project.</p>
  <label v-if="colocated.length > 1" class="colocated">Projects at these coordinates ({{ colocated.length }})
    <select :value="feature.id" @change="choose"><option v-for="project in colocated" :key="project.id" :value="project.id">{{ project.properties.name }} · {{ project.properties.target_cod_year ?? 'Year unavailable' }} · {{ project.properties.id }}</option></select>
  </label>
  <dl class="detail-fields">
    <div><dt>Source project ID</dt><dd class="mono">{{ p.id }}</dd></div>
    <div v-if="p.site_id"><dt>Source site ID</dt><dd class="mono">{{ p.site_id }}</dd></div>
    <div><dt>Province / system</dt><dd>{{ formatValue(p.province) }} / {{ formatValue(p.system) }}</dd></div>
    <div><dt>Target COD year</dt><dd>{{ formatValue(p.target_cod_year) }}</dd></div>
    <div><dt>RE Base / ARED targets</dt><dd>{{ formatValue(p.cod_re_base) }} / {{ formatValue(p.cod_ared) }}</dd></div>
    <div v-if="kind !== 'generators'"><dt>Project voltage</dt><dd>{{ p.voltage_kv == null ? 'Not available' : p.voltage_kv + ' kV' }}</dd></div>
    <div v-if="p.voltage_label"><dt>Source voltage label</dt><dd>{{ p.voltage_label }}</dd></div>
    <div v-if="kind === 'substations'"><dt>Project capacity</dt><dd>{{ p.capacity_mva == null ? 'Not available' : p.capacity_mva + ' MVA' }}</dd></div>
    <template v-if="kind === 'generators'">
      <div><dt>Technology</dt><dd>{{ p.technology_label || p.type || p.technology || 'Not available' }}</dd></div>
      <div><dt>Project capacity</dt><dd>{{ p.capacity_mw == null ? 'Not available' : p.capacity_mw + ' MW' }}</dd></div>
      <div v-if="p.storage_mwh != null"><dt>Storage</dt><dd>{{ p.storage_mwh }} MWh</dd></div>
    </template>
    <template v-if="kind === 'transmission'">
      <div><dt>From / to (source)</dt><dd>{{ formatValue(p.from_substation) }} / {{ formatValue(p.to_substation) }}</dd></div>
      <div><dt>Route status</dt><dd>{{ formatValue(p.route_status) }}</dd></div>
      <div><dt>Line type / circuits</dt><dd>{{ formatValue(p.line_type) }} / {{ formatValue(p.circuits) }}</dd></div>
      <div v-if="p.length_km != null"><dt>Source length</dt><dd>{{ p.length_km }} km</dd></div>
      <div v-if="p.circuit_km != null"><dt>Source circuit length</dt><dd>{{ p.circuit_km }} circuit-km</dd></div>
    </template>
    <div><dt>Geometry source</dt><dd>{{ formatValue(p.geometry_source || p.location_source) }}</dd></div>
    <div v-if="p.location_confidence"><dt>Location confidence</dt><dd>{{ p.location_confidence }}</dd></div>
    <div v-if="p.ruptl_page || p.ruptl_row"><dt>Source page / row</dt><dd>{{ formatValue(p.ruptl_page) }} / {{ formatValue(p.ruptl_row) }}</dd></div>
  </dl>
</template>
