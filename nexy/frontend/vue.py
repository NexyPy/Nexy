from nexy.core.models import FFModel

def vue() -> FFModel:
    render_script = """
    (async function() {
        const w = window;
        if (w.__nexy_vue_init) return;
        w.__nexy_vue_init = true;

        const gi = w.__nexy_import || ((p) => import(/* @vite-ignore */ p));

        let Vue;
        try {
            Vue = await import("vue");
        } catch(e) {
            console.error("[Nexy] Failed to load Vue runtime:", e);
            return;
        }

        async function m(el) {
            if (!el || el.dataset.nexyMounted === "1") return;
            
            const key = el.getAttribute("data-nexy-key") || "";
            const path = el.dataset.nexyPath || "";
            const symbol = el.getAttribute("data-nexy-symbol") || "";
            const propsStr = el.dataset.nexyProps || "{}";
            const serverHTML = el.innerHTML;

            let props = {};
            try { 
                props = JSON.parse(propsStr); 
            } catch(e) {}

            let slots = {};
            if (props.children === true || props.children === "true") {
                slots.default = () => Vue.h("div", {
                    innerHTML: serverHTML,
                    style: { display: "contents" }
                });
                delete props.children;
            }

            el.dataset.nexyMounted = "1";
            const ref = key || path;
            if (!ref) return;

            try {
                const mod = await gi(ref);
                
                // ENHANCED VUE COMPONENT RESOLUTION
                let Comp = null;
                if (symbol && mod[symbol]) {
                    Comp = mod[symbol];
                } else if (mod.__vccOpts) {
                    // Direct Vite/Vue compiled object
                    Comp = mod;
                } else if (mod.default) {
                    // Standard export default
                    Comp = mod.default;
                } else {
                    // Fallback to the module itself
                    Comp = mod;
                }

                // Final check: Vue components are usually objects or functions
                if (!Comp || (typeof Comp !== 'object' && typeof Comp !== 'function')) {
                    throw new Error(`The module at ${ref} does not export a valid Vue component.`);
                }

                const app = (serverHTML.trim() !== "" && !slots.default)
                    ? Vue.createSSRApp({ render: () => Vue.h(Comp, props, slots) })
                    : Vue.createApp({ render: () => Vue.h(Comp, props, slots) });

                app.mount(el);
            } catch(e) {
                console.error(`[Nexy] Execution error in ${ref}:`, e);
                // Unmark so it can be retried or debugged
                el.dataset.nexyMounted = "0";
            }
        }

        function init() {
            const nodes = document.querySelectorAll('[data-nexy-fw="vue"]');
            nodes.forEach(m);
        }

        if (document.readyState === "loading") {
            document.addEventListener("DOMContentLoaded", init);
        } else {
            init();
        }
    })();
    """

    return FFModel(
        name="vue",
        render=render_script,
        extension=["vue"],
    )