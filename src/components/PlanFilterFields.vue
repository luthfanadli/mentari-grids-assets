<script setup lang="ts">
import type { PlanFilters, PlanningCatalog } from '../types/planning'
defineProps<{ options: PlanningCatalog['filters'] }>()
const filters = defineModel<PlanFilters>({ required: true })
</script>
<template>
  <div class="plan-filter-fields">
    <label>Plan source<select v-model="filters.source"><option value="">All plans</option><option v-for="source in options.sources" :key="source">{{ source }}</option></select></label>
    <label>Target COD year<select v-model="filters.year"><option value="">All target years</option><option v-for="year in options.target_years" :key="year" :value="String(year)">{{ year }}</option><option v-if="options.unknown_year" value="unknown">Year unavailable</option></select></label>
    <label>Project stage<select v-model="filters.status"><option value="">All stages</option><option v-for="status in options.statuses" :key="status">{{ status }}</option></select></label>
  </div>
</template>
