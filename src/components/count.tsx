import { useState } from "react";

export function Count() {
    const [count, setCount] = useState(10);

    return (
        <div className="">
            <p>Count: {count}</p>
            <button 
                className="bg-white px-2 py-1 border "
                onClick={() => setCount(count + 1)}>Increment</button>
        </div>
    );
}