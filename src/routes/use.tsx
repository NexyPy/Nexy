type propsType = {
    theme : string | undefined
}
export const User = (props:propsType)=>(
    <div className="" style={{backgroundColor:props.theme}}>Junior 🐦‍🔥</div>
)