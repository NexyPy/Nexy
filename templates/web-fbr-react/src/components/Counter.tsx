import { useState } from 'react'

export default function Counter() {
  const [count, setCount] = useState(0)

  return (
    <div className="flex flex-col items-center gap-4 p-6 bg-white rounded-xl shadow-lg border border-gray-100">
      <h3 className="text-xl font-bold text-gray-800">React Component</h3>
      <div className="flex items-center gap-6">
        <button
          onClick={() => setCount(c => c - 1)}
          className="w-10 h-10 flex items-center justify-center rounded-full bg-indigo-50 text-indigo-600 hover:bg-indigo-100 transition-colors text-xl font-bold"
        >
          -
        </button>
        <span className="text-4xl  font-mono font-bold text-indigo-600 min-w-12 text-center">
          {count}
        </span>
        <button
          onClick={() => setCount(c => c + 1)}
          className="w-10 h-10 flex items-center justify-center rounded-full bg-indigo-600 text-white hover:bg-indigo-700 transition-colors text-xl font-bold"
        >
          +
        </button>
      </div>
      <p className="text-sm text-gray-500 italic">
        This is a standard React component managed by Nexy
      </p>
    </div>
  )
}
