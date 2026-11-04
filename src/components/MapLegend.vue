<script setup lang="ts">
import { ref } from 'vue'
import { VOLTAGE_COLORS } from '../utils/formatAssets'

defineProps<{ overview: boolean }>()
const expanded = ref(false)
</script>

<template>
  <section class="legend-panel" :class="{ expanded }" aria-label="Map legend">
    <button class="legend-toggle" :aria-expanded="expanded" aria-controls="map-legend-content" :title="expanded ? 'Collapse map legend' : 'Show map legend'" @click="expanded = !expanded">
      <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M9 6h11M9 12h11M9 18h11"/><circle cx="4" cy="6" r="1"/><circle cx="4" cy="12" r="1"/><circle cx="4" cy="18" r="1"/></svg>
      <span>Legend</span>
      <svg class="legend-chevron" :class="{ rotated: expanded }" width="14" height="14" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="m5 8 5 5 5-5"/></svg>
    </button>
    <div v-show="expanded" id="map-legend-content" class="legend-content">
      <strong>Voltage <span>kV</span></strong>
      <span v-for="(color, voltage) in VOLTAGE_COLORS" :key="voltage" class="legend-row"><i class="line-sample" :style="{ background: color }"></i>{{ voltage }}</span>
      <div class="legend-divider"></div>
      <span class="legend-row"><i class="primary-sample" :class="{ round: overview }"></i>Primary substation</span>
      <span class="legend-row"><i class="review-sample" :class="{ round: overview }"></i>Review polygon</span>
      <span class="legend-row"><i class="point-sample"></i>Point-only candidate</span>
      <div class="legend-divider"></div>
      <span class="legend-row status-key"><i class="construction-sample"></i>Tagged construction</span>
      <span class="legend-row status-key"><i class="disused-sample"></i>Tagged disused</span>
    </div>
  </section>
</template>

<style scoped>
.legend-panel { position: absolute; top: 14px; left: 14px; z-index: 1; max-width: calc(100% - 72px); background: #fffffff5; border: 1px solid var(--border); border-radius: 6px; box-shadow: 0 2px 8px #123b6814; color: var(--ink); overflow: visible }
.legend-panel.expanded { width: 198px }
.legend-toggle { display: flex; align-items: center; gap: 8px; min-height: 36px; padding: 8px 11px; width: 100%; font-size: 11px; font-weight: 600; border-radius: 6px }
.legend-toggle:hover { background: var(--surface-blue) }
.legend-chevron { margin-left: auto; transition: transform 150ms ease }
.legend-chevron.rotated { transform: rotate(180deg) }
.legend-content { display: flex; flex-direction: column; gap: 8px; padding: 4px 14px 14px; font-size: 11px }
.legend-content strong { font-size: 11px; margin-bottom: 2px }
.legend-content strong span { margin-left: 6px; color: var(--muted); font-weight: 400 }
.legend-row { display: flex; align-items: center; gap: 10px; min-height: 14px }
.legend-row i { display: inline-block; flex: none; width: 18px }
.line-sample { height: 3px; border-radius: 1px }
.legend-divider { height: 1px; background: var(--border); margin: 2px 0 }
.legend-row .primary-sample, .legend-row .review-sample, .legend-row .point-sample { width: 9px; height: 9px; margin: 0 4px }
.primary-sample { background: #086e66; border: 1px solid #075c55 }
.review-sample { background: #fff7df; border: 1px dashed #b46c00 }
.round, .point-sample { border-radius: 50% }
.review-sample.round { border-style: solid }
.point-sample { border: 2px solid #b8406a; background: white }
.construction-sample { border-top: 2px dashed #ac6910 }
.disused-sample { border-top: 2px dotted #8b837a }
.status-key { color: var(--muted); font-size: 10px }
@media(max-width:720px) { .legend-panel { top: 10px; left: 10px } .legend-toggle { min-height: 36px } }
@media(prefers-reduced-motion:reduce) { .legend-chevron { transition: none } }
</style>
