<script setup lang="ts">
import { formatNumber } from '../utils/formatAssets'
defineProps<{ counts: { lines: number; primary: number; review: number; points: number }; loading: boolean }>()
</script>
<template>
  <section class="summary-grid" aria-label="Selected record counts" aria-live="polite">
    <article class="metric-card"><span class="metric-label"><span class="metric-icon">╱</span> Line segments</span><strong data-testid="line-count">{{ loading ? '—' : formatNumber(counts.lines) }}</strong><small>Selected mapped segments</small></article>
    <article class="metric-card"><span class="metric-label"><span class="metric-icon">▧</span> Primary substations</span><strong data-testid="primary-count">{{ loading ? '—' : formatNumber(counts.primary) }}</strong><small>Selected transmission-tagged polygons</small></article>
    <article class="metric-card review-metric"><span class="metric-label"><span class="metric-icon">◇</span> Review polygons</span><strong data-testid="review-count">{{ loading ? '—' : formatNumber(counts.review) }}</strong><small>Unvalidated polygons · off by default</small></article>
    <article class="metric-card point-metric"><span class="metric-label"><span class="metric-icon">◎</span> Point-only candidates</span><strong data-testid="point-count">{{ loading ? '—' : formatNumber(counts.points) }}</strong><small>Unvalidated source locations · off by default</small></article>
  </section>
</template>
