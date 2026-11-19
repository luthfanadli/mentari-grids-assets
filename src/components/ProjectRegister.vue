<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { planningKinds, planningLabels, type PlanningCatalog, type PlanningKind, type PlanFilters, type ProjectFeature } from '../types/planning'
import { formatNumber } from '../utils/formatAssets'
import { projectKind } from '../utils/planning'
import PlanFilterFields from './PlanFilterFields.vue'

const props = defineProps<{
  catalog: PlanningCatalog | null; catalogError: string; matches: Record<PlanningKind, ProjectFeature[]>
  loading: Partial<Record<PlanningKind, boolean>>; errors: Partial<Record<PlanningKind, string>>
  selectedCount: number; viewportCount: number | null; voltages: number[]
}>()
const query = defineModel<string>('query', { required: true })
const criteria = defineModel<PlanFilters>('criteria', { required: true })
const emit = defineEmits<{ select: [record: ProjectFeature]; show: [kinds: PlanningKind[]]; retry: [kind: PlanningKind]; retryCatalog: []; reset: [] }>()
const kind = ref<PlanningKind | ''>('')
const listOnly = ref(false)
const kinds = computed(() => kind.value ? [kind.value] : [...planningKinds])
const records = computed(() => kinds.value.flatMap(k => props.matches[k]).filter(f => !listOnly.value || !f.geometry))
const busy = computed(() => kinds.value.some(k => props.loading[k]))
const page = ref(1), pageSize = 20
const pages = computed(() => Math.max(1, Math.ceil(records.value.length / pageSize)))
const pageRows = computed(() => records.value.slice((page.value - 1) * pageSize, page.value * pageSize))
watch(records, () => { page.value = 1 })
function reset() { kind.value = ''; listOnly.value = false; emit('reset') }
</script>
<template>
  <div class="page-content">
    <div class="page-heading">
      <div><h1>Planning projects</h1><p>RUPTL 2025–2034 and RUKN 2025–2060 · Indonesia Power Map</p></div>
      <button class="primary-button" :disabled="busy || !records.some(f => f.geometry)" @click="emit('show', kinds)">Show results on map</button>
    </div>
    <section v-if="catalog" class="plan-totals" aria-label="Published planning records">
      <div v-for="item in planningKinds" :key="item"><span>{{ planningLabels[item] }}</span><strong>{{ formatNumber(catalog.datasets[item].count) }}</strong><small>{{ formatNumber(catalog.datasets[item].mapped) }} with map geometry</small></div>
    </section>
    <p v-if="catalogError" class="load-error" role="alert">{{ catalogError }} <button class="text-button" @click="emit('retryCatalog')">Retry catalogue</button></p>
    <div class="register-controls">
      <label class="register-search">Search projects<input v-model="query" type="search" placeholder="Name, ID, province or system…"/></label>
      <label>Project type<select v-model="kind"><option value="">All projects</option><option v-for="item in planningKinds" :key="item" :value="item">{{ planningLabels[item] }}</option></select></label>
      <PlanFilterFields v-if="catalog" v-model="criteria" :options="catalog.filters"/>
    </div>
    <div class="register-options">
      <label><input v-model="listOnly" type="checkbox"/>Only records without map geometry</label>
      <span v-if="voltages.length < 4">Grid voltage filter · {{ voltages.length ? voltages.join(' / ') + ' kV' : 'no levels selected' }}</span>
      <button class="text-button" @click="reset">Reset filters</button>
    </div>
    <p v-for="item in kinds.filter(k => errors[k])" :key="item" class="load-error" role="alert">{{ errors[item] }} <button class="text-button" @click="emit('retry', item)">Retry {{ planningLabels[item].toLowerCase() }}</button></p>
    <section class="asset-table-card" aria-labelledby="plan-records-heading" :aria-busy="busy">
      <div class="results-heading"><div><h2 id="plan-records-heading">Project register <span>{{ formatNumber(records.length) }}</span></h2><p>Each row is one project entry. Several works can share a site.</p></div>
        <span class="viewport-count">{{ formatNumber(selectedCount) }} selected for map<span v-if="viewportCount !== null"> · {{ formatNumber(viewportCount) }} in viewport</span></span>
      </div>
      <p v-if="busy" class="empty-state" role="status">Loading project records…</p>
      <div v-else-if="!records.length" class="empty-state">No projects match these filters.</div>
      <div v-else class="table-scroll"><table><thead><tr><th scope="col">Project</th><th scope="col">Stage</th><th scope="col">Target COD</th><th scope="col">Province</th></tr></thead>
        <tbody><tr v-for="record in pageRows" :key="record.id">
          <td><button class="asset-name" @click="emit('select', record)"><span><strong>{{ record.properties.name }}</strong><small>{{ planningLabels[projectKind(record)] }} · {{ record.properties.id }}<template v-if="!record.geometry"> · No drawable route</template></small></span></button></td>
          <td>{{ record.properties.status }}</td><td>{{ record.properties.target_cod_year ?? 'Unavailable' }}</td><td>{{ record.properties.province ?? 'Unavailable' }}</td>
        </tr></tbody></table></div>
      <div v-if="records.length" class="pagination"><span>Page {{ page }} of {{ pages }}</span><div><button class="small-button" :disabled="page === 1" @click="page--">Previous</button><button class="small-button" :disabled="page === pages" @click="page++">Next</button></div></div>
    </section>
  </div>
</template>
