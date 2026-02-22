from nexy.core.models import FFModel

def preact() -> FFModel:
    return FFModel(
        name="preact",
        render=(
            '(function(){'
            'const w=window;'
            'async function m(el){'
            'if(!el||el.dataset.nexyMounted==="1")return;'
            'el.dataset.nexyMounted="1";'
            'const path=el.dataset.nexyPath;'
            'const propsStr=el.dataset.nexyProps||"{}";'
            'let props={};'
            'try{props=JSON.parse(propsStr)}catch(e){}'
            'const mod=await import(path);'
            'const Comp=mod.default;'
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
