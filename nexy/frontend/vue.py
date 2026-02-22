from nexy.core.models import FFModel

def vue() -> FFModel:
    return FFModel(
        name="vue",
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
            'const vue=await import("vue");'
            'const app=vue.createApp({render:()=>vue.h(Comp,props)});'
            'app.mount(el);'
            '}'
            'function init(){'
            'const nodes=w.document.querySelectorAll("[data-nexy-fw=\\"vue\\"]");'
            'nodes.forEach(el=>{m(el)});'
            '}'
            'if(w.document.readyState==="loading"){'
            'w.document.addEventListener("DOMContentLoaded",init);'
            '}else{init()}'
            '})();'
        ),
        extension=["vue"],
    )
