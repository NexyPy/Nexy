class ComponentEntry:
    def __init__(
        self,
        name: str,
        framework_code: dict[str, str],
        dependencies: list[str] | None = None,
        python_dependencies: list[str] | None = None,
    ):
        self.name = name
        self.framework_code = framework_code
        self.dependencies = dependencies or []
        self.python_dependencies = python_dependencies or []


COMPONENT_REGISTRY: dict[str, ComponentEntry] = {
    "button": ComponentEntry(
        name="Button",
        framework_code={
            "react": """import React from 'react';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline';
}

export default function Button({ variant = 'primary', className = '', ...props }: ButtonProps) {
  const baseStyles = "px-4 py-2 rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2";
  const variants = {
    primary: "bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500",
    secondary: "bg-gray-600 text-white hover:bg-gray-700 focus:ring-gray-500",
    outline: "border-2 border-blue-600 text-blue-600 hover:bg-blue-50 focus:ring-blue-500"
  };

  return (
    <button 
      className={`${baseStyles} ${variants[variant]} ${className}`}
      {...props}
    />
  );
}
""",
            "vue": """<script setup lang="ts">
interface Props {
  variant?: 'primary' | 'secondary' | 'outline'
  class?: string
}

withDefaults(defineProps<Props>(), {
  variant: 'primary',
  class: ''
})
</script>

<template>
  <button 
    :class="[
      'px-4 py-2 rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2',
      variant === 'primary' ? 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500' : '',
      variant === 'secondary' ? 'bg-gray-600 text-white hover:bg-gray-700 focus:ring-gray-500' : '',
      variant === 'outline' ? 'border-2 border-blue-600 text-blue-600 hover:bg-blue-50 focus:ring-blue-500' : '',
      $props.class
    ]"
    v-bind="$attrs"
  >
    <slot />
  </button>
</template>
""",
            "svelte": """<script lang="ts">
  export let variant: 'primary' | 'secondary' | 'outline' = 'primary';
  let className: string = '';
  export { className as class };

  const baseStyles = "px-4 py-2 rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2";
  const variants = {
    primary: "bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500",
    secondary: "bg-gray-600 text-white hover:bg-gray-700 focus:ring-gray-500",
    outline: "border-2 border-blue-600 text-blue-600 hover:bg-blue-50 focus:ring-blue-500"
  };
</script>

<button 
  class="{baseStyles} {variants[variant]} {className}"
  {...$$restProps}
>
  <slot />
</button>
""",
        },
        dependencies=["clsx", "tailwind-merge"],
    ),
    "input": ComponentEntry(
        name="Input",
        framework_code={
            "react": """import React from 'react';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {}

export default function Input({ className = '', ...props }: InputProps) {
  return (
    <input
      className={`flex h-10 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 ${className}`}
      {...props}
    />
  );
}
"""
        },
    ),
    "card": ComponentEntry(
        name="Card",
        framework_code={
            "react": """import React from 'react';

export function Card({ children, className = '' }: { children: React.ReactNode, className?: string }) {
  return (
    <div className={`rounded-xl border border-gray-200 bg-white text-gray-950 shadow-sm ${className}`}>
      {children}
    </div>
  );
}

export function CardHeader({ children, className = '' }: { children: React.ReactNode, className?: string }) {
  return <div className={`flex flex-col space-y-1.5 p-6 ${className}`}>{children}</div>;
}

export function CardTitle({ children, className = '' }: { children: React.ReactNode, className?: string }) {
  return <h3 className={`font-semibold leading-none tracking-tight ${className}`}>{children}</h3>;
}

export function CardContent({ children, className = '' }: { children: React.ReactNode, className?: string }) {
  return <div className={`p-6 pt-0 ${className}`}>{children}</div>;
}
"""
        },
    ),
}
