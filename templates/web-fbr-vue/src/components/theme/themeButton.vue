<script setup lang="ts">
defineProps<{
  mode: string;
  active: string;
}>();

defineEmits(['click']);
</script>

<template>
  <button
    :data-mode="mode"
    @click="$emit('click')"
    class="relative z-10 cursor-pointer size-7 grid place-content-center rounded-full transition-colors duration-300"
    :class="active === mode 
      ? 'text-white dark:text-slate-900' 
      : 'text-gray-500 dark:text-slate-400 hover:text-gray-900'"
  >
    <slot />
  </button>
</template>