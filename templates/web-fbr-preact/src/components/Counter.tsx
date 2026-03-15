import { useState } from 'preact/hooks'

export default function Counter() {
  const [count, setCount] = useState(0)

  return (
    <div class="p-6 bg-white rounded-2xl shadow-sm border border-slate-100 flex flex-col items-center gap-4">
      <h3 class="text-xl font-bold text-slate-800">Preact Component</h3>
      <div class="flex items-center gap-6">
        <button
          onClick={() => setCount(c => c - 1)}
          class="w-10 h-10 flex items-center justify-center rounded-full bg-indigo-50 text-indigo-600 hover:bg-indigo-100 transition-colors text-xl font-bold"
        >
          -
        </button>
        <span class="text-4xl font-mono font-bold text-indigo-600 min-w-12 text-center">
          {count}
        </span>
        <button
          onClick={() => setCount(c => c + 1)}
          class="w-10 h-10 flex items-center justify-center rounded-full bg-indigo-600 text-white hover:bg-indigo-700 transition-colors text-xl font-bold"
        >
          +
        </button>
      </div>
      <p class="text-xs text-slate-400 mt-2">
        This is a Preact component managed by Nexy
      </p>
    </div>
  )
}
