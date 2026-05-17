import { useState } from "react";

function Form({use=2}:{use:any}) {
    
    const [name, setName] = useState("");
    

    return (
        <form onSubmit={(e) => e.preventDefault()} className="max-w-80 border border-border dark:border-border/70 bg-gray-100/20 dark:bg-black/10  rounded-xl p-1 flex items-center ">
            <input 
                type="email" id="name" name="name" pattern=""
                placeholder="you@domaine.com"
                className="w-full outline-0 px-2 placeholder:text-sm bg-transparent" 
            />
            <button 
                type="submit"
                className=" cursor-pointer flex items-center justify-center gap-2 bg-yellow-300 px-4 py-2 rounded-lg uppercase text-xs font-medium text-black"
            >
                <span>Subcribe</span>
                <svg
                    viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
                    strokeLinecap="round" strokeLinejoin="round"
                    className="size-3.5"
                >
                    <path
                        d="M14.536 21.686a.5.5 0 0 0 .937-.024l6.5-19a.496.496 0 0 0-.635-.635l-19 6.5a.5.5 0 0 0-.024.937l7.93 3.18a2 2 0 0 1 1.112 1.11z" />
                    <path d="m21.854 2.147-10.94 10.939" />
                </svg>
            </button>
        </form>)
}


export default Form;