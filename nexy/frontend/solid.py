from nexy.core.models import FFModel

def solid() -> FFModel:
    return FFModel(
        name="solid",
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
            'const { render } = await import("solid-js/web");'
            'const { createComponent } = await import("solid-js");'
            'render(() => createComponent(Comp, props), el);'
            '}'
            'function init(){'
            'const nodes=w.document.querySelectorAll("[data-nexy-fw=\\"solid\\"]");'
            'nodes.forEach(el=>{m(el)});'
            '}'
            'if(w.document.readyState==="loading"){'
            'w.document.addEventListener("DOMContentLoaded",init);'
            '}else{init()}'
            '})();'
        ),
        extension=["jsx", "tsx"],
    )
