from nexy.core.models import FFModel

def preact() -> FFModel:
    return FFModel(
        name="preact",
        render=(
            '(function(){'
            'const w=window;'
            'const gi=w.__nexy_import||((p)=>import(/* @vite-ignore */ p));'
            'async function m(el){'
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
            'const preact=await import("preact");'
            'preact.render(preact.h(Comp,props),el);'
            '}'
            'function init(){'
            'const nodes=w.document.querySelectorAll("[data-nexy-fw=\\"preact\\"]");'
            'nodes.forEach(el=>{m(el)});'
            '}'
            'if(w.document.readyState==="loading"){'
            'w.document.addEventListener("DOMContentLoaded",init);'
            '}else{init()}'
            '})();'
        ),
        extension=["jsx", "tsx"],
    )
