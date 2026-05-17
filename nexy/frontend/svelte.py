from nexy.core.models import FFModel

def svelte() -> FFModel:
    return FFModel(
        name="svelte",
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
            'const s=await import("svelte");'
            'const hasContent=el.innerHTML.trim().length>0;'
            'if(hasContent){'
            's.hydrate(Comp,{target:el,props:props});'
            '}else{'
            'el.innerHTML="";'
            's.mount(Comp,{target:el,props:props});'
            '}'
            '}'
            'function init(){'
            'const nodes=w.document.querySelectorAll("[data-nexy-fw=\\"svelte\\"]");'
            'nodes.forEach((el: any)=>{m(el)});'
            '}'
            'if(w.document.readyState==="loading"){'
            'w.document.addEventListener("DOMContentLoaded",init);'
            '}else{init()}'
            '})();'
        ),
        extension=["svelte"],
    )