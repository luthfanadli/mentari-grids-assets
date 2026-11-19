<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import type { PageName } from './AppHeader.vue'

const props = defineProps<{ view: PageName }>()
const emit = defineEmits<{ close: [] }>()
const dialog = ref<HTMLDialogElement>()
const title = ref<HTMLElement>()
const label = computed(() => props.view === 'plans' ? 'RUPTL plans' : 'Summary')
let pressedBackdrop = false

watch(() => props.view, async view => {
  await nextTick()
  if (!dialog.value) return
  if (view === 'map') {
    dialog.value.close()
    return
  }
  if (!dialog.value.open) dialog.value.showModal()
  title.value?.focus({ preventScroll: true })
}, { immediate: true, flush: 'post' })

function isBackdrop(event: MouseEvent) {
  if (event.target !== dialog.value || !dialog.value) return false
  const bounds = dialog.value.getBoundingClientRect()
  return event.clientX < bounds.left || event.clientX > bounds.right ||
    event.clientY < bounds.top || event.clientY > bounds.bottom
}
function dismissBackdrop(event: MouseEvent) {
  if (pressedBackdrop && isBackdrop(event)) emit('close')
  pressedBackdrop = false
}
function onClose() {
  if (!dialog.value?.open && props.view !== 'map') emit('close')
}
function wrapFocus(event: KeyboardEvent) {
  if (event.ctrlKey || event.altKey || event.metaKey) return
  const controls = [...dialog.value!.querySelectorAll<HTMLElement>('a[href], button, input, select, textarea, [tabindex="0"]')]
    .filter(element => !element.matches(':disabled') && element.getClientRects().length)
  const first = controls[0], last = controls[controls.length - 1]
  const active = document.activeElement
  const wrapBackward = event.shiftKey && (active === first || active === title.value)
  if (wrapBackward || (!event.shiftKey && active === last)) {
    event.preventDefault()
    const target = wrapBackward ? last : first
    target?.focus()
  }
}
</script>

<template>
  <dialog id="data-report-dialog" ref="dialog" class="report-dialog" aria-labelledby="report-dialog-title"
    @cancel.prevent="emit('close')" @close="onClose"
    @pointerdown="pressedBackdrop = isBackdrop($event)" @click="dismissBackdrop" @keydown.tab="wrapFocus">
    <div class="report-dialog-header">
      <h2 id="report-dialog-title" ref="title" tabindex="-1">{{ label }}</h2>
      <button type="button" class="icon-button" aria-label="Close report" @click="emit('close')">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18"/></svg>
      </button>
    </div>
    <div class="report-dialog-content"><slot/></div>
  </dialog>
</template>
