# Task 30: Implement Link component with SPA navigation

## Problem

`nexy/link.py` is a stub (`def Link() -> None: return None`). Nexy needs a real `<Link>` component that:
- Works in Jinja2 templates as `{{ Link(...) }}`
- Supports SPA-style client-side navigation
- Intercepts clicks, uses History API to update URL
- Fetches new page content via fetch/XMLHttpRequest
- Falls back to normal `<a>` navigation for external links
- No `client:` attribute needed (better than Astro)

## Implementation

### 1. `nexy/link.py` — Implement Link function

```python
# Before:
def Link() -> None:
    return None

# After:
from typing import Optional

def Link(
    href: str,
    children: str = "",
    class_name: Optional[str] = None,
    target: Optional[str] = None,
    **kwargs: str,
) -> str:
    attrs = [f'href="{href}"']
    if class_name:
        attrs.append(f'class="{class_name}"')
    if target:
        attrs.append(f'target="{target}"')
    for k, v in kwargs.items():
        if v is not None:
            attrs.append(f'{k}="{v}"')
    attrs.append('data-nexy-link="true"')
    return f'<a {" ".join(attrs)}>{children}</a>'
```

### 2. `nexy/frontend/runtime.ts` — Add SPA navigation handler

Append to the runtime.ts (before `export {}`):

```typescript
// SPA navigation via Link component
document.addEventListener('click', (e) => {
    const target = e.target as HTMLElement;
    const link = target.closest('a[data-nexy-link="true"]') as HTMLAnchorElement;
    if (!link) return;
    
    const href = link.getAttribute('href');
    if (!href || href.startsWith('http') || href.startsWith('//') || href.startsWith('#')) return;
    
    e.preventDefault();
    const url = new URL(href, window.location.origin);
    
    // Update History API
    history.pushState({}, '', url.pathname + url.search);
    
    // Fetch new content
    fetch(url.pathname + url.search)
        .then(res => res.text())
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const main = doc.querySelector('[data-nexy-main]') || doc.body;
            const targetMain = document.querySelector('[data-nexy-main]') || document.body;
            targetMain.innerHTML = main.innerHTML;
            
            // Re-hydrate any islands
            document.querySelectorAll('[data-nexy-fw]').forEach(el => {
                delete (el as HTMLElement).dataset.nexyMounted;
            });
            const event = new CustomEvent('nexy:navigate', { detail: { url } });
            document.dispatchEvent(event);
        })
        .catch(err => console.error('[Nexy] SPA navigation failed:', err));
});

// Handle browser back/forward
window.addEventListener('popstate', () => {
    const event = new CustomEvent('nexy:popstate', { detail: { url: new URL(window.location.href) } });
    document.dispatchEvent(event);
});
```

### 3. `nexy/compiler/parser/template.py` — Add Link as reserved component

In the `TemplateParser.parse()` method, add `Link` to the reserved components:

```python
unknowns.remove("Link") if "Link" in unknowns else None  # Link is a reserved component
```

Add after line 73 (`unknowns.remove("Slot")`).

### 4. `nexy/__init__.py` — Ensure Link is exported

```python
# Already exports: from .template import Template
# Add Link export (if not already present)
```

## Search commands

```bash
rg "from nexy.link" nexy/
rg "Link" nexy/compiler/parser/template.py
rg "data-nexy" nexy/frontend/
```

## Verify

- [ ] `Link()` returns valid `<a>` HTML string
- [ ] Link with `href="/about"` renders `<a href="/about" data-nexy-link="true">...</a>`
- [ ] Clicking a Link triggers SPA navigation (not full page reload)
- [ ] External links (`https://...`) are not intercepted
- [ ] `data-nexy-main` content area is updated on navigation
- [ ] `nexy:navigate` custom event fires after navigation
- [ ] Browser back/forward triggers `nexy:popstate` event
- [ ] `ruff check nexy/` — no lint errors
- [ ] `python -m mypy nexy --strict` — no type errors
- [ ] `python -m pytest tests/ -v` — no regressions
