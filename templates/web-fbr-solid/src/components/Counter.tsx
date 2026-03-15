import { createSignal } from 'solid-js'

export default function Counter() {
  const [count, setCount] = createSignal(0)

  return (
    <div class="p-6 bg-white rounded-2xl shadow-sm border border-slate-100 flex flex-col items-center gap-4">
      <h3 class="text-xl font-bold text-slate-800">SolidJS Component</h3>
      <div class="flex items-center gap-6">
        <button
          onClick={() => setCount(count() - 1)}
          class="w-10 h-10 flex items-center justify-center rounded-full bg-blue-50 text-blue-600 hover:bg-blue-100 transition-colors text-xl font-bold"
        >
          -
        </button>
        <span class="text-4xl font-mono font-bold text-blue-600 min-w-12 text-center">
          {count()}
        </span>
        <button
          onClick={() => setCount(count() + 1)}
          class="w-10 h-10 flex items-center justify-center rounded-full bg-blue-600 text-white hover:bg-blue-700 transition-colors text-xl font-bold"
        >
          +
        </button>
      </div>
      <p class="text-xs text-slate-400 mt-2">
        This is a SolidJS component managed by Nexy
      </p>
    </div>
  )
}
