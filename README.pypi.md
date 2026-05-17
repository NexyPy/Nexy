# Nexy

Nexy is a modular, full-stack meta-framework designed to bridge the gap between **FastAPI** backends and **Vite-powered** frontend ecosystems such as React, Vue, Svelte, and Solid.js. Built on Python 3.10+, it enables the development of rich, interactive applications within a unified environment.

---

## Getting Started

Nexy leverages a streamlined workflow. The use of `uv` is recommended for optimal performance and dependency management.

### 1. Initialize Project
```bash
mkdir my_project && cd my_project
uv init && uv venv
```

### 2. Install and Initialize Nexy
```bash
uv add nexy && nexy init
# Alternative: pip install nexy && nexy init
```

### 3. Launch Development Server
```bash
nexy dev
```

---

## The .nexy Format (Server Components)

A `.nexy` or `.mdx` file serves as a **Server Component**. Internally, Nexy transforms these files into Python functions where the header contains the logic and the body defines the template.

```html
---
# Python Logic Layer
title : prop[str] = "Nexy Component"

from "@/components/Card.nexy" import Card
from "@/components/Chart.tsx" import Chart
from "@/assets/data.json" as config
---
<!-- Jinja2 Template Layer (Server-Side Rendered) -->
<div class="p-6 bg-white rounded-xl shadow-lg">
    <h1>{{ title }}</h1>
    
    <!-- Nexy Server Component -->
    <Card content="Server-side rendered content" />
    
    <!-- Frontend Island (React/Vue/Svelte) -->
    <Chart data="{{ config }}" />
</div>
```

### Core Features
*   **Typed Props**: Properties are defined using the `name : prop[type]` syntax.
*   **Polyglot Imports**: Direct import support for `.nexy`, `.vue`, `.tsx`, `.svelte`, `.mdx`, `.py`, `.json`, and image assets within the component header.
*   **Function Mapping**: A file named `users.nexy` is automatically mapped to a Python function named `Users()`.

---

## Routing Systems

Nexy provides two distinct routing strategies to accommodate different architectural requirements.

### 1. File-Based Routing
The directory structure within `src/routes/` automatically generates the application's URL schema. This system supports `.nexy`, `.mdx`, and `.py` files.

| File Path | URL | Resource Type |
| :--- | :--- | :--- |
| `index.nexy` | `/` | HTML Page |
| `about.mdx` | `/about` | Markdown Page |
| `blog/[slug].nexy` | `/blog/:slug` | Dynamic Page |
| `api/users.py` | `/api/users` | API Endpoint |

#### API Route Definitions (.py)
API routes are defined by standard Python functions corresponding to HTTP methods:
```python
def GET(slug: str):
    return {"message": f"Hello, {slug}"}

def POST():
    return {"status": "success"}
```

#### Dynamic Patterns
*   **[slug]**: Standard dynamic parameter.
*   **[...slug]**: Catch-all segments for deep nesting.
*   **name-[slug]**: Prefixed dynamic parameters.
*   **(group)**: Organizational folders that do not affect the URL path.

### 2. Module-Based Routing
For enterprise-level architectures, Nexy offers a decorator-based approach inspired by modular frameworks like NestJS.

```python
from nexy.decorators import Module, Controller

@Controller()
class AppController:
    def GET(self):
        return "Hello from Controller"

@Module()
class AppModule:
    controllers = [AppController]
    providers = []
    imports = []
```

---

## Nexy CLI (nx)

The `nexy` command-line interface (also accessible via the `nx` alias) manages the application lifecycle:

*   **nexy init**: Initializes the project configuration, including framework selection and Tailwind CSS integration.
*   **nexy dev**: Starts the development server with Hot Module Replacement (HMR) for both FastAPI and Vite.
*   **nexy build**: Compiles and optimizes assets for production deployment.
*   **nexy start**: Launches the production server.

---

## Technical Specifications

*   **Requirement**: Python 3.10+ and Node.js environment.
*   **Backend**: Built on FastAPI and Pydantic for high-performance data validation.
*   **Frontend**: Powered by Vite for near-instant builds and modern ecosystem compatibility.
*   **Security**: Automatic Jinja2 escaping and Pydantic-based prop validation to ensure architectural integrity.

---

## License
Distributed under the MIT License.