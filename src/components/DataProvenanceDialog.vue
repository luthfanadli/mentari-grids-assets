<script setup lang="ts">
import { onMounted, ref } from 'vue'
const emit = defineEmits<{ close: [] }>()
const dialog = ref<HTMLDialogElement>()
onMounted(() => dialog.value?.showModal())
</script>
<template>
  <dialog ref="dialog" class="provenance-dialog" aria-labelledby="about-title" @close="emit('close')" @click="event => { if (event.target === dialog) dialog?.close() }">
    <div class="dialog-inner">
      <div class="drawer-heading">
        <h2 id="about-title">About the data</h2>
        <button type="button" class="icon-button" aria-label="Close about data" @click="dialog?.close()">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18"/></svg>
        </button>
      </div>
      <div class="about-body">
        <section aria-labelledby="about-assets">
          <h3 id="about-assets">Mapped assets</h3>
          <p>Transmission lines and primary substations at 70, 150, 275 and 500 kV, plus power-plant footprints.</p>
          <p class="source-links">© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a> · <a href="https://openinframap.org/">OpenInfraMap</a> · <a href="https://opendatacommons.org/licenses/odbl/1-0/">ODbL 1.0</a></p>
        </section>
        <section aria-labelledby="about-plans">
          <h3 id="about-plans">Planning projects</h3>
          <p>Projects from RUPTL 2025–2034 and RUKN 2025–2060, including new construction, extensions, uprates and energy storage.</p>
          <p class="source-links"><a href="https://indonesiapowermap.com/#data">Indonesia Power Map</a> · <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a> · Adapted for this map.</p>
        </section>
        <section aria-labelledby="about-limitations">
          <h3 id="about-limitations">Data limitations</h3>
          <p>Coverage may be incomplete. The OSM data date is unknown, and current operation is unverified. Project locations may be approximate; target years are planned dates.</p>
        </section>
        <details class="additional-credits">
          <summary>Additional credits</summary>
          <p class="source-links"><a href="https://www.naturalearthdata.com/">Natural Earth</a> · <a href="https://www.naturalearthdata.com/about/terms-of-use/">Public domain</a><br/><a href="https://maplibre.org/">MapLibre GL JS</a> · <a href="https://github.com/maplibre/maplibre-gl-js/blob/main/LICENSE.txt">BSD 3-Clause license</a></p>
        </details>
      </div>
    </div>
  </dialog>
</template>
