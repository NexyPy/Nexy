from nexy.core.models import FFModel

def react() -> FFModel:
    return FFModel(
        name="react",
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
            'const React=await import("react");'
            'const RDC=await import("react-dom/client");'
            'const root=RDC.createRoot(el);'
            'root.render(React.createElement(React.StrictMode,null,React.createElement(Comp,props)));'
            '}'
            'function init(){'
            'const nodes=w.document.querySelectorAll("[data-nexy-fw=\\"react\\"]");'
            'nodes.forEach(el=>{m(el)});'
            '}'
            'if(w.document.readyState==="loading"){'
            'w.document.addEventListener("DOMContentLoaded",init);'
            '}else{init()}'
            '})();'
        ),
        extension=["jsx", "tsx"],
    )
