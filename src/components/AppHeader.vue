<script setup lang="ts">
defineEmits<{ about: [] }>()
</script>
<template>
  <header class="app-header">
    <a class="brand" href="#main" aria-label="MENTARI Grids inventory"><img class="brand-logo" src="/images/Mentari Logo_Tagline Revamp_Color.png" alt="MENTARI logo" width="1890" height="1063"/><span><strong>MENTARI <span>Grids</span></strong><small>TRANSMISSION ASSET INVENTORY</small></span></a>
    <nav aria-label="Main navigation"><a class="nav-active" href="#main" aria-current="page">Inventory</a><button class="nav-button" @click="$emit('about')">About the data <span aria-hidden="true">↗</span></button></nav>
  </header>
</template>

<style scoped>
.brand-logo { display: block; width: 92px; height: 54px; padding: 3px 6px; object-fit: contain; flex: none; background: #fff; border-radius: 6px }
@media(max-width:720px) { .brand-logo { width: 62px; height: 38px } }
@media(max-width:380px) { .app-header { padding-inline: 14px; gap: 8px } .brand { gap: 8px } .brand-logo { width: 56px; height: 36px } .brand strong { font-size: 17px } .brand small { font-size: 5.5px; letter-spacing: .8px } }
</style>
