from nexy.core.models import FFModel

def vue() -> FFModel:
    return FFModel(
        name="vue",
        render=(
            '(function(){'
            'const w=window as any;'
            'const gi=w.__nexy_import||((p: any)=>import(/* @vite-ignore */ p));'
            'async function m(el: any){'
            'if(!el||el.dataset.nexyMounted==="1")return;'
            'el.dataset.nexyMounted="1";'
            'const key=el.getAttribute("data-nexy-key")||"";'
            'const path=el.dataset.nexyPath||"";'
            'const symbol=el.getAttribute("data-nexy-symbol")||"";'
            'const propsStr=el.dataset.nexyProps||"{}";'
            'let props={};'
            'try{props=JSON.parse(propsStr)}catch(e){}'
            'const ref= key || path;'
            'const mod=await gi(ref);'
            'const Comp=(mod&&mod.default)!==undefined?mod.default:(symbol&&mod&&mod[symbol]);'
            'const vue=await import("vue");'
            'const app=vue.createApp({render:()=>vue.h(Comp,props)});'
            'app.mount(el);'
            '}'
            'function init(){'
            'const nodes=w.document.querySelectorAll("[data-nexy-fw=\\"vue\\"]");'
            'nodes.forEach((el: any)=>{m(el)});'
            '}'
            'if(w.document.readyState==="loading"){'
            'w.document.addEventListener("DOMContentLoaded",init);'
            '}else{init()}'
            '})();'
        ),
        extension=["vue"],
    )