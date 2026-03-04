
type TabType = {
    label: string
}
const tab: TabType[] = [
    { label: "espoir" },
    { label: "force" },
    { label: "Loemba" },
    { label: "Loea" },
    { label: "klkl" },
    { label: "hope" },
]

export function Card() {
    
    const x = 3 / 0
    // setTimeout(() => {
    

    console.log(x);

    return (
        <>
            <div className="flex gap-2 caret-indigo-300 border p-2 px-4 rounded-lg">
                {
                    tab.map(e => {
                        return <p key={e.label}>{e.label}</p>
                    })
                }
            </div>
           
        </>
    )

}