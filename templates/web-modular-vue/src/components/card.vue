<script setup lang="ts">
import Counter from './counter/counter.vue'
</script>

<template>
  <div
    class="w-full lg:w-1/2 md:h-full h-120 flex flex-col justify-between p-2 border-[1.34px] border-dashed border-gray-500/30 rounded-2xl hover:rounded-3xl hover:border-4 hover:border-double hover:bg-[hsl(180,8%,3%)]/2 transition-all duration-300"
  >
    <p class="text-white/70 text-xs border border-white/40 rounded-full w-fit px-2 py-1">
      This is Vue component
    </p>

    <div class="flex justify-center items-center">
      <svg
        viewBox="0 0 128 128"
        width="100%"
        height="100%"
        class="mt-4 mb-3 w-24 lg:w-28 self-center transition-all ease-in-out"
      >
        <path fill="#42b883" d="M78.8,10L64,35.4L49.2,10H0l64,110l64-110H78.8z" />
        <path fill="#35495e" d="M78.8,10L64,35.4L49.2,10H25.6L64,76l38.4-66H78.8z" />
      </svg>
    </div>

    <Counter />
  </div>
</template>