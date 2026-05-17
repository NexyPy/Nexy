<script lang="ts">
	import SunIcon from './sunIcon.svelte';
	import MoonIcon from './moonIcon.svelte';
	import MonitorIcon from './monitorIcon.svelte';
	import ThemeButton from './themeButton.svelte';

	type ThemeMode = 'light' | 'dark' | 'system';

	let active = $state<ThemeMode>((localStorage.getItem('nexy-theme') as ThemeMode) || 'system');
	let containerRef = $state<HTMLDivElement>();

	// Effet pour appliquer le thème et sauvegarder
	$effect(() => {
		const root = document.documentElement;
		localStorage.setItem('nexy-theme', active);

		const applyTheme = (isDark: boolean) => {
			root.classList.toggle('dark', isDark);
		};

		if (active === 'system') {
			const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
			applyTheme(systemDark);
		} else {
			applyTheme(active === 'dark');
		}
	});

	// Effet pour mettre à jour la position du slider
	$effect(() => {
		if (containerRef && active) {
			const activeElement = containerRef.querySelector(`[data-mode="${active}"]`) as HTMLElement;
			if (activeElement) {
				const root = document.documentElement;
				root.style.setProperty('--slider-left', `${activeElement.offsetLeft}px`);
				root.style.setProperty('--slider-width', `${activeElement.offsetWidth}px`);
			}
		}
	});
</script>

<div
	bind:this={containerRef}
	class="relative flex size-fit items-center justify-center gap-0.5 rounded-full border border-border p-1 transition-colors"
>
	<div
		class="bg-foreground absolute left-0 size-7 rounded-full transition-all duration-300 ease-in-out"
		style:transform="translateX(var(--slider-left))"
		style:width="var(--slider-width)"
	></div>

	<ThemeButton mode="light" {active} onclick={() => (active = 'light')}>
		<SunIcon />
	</ThemeButton>

	<ThemeButton mode="dark" {active} onclick={() => (active = 'dark')}>
		<MoonIcon />
	</ThemeButton>

	<ThemeButton mode="system" {active} onclick={() => (active = 'system')}>
		<MonitorIcon />
	</ThemeButton>
</div>