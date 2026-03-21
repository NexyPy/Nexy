<script lang="ts">
  import Button from './button.svelte';
  import AddIcon from './addIcon.svelte';
  import RemoveIcon from './removeIcon.svelte';

  let count = $state(0);
</script>

<div class="flex justify-end rounded-xl p-4 border border-white/40 hover:rounded-2xl hover:border-dashed hover:bg-[hsl(193,46%,29%)]/5 transition-all duration-300">
  <div class="flex-1 flex flex-col justify-between gap-2">
    <p class="uppercase text-xs font-mono font-medium border border-white/40 text-white w-fit px-2 py-1 rounded-2xl">
      Counter
    </p>
    <span class="text-6xl font-medium text-white w-fit rounded-xl p-2">
      {count}
    </span>
  </div>

  <div class="relative md:h-full flex flex-col items-center justify-between p-1 border border-gray-50/40 rounded-full">
    <button
      onclick={() => count++}
      class="z-10 cursor-pointer size-8 flex items-center justify-center rounded-full bg-white text-gray-950 hover:bg-yellow-500 transition-colors text-xl font-bold"
    >
      <AddIcon />
    </button>

    <div class="space-y-[0.5px] opacity-40 z-0 absolute top-1/2 -translate-y-1/2 pointer-events-none">
      {#each Array(30) as _, i}
        <div class="border-b border-white w-5 h-0.5"></div>
      {/each}
    </div>

    <Button onclick={() => count--}>
      <RemoveIcon />
    </Button>
  </div>
</div>