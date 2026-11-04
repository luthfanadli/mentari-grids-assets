<script setup lang="ts">
import { computed, ref } from 'vue'
import type { AssetFeature } from '../types/assets'
import { VOLTAGE_COLORS } from '../utils/formatAssets'
import { selectedMapLegend } from '../utils/substationPresentation'

const props = defineProps<{ overview: boolean; features: AssetFeature[] }>()
const expanded = ref(false)
const key = computed(() => selectedMapLegend(props.features))
</script>

<template>
  <section class="legend-panel" :class="{ expanded }" aria-label="Map legend">
    <button class="legend-toggle" :aria-expanded="expanded" aria-controls="map-legend-content" :title="expanded ? 'Collapse map legend' : 'Show map legend'" @click="expanded = !expanded">
      <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M9 6h11M9 12h11M9 18h11"/><circle cx="4" cy="6" r="1"/><circle cx="4" cy="12" r="1"/><circle cx="4" cy="18" r="1"/></svg>
      <span>Legend</span>
      <svg class="legend-chevron" :class="{ rotated: expanded }" width="14" height="14" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="m5 8 5 5 5-5"/></svg>
    </button>
    <div v-show="expanded" id="map-legend-content" class="legend-content">
      <p class="legend-note">{{ features.length ? 'Matches current filters.' : 'No matching records.' }}</p>
      <template v-if="key.lineVoltages.length">
        <strong>Transmission lines <span>kV</span></strong>
        <span v-for="voltage in key.lineVoltages" :key="voltage" class="legend-row"><i class="line-sample" :style="{ background: VOLTAGE_COLORS[voltage] }"></i>{{ voltage }}</span>
      </template>
      <template v-if="key.primary || key.constructionPrimary || key.review || key.points">
        <strong class="legend-section">Substations</strong>
        <span v-if="key.primary" class="legend-row"><i class="primary-sample" :class="{ round: overview }"></i>Primary substations</span>
        <span v-if="key.constructionPrimary" class="legend-row"><i class="construction-primary-sample" :class="{ round: overview }"></i>Substation · construction</span>
        <span v-if="key.review" class="legend-row"><i class="review-sample" :class="{ round: overview }"></i>Review polygons</span>
        <span v-if="key.points" class="legend-row"><i class="point-sample"></i>Point-only candidates</span>
      </template>
      <template v-if="key.constructionLines || key.disusedLines">
        <strong class="legend-section">Line pattern</strong>
        <span v-if="key.baselineLines" class="legend-row"><i class="baseline-sample"></i>Not flagged in OSM</span>
        <span v-if="key.constructionLines" class="legend-row"><i class="construction-sample"></i>Tagged construction</span>
        <span v-if="key.disusedLines" class="legend-row"><i class="disused-sample"></i>Tagged disused</span>
      </template>
    </div>
  </section>
</template>

<style scoped>
.legend-panel { position: absolute; top: 14px; left: 14px; z-index: 1; max-width: calc(100% - 72px); background: #fffffff5; border: 1px solid var(--border); border-radius: 6px; box-shadow: 0 2px 8px #123b6814; color: var(--ink); overflow: visible }
.legend-panel.expanded { width: 216px }
.legend-toggle { display: flex; align-items: center; gap: 8px; min-height: 36px; padding: 8px 11px; width: 100%; font-size: 11px; font-weight: 600; border-radius: 6px }
.legend-toggle:hover { background: var(--surface-blue) }
.legend-chevron { margin-left: auto; transition: transform 150ms ease }
.legend-chevron.rotated { transform: rotate(180deg) }
.legend-content { display: flex; flex-direction: column; gap: 8px; padding: 4px 14px 14px; font-size: 11px; max-height: min(420px, calc(100svh - 170px)); overflow-y: auto; overscroll-behavior: contain }
.legend-note { margin: 0; color: var(--muted); font-size: 10px; line-height: 1.5 }
.legend-section { border-top: 1px solid var(--border); padding-top: 10px; margin-top: 2px }
.legend-content strong { font-size: 11px; margin-bottom: 2px }
.legend-content strong span { margin-left: 6px; color: var(--muted); font-weight: 400 }
.legend-row { display: flex; align-items: center; gap: 10px; min-height: 14px }
.legend-row i { display: inline-block; flex: none; width: 18px }
.line-sample { height: 3px; border-radius: 1px }
.legend-row .primary-sample, .legend-row .construction-primary-sample, .legend-row .review-sample, .legend-row .point-sample { width: 9px; height: 9px; margin: 0 4px }
.primary-sample { background: #086e66; border: 1px solid #075c55 }
.construction-primary-sample { background: #086e6666; border: 1px dashed #ac6910 }
.construction-primary-sample.round { background: #ac6910; border-style: solid }
.review-sample { background: #fff7df; border: 1px dashed #b46c00 }
.round, .point-sample { border-radius: 50% }
.review-sample.round { border-style: solid }
.point-sample { border: 2px solid #b8406a; background: white }
.baseline-sample { border-top: 2px solid var(--muted) }
.construction-sample { border-top: 2px dashed var(--muted) }
.disused-sample { border-top: 2px dotted var(--muted) }
@media(max-width:720px) { .legend-panel { top: 10px; left: 10px } .legend-toggle { min-height: 36px } }
@media(prefers-reduced-motion:reduce) { .legend-chevron { transition: none } }
</style>
