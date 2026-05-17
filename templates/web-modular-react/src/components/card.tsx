import Counter from "./counter";

function Card() {
    return (
        <div
            className="w-full lg:w-1/2 md:h-full h-120 flex flex-col justify-between p-2  border-[1.34px] border-dashed  border-gray-500/30 rounded-2xl hover:rounded-3xl hover:border-4 hover:border-double hover:bg-[hsl(180,8%,3%)]/2 transition-all duration-300"
        >
            <p className="text-white/70 text-xs border border-white/40 rounded-full w-fit px-2 py-1">This is React component</p>
            <div className="flex justify-center items-center">
                <svg
                    width="100%" height="100%" viewBox="-10.5 -9.45 21 18.9"
                    fill="none" xmlns="http://www.w3.org/2000/svg"
                    className="uwu-hidden mt-4 mb-3 text-brand text-[#61DAFB] w-24 lg:w-28 self-center text-sm me-0 flex origin-center transition-all ease-in-out"
                >
                    <circle cx="0" cy="0" r="2" fill="currentColor"></circle>
                    <g stroke="currentColor" strokeWidth="1" fill="none">
                        <ellipse rx="10" ry="4.5"></ellipse>
                        <ellipse rx="10" ry="4.5" transform="rotate(60)"></ellipse>
                        <ellipse rx="10" ry="4.5" transform="rotate(120)"></ellipse>
                    </g>
                </svg>
            </div>
            <Counter />
        </div>
    )
}

export default Card;