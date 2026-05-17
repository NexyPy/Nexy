from nexy.core.models import FFModel

def react() -> FFModel:
    render_script = """
    (async function() {
        const w = window;
        if (w.__nexy_react_init) return;
        w.__nexy_react_init = true;

        const gi = w.__nexy_import || ((p) => import(/* @vite-ignore */ p));

        let React, RDC;
        try {
            [React, RDC] = await Promise.all([
                import("react"),
                import("react-dom/client")
            ]);
        } catch(e) {
            console.error("[Nexy] Failed to load React runtimes:", e);
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
            } catch(e) {
                console.error("[Nexy] Failed to parse props:", e);
            }

            if (props.children === true || props.children === "true") {
                props.children = React.createElement("div", {
                    dangerouslySetInnerHTML: { __html: serverHTML },
                    style: { display: "contents" },
                    suppressHydrationWarning: true
                });
            }

            el.dataset.nexyMounted = "1";
            const ref = key || path;
            if (!ref) return;

            try {
                const mod = await gi(ref);
                
                // Robust Export Resolution
                let Comp = null;
                if (symbol && mod[symbol]) {
                    Comp = mod[symbol];
                } else if (mod.default) {
                    Comp = mod.default;
                } else {
                    // Fallback for modules that export the component directly
                    Comp = mod;
                }

                if (!Comp || (typeof Comp !== 'function' && typeof Comp.render !== 'function')) {
                    throw new Error(`No valid React component found in ${ref}. Check your exports.`);
                }

                const element = React.createElement(
                    React.StrictMode, 
                    null, 
                    React.createElement(Comp, props)
                );

                if (serverHTML.trim() !== "" && !(props.children)) {
                    RDC.hydrateRoot(el, element);
                } else {
                    const root = RDC.createRoot(el);
                    root.render(element);
                }
            } catch(e) {
                console.error(`[Nexy] Execution error in ${ref}:`, e);
            }
        }

        function init() {
            const nodes = document.querySelectorAll('[data-nexy-fw="react"]');
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
        name="react",
        render=render_script,
        extension=["jsx", "tsx"],
    )