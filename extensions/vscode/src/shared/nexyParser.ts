export type NexyFramework = "vue" | "nexy" | "react" | "svelte" | "unknown";

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
  if (importPath.endsWith(".vue")) return "vue";
  if (importPath.endsWith(".nexy")) return "nexy";
  if (importPath.endsWith(".jsx") || importPath.endsWith(".tsx")) return "react";
  if (importPath.endsWith(".svelte")) return "svelte";
  return "unknown";
}

export function parseHeader(text: string): { imports: NexyImport[]; props: NexyProp[] } {
  const imports: NexyImport[] = [];
  const props: NexyProp[] = [];

  const headerMatch = text.match(/^---\s*\n([\s\S]*?)\n---/m);
  if (!headerMatch) {
    return { imports, props };
  }

  const header = headerMatch[1];

  const importRegex =
    /^from\s+["']([^"']+)["']\s+import\s+([A-Za-z_][A-Za-z0-9_]*(?:\s*,\s*[A-Za-z_][A-Za-z0-9_]*)*)/gm;
  let m: RegExpExecArray | null;
  while ((m = importRegex.exec(header)) !== null) {
    const fw = detectFramework(m[1]);
    m[2]
      .split(",")
      .map((n) => n.trim())
      .forEach((name) => {
        imports.push({ path: m?.[1] || "", name, framework: fw });
      });
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
  const headerMatch = text.match(/^---\s*\n([\s\S]*?)\n---/m);
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
  const templateMatch = text.match(/^---[\s\S]*?---\n([\s\S]*)$/m);
  if (!templateMatch) {
    return text;
  }
  return templateMatch[1];
}

export function findUsedComponentsInTemplate(text: string): string[] {
  const template = getTemplate(text);
  const usedComponents = [...template.matchAll(/<([A-Z][A-Za-z0-9]*)/g)].map(
    (match) => match[1],
  );
  return Array.from(new Set(usedComponents));
}

