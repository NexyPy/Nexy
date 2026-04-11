# Nexy

Nexy is a modular fullstack meta-framework designed to simplify modern web development. By bridging the gap between FastAPI backends and Vite-powered frontend ecosystems (React, Vue, Svelte, Solid.js), Nexy 2 allows you to build rich, interactive applications within a unified Python environment.

## The Nexy 2 Vision

Nexy 2 transforms the development experience by masking complex architectural patterns behind an intuitive interface. The framework handles the orchestration between the Python server and the JavaScript client, allowing you to focus exclusively on business logic and UI.

## Core Concepts

Mastering Nexy involves three essential pillars:

### 1. The .nexy Format (Polyglot Component)
While Nexy is fully functional for pure backend development (FastAPI-based APIs), the `.nexy` file is its powerful optional unit for building fullstack interfaces. It allows for a fluid composition of multiple languages:
- **Header (Python)**: Defined within `---` blocks, this is where you declare properties (`prop`) and import components (whether they are `.nexy`, `.vue`, `.tsx`, `.mdx`, or even Python functions).
- **Template (HTML/Jinja2)**: The structure of your component, rendered server-side with the power of Jinja2.

```html
---
# Definition Logic (Python)
title : prop[str] = "Nexy Component"
from "@/components/Card.nexy" import Card
from nexy import Vite  # Automatic asset injection
---
<!-- Server Rendering (Jinja2) -->
<div class="p-6 bg-white rounded-xl shadow-lg">
    <h1 class="text-2xl font-bold">{{ title }}</h1>
    <Card content="I can contain other components." />
</div>
```

### 2. Intelligent Hybrid Routing
Nexy scales with your project size:
- **File-Based Routing**: Your `src/routes/` directory structure defines your URLs (e.g., `index.nexy` -> `/`).
- **Module-Based Routing**: For enterprise architectures, use a modular approach inspired by NestJS.
- **Hybrid Rendering**: Mix static pages and dynamic API routes within the same project.

### 3. Unified Ecosystem via Vite
Nexy is framework-agnostic. You can import and use React, Vue, Svelte, or Solid.js components directly within your Nexy templates. The Vite build pipeline handles everything, ensuring optimal performance and zero configuration.

## Tooling and Development

### Nexy CLI (nx)
The `nx` command-line tool centralizes your development workflow:
- `nx init` or `nexy init`: Initializes a Nexy project.
- `nx dev` or `nexy dev`: Starts the Nexy server for development with Vite in parallel.
- `nx build` or `nexy build`: Compiles your assets for optimized production deployment.
- `nx start` or `nexy start`: Starts the Nexy server for production without Vite in parallel.

### VS Code Extension (Alpha)
A dedicated extension (LSP) is included in the repository (currently in **Alpha**) to provide a first-class development experience: real-time diagnostics, prop and import auto-completion, and contextual snippets.

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+

### Installation
```bash
pip install nexy
```

### Project Initialization
```bash
nexy init
```
The interactive assistant will help you choose your preferred frontend framework and enable Tailwind CSS.

### Run
```bash
nexy dev
```

## Security and Reliability
- **Strict Typing**: Pydantic integration for robust data and prop validation.
- **Native Protection**: Automatic Jinja2 character escaping against XSS vulnerabilities.
- **Architectural Integrity**: Built on SOLID principles for long-term maintainability.

## License
Distributed under the MIT License.
