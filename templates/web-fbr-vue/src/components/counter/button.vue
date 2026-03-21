<script setup lang="ts">
defineProps<{
  onClick: () => void
}>()
</script>

<template>
  <button
    @click="onClick"
    class="z-10 size-8 cursor-pointer flex items-center justify-center rounded-full border border-white/40 text-white bg-black/50 backdrop-blur-2xl hover:bg-indigo-100/20 transition-colors text-xl font-bold"
  >
    <slot />
  </button>
</template>