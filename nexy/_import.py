import hashlib
import json
from typing import Any, Callable, Dict
from nexy.core.config import Config


class Import:
    def __new__(cls, path: str, framework: str, symbol: str) -> Callable[..., str]:
        return _Importer(path=path, framework=framework, symbol=symbol)


class _Importer:
    def __init__(self, path: str, framework: str, symbol: str) -> None:
        self.path = path
        self.framework = framework.lower()
        self.symbol = symbol
        self._seq = 0
        self._cfg = Config()

    def __call__(self, **kwargs: Any) -> str:
        self._seq += 1
        mount_id = self._mount_id(self.path, self.symbol, self._seq)
        props = self._serialize_props(kwargs)
        script = self._script(self.framework, self.path, mount_id, props)
        return f'<div id="{mount_id}"></div><script type="module">{script}</script>'

    def _mount_id(self, path: str, symbol: str, seq: int) -> str:
        base = f"{path}|{symbol}|{seq}"
        h = hashlib.md5(base.encode()).hexdigest()[:10]
        return f"nexy-{h}"

    def _serialize_props(self, props: Dict[str, Any]) -> str:
        try:
            return json.dumps(props)
        except Exception:
            return "{}"

    def _script(self, framework: str, path: str, mount_id: str, props_json: str) -> str:
        url = path if path.startswith("/") else f"/{path}"
        desc = {
            "id": mount_id,
            "url": url,
            "props": props_json,
            "fw": framework,
        }
        runtime = """
        (() => {
          const d = DESC_PLACEHOLDER;
          const el = document.getElementById(d.id);
          if (!el) return;
          el.dataset.nexyId = d.id;
          const w = window;
          if (!w.__nexyR) {
            w.__nexyR = {
              q: [],
              roots: new Map(),
              fw: {},
              io: null,
              ready: false
            };
            const init = async () => {
              w.__nexyR.io = new IntersectionObserver((entries) => {
                entries.forEach((entry) => {
                  if (entry.isIntersecting) {
                    const id = entry.target.dataset.nexyId;
                    const item = w.__nexyR.q.find(x => x.id === id);
                    if (item) {
                      w.__nexyR.mount(item);
                    }
                    w.__nexyR.io.unobserve(entry.target);
                  }
                });
              }, { rootMargin: '120px' });
              w.__nexyR.ready = true;
              w.__nexyR.q.forEach((it) => {
                const target = document.getElementById(it.id);
                if (target) w.__nexyR.io.observe(target);
              });
              if ('requestIdleCallback' in w) {
                w.requestIdleCallback(() => {
                  w.__nexyR.q.forEach((it) => {
                    const target = document.getElementById(it.id);
                    if (target && target.getBoundingClientRect().top > window.innerHeight) {
                      // out-of-viewport kept lazy
                    }
                  });
                });
              }
            };
            w.__nexyR.mount = async (it) => {
              const target = document.getElementById(it.id);
              if (!target) return;
              const Comp = (await import(it.url)).default;
              if (it.fw === 'react') {
                if (!w.__nexyR.fw.react) {
                  const React = await import('react');
                  const RDC = await import('react-dom/client');
                  const createRoot = RDC.createRoot;
                  const hydrateRoot = RDC.hydrateRoot;
                  w.__nexyR.fw.react = { React, createRoot, hydrateRoot };
                }
                const { React, createRoot, hydrateRoot } = w.__nexyR.fw.react;
                const existing = w.__nexyR.roots.get(it.id);
                let root = existing;
                if (!root) {
                  if (hydrateRoot && target.hasChildNodes()) {
                    root = hydrateRoot(target, React.createElement(Comp, JSON.parse(it.props)));
                  } else {
                    root = createRoot(target);
                  }
                  w.__nexyR.roots.set(it.id, root);
                }
                if (root.render) {
                  root.render(React.createElement(Comp, JSON.parse(it.props)));
                }
              } else if (it.fw === 'preact') {
                if (!w.__nexyR.fw.preact) {
                  const preact = await import('preact');
                  w.__nexyR.fw.preact = { h: preact.h, render: preact.render };
                }
                const { h, render } = w.__nexyR.fw.preact;
                render(h(Comp, JSON.parse(it.props)), target);
              } else if (it.fw === 'svelte') {
                const props = JSON.parse(it.props);
                const opts = target.hasChildNodes() ? { target, hydrate: true, props } : { target, props };
                new Comp(opts);
              } else if (it.fw === 'vue') {
                if (!w.__nexyR.fw.vue) {
                  const vue = await import('vue');
                  w.__nexyR.fw.vue = { createApp: vue.createApp, h: vue.h };
                }
                const { createApp, h } = w.__nexyR.fw.vue;
                const props = JSON.parse(it.props);
                createApp({ render: () => h(Comp, props) }).mount(target);
              }
            };
            init();
          }
          w.__nexyR.q.push(d);
          if (w.__nexyR.ready && w.__nexyR.io) {
            w.__nexyR.io.observe(el);
          }
        })();
        """
        runtime = runtime.replace("DESC_PLACEHOLDER", json.dumps(desc))
        return runtime
