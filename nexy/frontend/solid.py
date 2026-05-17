from nexy.core.models import FFModel

def solid() -> FFModel:
    return FFModel(
        name="solid",
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
            'const ref=key||path;'
            # OPTIMISATION : Chargement parallèle du composant et de Solid
            'const [mod, sw, {createComponent}] = await Promise.all(['
            'gi(ref),'
            'import("solid-js/web"),'
            'import("solid-js")'
            ']);'
            'const Comp=(mod&&mod.default)!==undefined?mod.default:(symbol&&mod&&mod[symbol]);'
            # REMPLACEMENT : On vide l'élément pour garantir que Solid prend le contrôle total (évite l'erreur .done)
            'el.innerHTML="";'
            'sw.render(() => createComponent(Comp, props), el);'
            '}'
            'function init(){'
            'const nodes=w.document.querySelectorAll("[data-nexy-fw=\\"solid\\"]");'
            'for(let i=0; i<nodes.length; i++) m(nodes[i]);'
            '}'
            'if(w.document.readyState==="loading"){'
            'w.document.addEventListener("DOMContentLoaded",init);'
            '}else{init()}'
            '})();'
        ),
        extension=["jsx", "tsx"],
    )