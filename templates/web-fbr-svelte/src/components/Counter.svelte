<script>
  let { count = 0 } = $props();
</script>

<div class="p-6 bg-white rounded-2xl shadow-sm border border-slate-100 flex flex-col items-center gap-4">
  <h3 class="text-xl font-bold text-slate-800">Svelte 5 Component</h3>
  <div class="flex items-center gap-6">
    <button
      onclick={() => count--}
      class="w-10 h-10 flex items-center justify-center rounded-full bg-orange-50 text-orange-600 hover:bg-orange-100 transition-colors text-xl font-bold"
    >
      -
    </button>
    <span class="text-4xl font-mono font-bold text-orange-600 min-w-12 text-center">
      {count}
    </span>
    <button
      onclick={() => count++}
      class="w-10 h-10 flex items-center justify-center rounded-full bg-orange-600 text-white hover:bg-orange-700 transition-colors text-xl font-bold"
    >
      +
    </button>
  </div>
  <p class="text-xs text-slate-400 mt-2">
    This is a Svelte 5 component managed by Nexy
  </p>
</div>
