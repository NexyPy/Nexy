<script lang="ts">
  import Counter from "./counter/counter.svelte";
</script>

<div
  class="w-full lg:w-1/2 md:h-full h-120 flex flex-col justify-between p-2 border-[1.34px] border-dashed border-gray-500/30 rounded-2xl hover:rounded-3xl hover:border-4 hover:border-double hover:bg-[hsl(180,8%,3%)]/2 transition-all duration-300"
>
  <p class="text-white/70 text-xs border border-white/40 rounded-full w-fit px-2 py-1">
    This is Svelte component
  </p>

  <div class="flex justify-center items-center">
    <figure>
      <img src="/public/svelte.png" alt="svelte" class="w-32" />
    </figure>
  </div>

  <Counter />
</div>