<template>
  <div class="flex flex-col items-center justify-center py-6">
    <p>Count: {{ count }}</p>
    <button class="bg-blue-500 text-white px-4 py-2 rounded-md" @click="increment">Increment</button>
  </div>
</template>
<script setup>
import { ref } from 'vue';
const count = ref(0);
const increment = () => {
  count.value++;
  console.log("espoir",count.value);
};
</script>