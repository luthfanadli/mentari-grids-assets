<script setup lang="ts">
import { computed, nextTick, onMounted, onBeforeUnmount, ref } from 'vue'
import { BASEMAP_LABELS } from '../utils/basemaps'
import type { BasemapId } from '../utils/basemaps'

const props = defineProps<{ selected: BasemapId; customAvailable: boolean; disabled: boolean }>()
const emit = defineEmits<{ change: [value: BasemapId] }>()
const root = ref<HTMLElement | null>(null), button = ref<HTMLButtonElement | null>(null), opened = ref(false)
const choices = computed<BasemapId[]>(() => ['osm', 'google_satellite', ...(props.customAvailable ? ['custom' as const] : []), 'plain'])

async function toggle() {
  opened.value = !opened.value
  if (opened.value) {
    await nextTick()
    root.value?.querySelector<HTMLInputElement>('input:checked')?.focus()
  }
}
function close(restoreFocus = false) {
  opened.value = false
  if (restoreFocus) button.value?.focus()
}
function select(value: BasemapId) { emit('change', value); close(true) }
function outside(event: PointerEvent) { if (!root.value?.contains(event.target as Node)) close() }
function focusOutside(event: FocusEvent) { if (!root.value?.contains(event.relatedTarget as Node | null)) close() }
onMounted(() => document.addEventListener('pointerdown', outside))
onBeforeUnmount(() => document.removeEventListener('pointerdown', outside))
</script>

<template>
  <div ref="root" class="basemap-picker" @keydown.esc.stop.prevent="close(true)" @focusout="focusOutside">
    <button ref="button" class="map-tool-button" :disabled="disabled" :aria-label="`Change basemap: ${BASEMAP_LABELS[selected]}`" :title="`Basemap: ${BASEMAP_LABELS[selected]}`" aria-haspopup="dialog" aria-controls="basemap-options" :aria-expanded="opened" @click="toggle">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" aria-hidden="true"><path d="m3 8 9-5 9 5-9 5zM3 12l9 5 9-5M3 16l9 5 9-5"/></svg>
    </button>
    <div v-if="opened" id="basemap-options" class="basemap-popover" role="dialog" aria-label="Basemap options">
      <fieldset><legend>Basemap</legend>
        <label v-for="choice in choices" :key="choice" class="basemap-choice">
          <input type="radio" name="map-basemap" :value="choice" :checked="choice === selected" @change="select(choice)"/>
          <span class="basemap-preview" :class="choice" aria-hidden="true"></span>
          <span>{{ BASEMAP_LABELS[choice] }}</span>
        </label>
      </fieldset>
    </div>
  </div>
</template>

<style scoped>
.basemap-picker { position: relative }
.basemap-popover { position: absolute; right: 0; top: calc(100% + 9px); width: 232px; z-index: 5; padding: 8px; background: #fff; border: 1px solid var(--border); border-radius: 7px; box-shadow: 0 5px 22px #123b6824; color: var(--ink); transform-origin: top right; animation: surface-in 160ms var(--ease) }
fieldset { padding: 0; margin: 0; border: 0 }
legend { float: none; padding: 6px 8px 10px; margin: 0; font-size: 11px; font-weight: 650 }
.basemap-choice { display: flex; align-items: center; gap: 10px; padding: 9px 8px; border-radius: 4px; cursor: pointer; font-size: 12px; min-height: 43px }
.basemap-choice:hover { background: var(--surface-soft) }
.basemap-choice:has(input:checked) { background: var(--surface-blue); color: var(--brand-blue) }
input { margin: 0; accent-color: var(--brand-blue); width: 14px; height: 14px; flex: none }
.basemap-preview { width: 29px; height: 27px; border: 1px solid var(--border-strong); border-radius: 3px; flex: none; background-color: var(--map-background) }
.osm { background: linear-gradient(35deg, transparent 42%, #fff 43%, #fff 51%, transparent 52%), linear-gradient(100deg, #dce7cc 40%, #c1d9e1 42%, #c1d9e1 52%, #e6edda 54%) }
.google_satellite { background: linear-gradient(30deg, transparent 37%, #a1ae83 38%, #a1ae83 42%, transparent 43%), linear-gradient(115deg, #324e2a 25%, #658446 26%, #304b32 68%, #344756 69%) }
.custom { background: linear-gradient(45deg, #dbe3ed 50%, #dce9d5 50%) }
</style>
