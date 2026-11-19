<script setup lang="ts">
export type PageName = 'map' | 'summary' | 'plans'
defineProps<{ page: PageName }>()
defineEmits<{ navigate: [page: PageName]; about: [] }>()
const tabs: { key: PageName; label: string }[] = [
  { key: 'map', label: 'Map' }, { key: 'summary', label: 'Summary' }, { key: 'plans', label: 'RUPTL plans' },
]
</script>

<template>
  <header class="app-header">
    <a class="brand" href="#map" aria-label="MENTARI Grids map">
      <img src="/images/Mentari Logo_Tagline Revamp_Color.png" alt="MENTARI logo" width="80" height="45"/>
      <span class="brand-label"><strong>MENTARI <span>Grids</span></strong><small>Indonesia power atlas</small></span>
    </a>
    <nav class="primary-nav" aria-label="Main navigation">
      <a v-for="tab in tabs" :key="tab.key" :href="'#' + tab.key" :aria-current="page === tab.key ? 'page' : undefined" @click.prevent="$emit('navigate', tab.key)">{{ tab.label }}</a>
    </nav>
    <button class="about-button" aria-haspopup="dialog" aria-label="About the data" @click="$emit('about')">
      <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 11v6m0-10v1"/></svg><span>About the data</span>
    </button>
  </header>
</template>
