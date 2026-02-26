export type NexyFramework = "vue" | "nexy" | "react" | "svelte" | "rust" | "unknown";

export interface NexyImport {
  path: string;
  name: string;
  framework: NexyFramework;
}

export interface NexyProp {
  name: string;
  type: string;
  defaultValue?: string;
}

export type NexySection = "header" | "template";

export function detectFramework(importPath: string): NexyFramework {
  if (importPath.endsWith(".vue")) {return "vue";}
  if (importPath.endsWith(".nexy")) {return "nexy";}
  if (importPath.endsWith(".jsx") || importPath.endsWith(".tsx")) {return "react";}
  if (importPath.endsWith(".svelte")) {return "svelte";}
  if (importPath.endsWith(".rs")) {return "rust";}
  return "unknown";
}

export function parseHeader(text: string): { imports: NexyImport[]; props: NexyProp[] } {
  const imports: NexyImport[] = [];
  const props: NexyProp[] = [];

  // Use the framework's pattern for scanning (lenient with spaces)
  const headerMatch = text.match(/^\s*---\s*\n([\s\S]*?)\n\s*---\s*/m);
  if (!headerMatch) {
    return { imports, props };
  }

  const header = headerMatch[1];

  // Support parentheses and multi-line imports (LogicSanitizer inspiration)
  const importRegex =
    /^\s*from\s+["'](?<path>[^"']+)["']\s+import\s+(?<targets>.+?)(?=\n\S|$)/gms;
  
  let m: RegExpExecArray | null;
  while ((m = importRegex.exec(header)) !== null) {
    const path = m.groups?.path || "";
    const targetsRaw = m.groups?.targets || "";
    const fw = detectFramework(path);
    
    // Clean targets (remove parentheses, newlines, semicolons)
    const targets = targetsRaw
      .replace(/[()]/g, "")
      .replace(/;/g, "") // Fix for semicolons in imports
      .replace(/\n/g, " ")
      .split(",")
      .map((t) => t.trim())
      .filter((t) => t.length > 0);

    targets.forEach((target) => {
      // Handle "as alias"
      const parts = target.split(/\s+as\s+/i);
      const symbol = parts[0];
      const name = parts[1] || symbol;
      imports.push({ path, name, framework: fw });
    });
  }

  // Support for __Import and __nexy_loader__.import_component (Framework Philosophy)
  // Pattern: symbol = __Import(path="...", symbol="...", framework="...")
  const loaderRegex = /^\s*(?<alias>\w+)\s*=\s*(?:__Import|__nexy_loader__\.import_component)\s*\(\s*path\s*=\s*["'](?<path>[^"']+)["']\s*,\s*symbol\s*=\s*["'](?<symbol>[^"']+)["']\s*(?:,\s*framework\s*=\s*["'](?<fw>[^"']+)["'])?\s*\)/gm;
  while ((m = loaderRegex.exec(header)) !== null) {
    const path = m.groups?.path || "";
    const alias = m.groups?.alias || "";
    const symbol = m.groups?.symbol || "";
    const fw_str = m.groups?.fw;
    const fw = fw_str ? (fw_str as NexyFramework) : detectFramework(path);
    
    imports.push({ path, name: alias || symbol, framework: fw });
  }

  const propRegex =
    /^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*prop\[([^\]]*)\](?:\s*=\s*(.+))?/gm;
  while ((m = propRegex.exec(header)) !== null) {
    props.push({
      name: m[1],
      type: m[2].trim(),
      defaultValue: m[3]?.trim(),
    });
  }

  return { imports, props };
}

export function getSection(text: string, offset: number): NexySection {
  const headerMatch = text.match(/^\s*---\s*\n([\s\S]*?)\n\s*---\s*/m);
  if (!headerMatch || headerMatch.index === undefined) {
    return "template";
  }

  const headerStart = headerMatch.index;
  const headerEnd = headerMatch.index + headerMatch[0].length;

  if (offset >= headerStart && offset <= headerEnd) {
    return "header";
  }
  return "template";
}

export function getTemplate(text: string): string {
  // Use the framework's scanner pattern for consistency
  const match = text.match(/^\s*---\s*(?:[\s\S]*?)\s*---\s*(?<template>.*)/s);
  if (match && match.groups?.template) {
    return match.groups.template.trim();
  }
  return text.trim();
}

export function findUsedComponentsInTemplate(text: string): string[] {
  const template = getTemplate(text);
  const usedComponents = [...template.matchAll(/<([A-Z][A-Za-z0-9]*)/g)].map(
    (match) => match[1],
  );
  return Array.from(new Set(usedComponents));
}

export function parseImports(text: string): Map<string, string> {
  const map = new Map<string, string>();
  const { imports } = parseHeader(text);

  for (const imp of imports) {
    if (imp.framework !== "unknown") {
      map.set(imp.name, imp.framework);
    }
  }

  return map;
}
