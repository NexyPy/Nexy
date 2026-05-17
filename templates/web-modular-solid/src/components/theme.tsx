/* eslint-disable react-hooks/refs */
import { createSignal, createEffect, onMount, JSX } from 'solid-js';

type ThemeMode = 'light' | 'dark' | 'system';

const Theme = () => {
    const [active, setActive] = createSignal<ThemeMode>(
        (localStorage.getItem('nexy-theme') as ThemeMode) || 'system'
    );

    let containerRef: HTMLDivElement | undefined;

    createEffect(() => {
        const root = document.documentElement;
        const currentActive = active();
        localStorage.setItem('nexy-theme', currentActive);

        const applyTheme = (isDark: boolean) => {
            root.classList.toggle('dark', isDark);
        };

        if (currentActive === 'system') {
            const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            applyTheme(systemDark);
        } else {
            applyTheme(currentActive === 'dark');
        }
    });

    const updateSlider = () => {
        const currentActive = active();
        const activeElement = containerRef?.querySelector(`[data-mode="${currentActive}"]`) as HTMLElement;

        if (activeElement) {
            const root = document.documentElement;
            root.style.setProperty('--slider-left', `${activeElement.offsetLeft}px`);
            root.style.setProperty('--slider-width', `${activeElement.offsetWidth}px`);
        }
    };

    // Run on mount to set initial slider position
    onMount(updateSlider);

    // Run on every active change
    createEffect(updateSlider);

    return (
        <div
            
            ref={containerRef}
            class="relative flex justify-center items-center p-1 gap-0.5 border border-border rounded-full size-fit transition-colors"
        >
            <div
                className="absolute left-0 size-7 bg-foreground rounded-full transition-all duration-300 ease-in-out"
                style={{
                    transform: `translateX(var(--slider-left))`,
                    width: `var(--slider-width)`
                }}
            />

            <ThemeButton mode="light" active={active()} onClick={() => setActive('light')} icon={<SunIcon />} />
            <ThemeButton mode="dark" active={active()} onClick={() => setActive('dark')} icon={<MoonIcon />} />
            <ThemeButton mode="system" active={active()} onClick={() => setActive('system')} icon={<MonitorIcon />} />
        </div>
    );
};

type ThemeButtonType = {
    mode: ThemeMode;
    active: ThemeMode;
    onClick: () => void;
    icon: JSX.Element;
}

const ThemeButton = (props: ThemeButtonType) => (
    
    <button
        data-mode={props.mode}
        onClick={props.onClick}
        class={`relative z-10 cursor-pointer size-7 grid place-content-center rounded-full transition-colors duration-300 ${
            props.active === props.mode
                ? 'text-white dark:text-slate-900'
                : 'text-gray-500 dark:text-slate-400 hover:text-gray-900'
        }`}
    >
        {props.icon}
    </button>
);


const SunIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="size-4.5">
        <path d="M10 2a.75.75 0 0 1 .75.75v1.5a.75.75 0 0 1-1.5 0v-1.5A.75.75 0 0 1 10 2ZM10 15a.75.75 0 0 1 .75.75v1.5a.75.75 0 0 1-1.5 0v-1.5A.75.75 0 0 1 10 15ZM10 7a3 3 0 1 0 0 6 3 3 0 0 0 0-6ZM15.657 5.404a.75.75 0 1 0-1.06-1.06l-1.061 1.06a.75.75 0 0 0 1.06 1.06l1.06-1.06ZM6.464 14.596a.75.75 0 1 0-1.06-1.06l-1.06 1.06a.75.75 0 0 0 1.06 1.06l1.06-1.06ZM18 10a.75.75 0 0 1-.75.75h-1.5a.75.75 0 0 1 0-1.5h1.5A.75.75 0 0 1 18 10ZM5 10a.75.75 0 0 1-.75.75h-1.5a.75.75 0 0 1 0-1.5h1.5A.75.75 0 0 1 5 10ZM14.596 15.657a.75.75 0 0 0 1.06-1.06l-1.06-1.061a.75.75 0 1 0-1.06 1.06l1.06 1.06ZM5.404 6.464a.75.75 0 0 0 1.06-1.06l-1.06-1.06a.75.75 0 1 0-1.061 1.06l1.06 1.06Z" />
    </svg>

);
const MoonIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="size-4.5">
        <path fillRule="evenodd" d="M7.455 2.004a.75.75 0 0 1 .26.77 7 7 0 0 0 9.958 7.967.75.75 0 0 1 1.067.853A8.5 8.5 0 1 1 6.647 1.921a.75.75 0 0 1 .808.083Z" clipRule="evenodd" />
    </svg>
);
const MonitorIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="size-4.5">
        <path fillRule="evenodd" d="M2 4.25A2.25 2.25 0 0 1 4.25 2h11.5A2.25 2.25 0 0 1 18 4.25v8.5A2.25 2.25 0 0 1 15.75 15h-3.105a3.501 3.501 0 0 0 1.1 1.677A.75.75 0 0 1 13.26 18H6.74a.75.75 0 0 1-.484-1.323A3.501 3.501 0 0 0 7.355 15H4.25A2.25 2.25 0 0 1 2 12.75v-8.5Zm1.5 0a.75.75 0 0 1 .75-.75h11.5a.75.75 0 0 1 .75.75v7.5a.75.75 0 0 1-.75.75H4.25a.75.75 0 0 1-.75-.75v-7.5Z" clipRule="evenodd" />
    </svg>
);

export default Theme;