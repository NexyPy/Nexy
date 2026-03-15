<script setup>
import { ref } from 'vue'

const count = ref(0)
</script>

<template>
  <div class="flex flex-col items-center gap-4 p-6 bg-white rounded-xl shadow-lg border border-gray-100">
    <h3 class="text-xl font-bold text-gray-800">Vue Component</h3>
    <div class="flex items-center gap-6">
      <button
        @click="count--"
        class="w-10 h-10 flex items-center justify-center rounded-full bg-emerald-50 text-emerald-600 hover:bg-emerald-100 transition-colors text-xl font-bold"
      >
        -
      </button>
      <span class="text-4xl font-mono font-bold text-emerald-600 min-w-[3rem] text-center">
        {{ count }}
      </span>
      <button
        @click="count++"
        class="w-10 h-10 flex items-center justify-center rounded-full bg-emerald-600 text-white hover:bg-emerald-700 transition-colors text-xl font-bold"
      >
        +
      </button>
    </div>
    <p class="text-sm text-gray-500 italic">
      This is a Vue 3 component (SFC) managed by Nexy
    </p>
  </div>
</template>
