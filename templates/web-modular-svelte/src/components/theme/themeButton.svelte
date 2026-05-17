<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		mode: string;
		active: string;
		onclick: () => void;
		children: Snippet;
	}

	let { mode, active, onclick, children }: Props = $props();
</script>

<button
	data-mode={mode}
	{onclick}
	class="relative z-10 grid size-7 cursor-pointer place-content-center rounded-full transition-colors duration-300 
    {active === mode
		? 'text-white dark:text-slate-900'
		: 'text-gray-500 hover:text-gray-900 dark:text-slate-400'}"
>
	{@render children()}
</button>