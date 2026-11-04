<script setup lang="ts">
defineEmits<{ about: [] }>()
</script>
<template>
  <header class="app-header">
    <a class="brand" href="#main" aria-label="MENTARI Grids inventory"><svg class="brand-mark" width="37" height="37" viewBox="0 0 40 40" fill="none" aria-hidden="true"><path d="M20 3v6m0 22v6M3 20h6m22 0h6M8 8l4 4m16 16 4 4M8 32l4-4m16-16 4-4" stroke="currentColor" stroke-width="2.2"/><circle cx="20" cy="20" r="8" stroke="currentColor" stroke-width="2.2"/><path d="m22 13-7 9h5l-2 6 8-10h-6z" fill="currentColor"/></svg><span><strong>MENTARI <span>Grids</span></strong><small>TRANSMISSION ASSET INVENTORY</small></span></a>
    <nav aria-label="Main navigation"><a class="nav-active" href="#main" aria-current="page">Inventory</a><button class="nav-button" @click="$emit('about')">About the data <span aria-hidden="true">↗</span></button></nav>
  </header>
</template>
