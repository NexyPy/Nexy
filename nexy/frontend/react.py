from nexy.core.models import FFModel

def react() -> FFModel:
    return FFModel(
        name="react",
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
            'const React=await import("react");'
            'const RDC=await import("react-dom/client");'
            'const root=RDC.createRoot(el);'
            'root.render(React.createElement(Comp,props));'
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
