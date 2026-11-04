<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { AssetFeature } from '../types/assets'
import { STATUS_LABELS, VOLTAGE_COLORS, formatNumber, formatVoltage } from '../utils/formatAssets'
const props = defineProps<{ features: AssetFeature[]; selectedId: string | null; viewportCount: number | null }>()
defineEmits<{ select: [feature: AssetFeature]; reset: [] }>()
const page = ref(1), pageSize = 20
const pageCount = computed(() => Math.max(1, Math.ceil(props.features.length / pageSize)))
const pageFeatures = computed(() => props.features.slice((page.value - 1) * pageSize, page.value * pageSize))
watch(() => props.features, () => { page.value = 1 })
</script>
<template>
  <section class="asset-table-card" aria-labelledby="results-heading">
    <div class="results-heading"><div><h2 id="results-heading">Selected records <span>{{ formatNumber(features.length) }}</span></h2><p>All matching records across the dataset</p></div><span class="viewport-count">{{ viewportCount === null ? 'Updating map…' : formatNumber(viewportCount) + ' rendered in viewport' }}</span></div>
    <div v-if="!features.length" class="empty-state"><strong>No records match these filters.</strong><p>Try another name, source ID, voltage or OSM status.</p><button class="small-button" @click="$emit('reset')">Reset filters</button></div>
    <div v-else class="table-scroll"><table><thead><tr><th scope="col">Asset / source name</th><th scope="col">Maximum voltage</th><th scope="col">OSM status</th><th scope="col">Source ID</th></tr></thead><tbody>
      <tr v-for="feature in pageFeatures" :key="feature.properties.feature_id" :class="{ 'selected-row': selectedId === feature.properties.feature_id }">
        <td><button class="asset-name" @click="$emit('select', feature)"><span class="asset-symbol" :class="{ 'candidate-symbol': !!feature.properties.review_reason, 'point-symbol': feature.properties.asset_type === 'substation_point' }" aria-hidden="true">{{ feature.properties.asset_type === 'transmission_line' ? '╱' : feature.properties.asset_type === 'substation_point' ? '◎' : '▧' }}</span><span>{{ feature.properties.display_name }}<small>{{ feature.properties.asset_type === 'substation_point' ? 'Unvalidated point-only location' : feature.properties.review_reason ? 'Unvalidated review polygon' : feature.properties.asset_type === 'transmission_line' ? 'Mapped line segment' : 'Transmission-tagged polygon' }}{{ feature.properties.display_name_is_fallback ? ' · fallback label' : '' }}</small></span></button></td>
        <td><span class="voltage-pill" :style="{ color: VOLTAGE_COLORS[feature.properties.max_voltage_kv ?? 0] }">{{ formatVoltage(feature.properties.max_voltage_kv) }}</span></td><td><span class="status-text" :class="feature.properties.osm_tag_status">{{ STATUS_LABELS[feature.properties.osm_tag_status] }}</span></td><td class="mono source-id">{{ feature.properties.source_id }}</td>
      </tr>
    </tbody></table></div>
    <div v-if="features.length" class="pagination"><span>{{ formatNumber((page - 1) * pageSize + 1) }}–{{ formatNumber(Math.min(page * pageSize, features.length)) }} of {{ formatNumber(features.length) }} records</span><div><button class="small-button" :disabled="page === 1" aria-label="Previous page" @click="page--">←</button><span>Page {{ page }} / {{ pageCount }}</span><button class="small-button" :disabled="page === pageCount" aria-label="Next page" @click="page++">→</button></div></div>
  </section>
</template>
