# Nexy

Nexy is a modular fullstack meta-framework designed to simplify modern web development. By bridging the gap between FastAPI backends and Vite-powered frontend ecosystems (React, Vue, Svelte, Solid.js), Nexy 2 allows you to build rich, interactive applications within a unified Python environment.

## The Nexy 2 Vision

Nexy 2 transforms the development experience by masking complex architectural patterns behind an intuitive interface. The framework handles the orchestration between the Python server and the JavaScript client, allowing you to focus exclusively on business logic and UI.

## Core Concepts

Mastering Nexy involves three essential pillars:

### 1. The .nexy Format (Polyglot Component)
The fundamental unit of Nexy is the `.nexy` file. Unlike traditional frameworks, it allows for a fluid composition of multiple languages:
- **Header (Python)**: Defined within `---` blocks, this is where you declare properties (`prop`) and import components (whether they are `.nexy`, `.vue`, `.tsx`, or even Python functions).
- **Template (HTML/Jinja2)**: The structure of your component, rendered server-side with the power of Jinja2.
- **Script & Style (Optional)**: Integrate JavaScript/TypeScript or CSS (Tailwind native) directly into your component. These blocks are extracted and optimized by Vite.

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

<script>
    // Client Interactivity (Optional)
    // Managed by Vite with HMR support
    console.log("Nexy component hydrated");
</script>
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
- `nx dev`: Starts both the FastAPI server and the Vite dev server in parallel.
- `nx build`: Compiles your assets for optimized production deployment.

### VS Code Extension
A dedicated extension (LSP) is included in the repository to provide a first-class development experience: real-time diagnostics, prop and import auto-completion, and contextual snippets.

## Getting Started

### Prerequisites
- Python 3.12+
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
nx dev
```

## Security and Reliability
- **Strict Typing**: Pydantic integration for robust data and prop validation.
- **Native Protection**: Automatic Jinja2 character escaping against XSS vulnerabilities.
- **Architectural Integrity**: Built on SOLID principles for long-term maintainability.

## License

Nexy is open-source software licensed under the [MIT License](LICENSE).
