import { createSignal,children as resolveChildren  } from 'solid-js';
import type { JSX } from 'solid-js';

type PropsType = {
  children: JSX.Element; 
  onClick: () => void;
};

function Button(props: PropsType) {
  const safeChildren = resolveChildren(() => props.children);
  return (
    <button
      onClick={props.onClick}
      className="z-10 size-8 cursor-pointer  flex items-center justify-center rounded-full border border-white/40 text-white bg-background/0.5 backdrop-blur-2xl hover:bg-indigo-100/20 transition-colors text-xl font-bold"
    >
      {safeChildren()}
    </button>
  )
}
export default function Counter() {
  const [count, setCount] = createSignal(0)

  return (
    <div className=" flex justify-end rounded-xl p-4 border border-white/40 hover:rounded-2xl hover:border-dashed hover:bg-[hsl(193,46%,29%)]/5 transition-all duration-300 ">
      <div className='flex-1 flex flex-col justify-between gap-2'>
        <p className='uppercase text-xs font-mono font-medium border border-white/40 text-white w-fit px-2 py-1 rounded-2xl'>Counter</p>
        <span className='text-6xl font-medium border-gray-300  text-white w-fit rounded-xl p-2'>{count()}</span>
      </div>
      <div className=" relative md:h-full   flex flex-col items-center justify-between p-1 border border-gray-50/40 rounded-full ">
        <button
          onClick={() => setCount(count() + 1)}
          className="z-10 cursor-pointer size-8 flex items-center justify-center rounded-full bg-white text-gray-950  hover:bg-yellow-500 transition-colors text-xl font-bold"
        >
          <AddIcon />
        </button>

        <div className='space-y-0.5px opacity-40 z-0 absolute top-1/2 -translate-y-1/2 '>
          {
            Array(30).fill(0).map((_, i) => (
              <div key={i} className='border-b border-white  w-5 h-0.5' />
            ))
          }
        </div>

        <Button
          onClick={() => setCount(count() - 1)}
        >
          <RemoveIcon/>
        </Button>
      </div>
    </div>
  )
}


const AddIcon = () => (
  <svg
    viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
    className='size-5'
  >
    <path d="M5 12h14" /><path d="M12 5v14" />
  </svg>
)

const RemoveIcon = () => (
  <svg
    width="24" height="24" viewBox="0 0 24 24" fill="none"
    stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
    className='size-5'
  >
    <path d="M5 12h14" />
  </svg>
)