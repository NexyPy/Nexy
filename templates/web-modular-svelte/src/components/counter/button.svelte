<script lang="ts">
  interface Props {
    children: any;
    onclick: () => void;
  }
  let { children, onclick }: Props = $props();
</script>

<button
  {onclick}
  class="z-10 size-8 cursor-pointer flex items-center justify-center rounded-full border border-white/40 text-white bg-black/50 backdrop-blur-2xl hover:bg-indigo-100/20 transition-colors text-xl font-bold"
>
  {@render children()}
</button>