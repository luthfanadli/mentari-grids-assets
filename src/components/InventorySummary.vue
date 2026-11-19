<script setup lang="ts">
import { formatNumber } from '../utils/formatAssets'
import type { InventorySummary } from '../types/assets'
defineProps<{ counts: { lines: number; primary: number; review: number; points: number; plants: number }; summary: InventorySummary | null; loading: boolean }>()
const metrics = [
  { key: 'lines', dataset: 'lines', label: 'Line segments', test: 'line-count' },
  { key: 'primary', dataset: 'primary', label: 'Primary substations', test: 'primary-count' },
  { key: 'plants', dataset: 'power_plants', label: 'Plant footprints', test: 'plant-count' },
  { key: 'review', dataset: 'review', label: 'Review polygons', test: 'review-count' },
  { key: 'points', dataset: 'point_candidates', label: 'Point candidates', test: 'point-count' },
] as const
</script>
<template>
  <section class="inventory-totals" aria-label="Selected OSM inventory records" aria-live="polite">
    <div v-for="metric in metrics" :key="metric.key"><span>{{ metric.label }}</span><strong :data-testid="metric.test">{{ loading ? '…' : formatNumber(counts[metric.key]) }}</strong><small v-if="summary">of {{ formatNumber(summary.datasets[metric.dataset].count) }} published</small></div>
  </section>
</template>
