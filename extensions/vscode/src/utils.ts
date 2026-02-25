import * as vscode from "vscode";

export const FRAMEWORK_COLORS: Record<string, string> = {
  vue:    "#42b883",
  nexy:   "#a8ff78",
  react:  "#61dafb",
  svelte: "#ff3e00",
};

export function detectFramework(importPath: string): string | null {
  if (importPath.endsWith(".vue")) return "vue";
  if (importPath.endsWith(".nexy")) return "nexy";
  if (importPath.endsWith(".jsx") || importPath.endsWith(".tsx")) return "react";
  if (importPath.endsWith(".svelte")) return "svelte";
  return null;
}

export function parseImports(text: string): Map<string, string> {
  const map = new Map<string, string>();
  const headerMatch = text.match(/^---\s*\n([\s\S]*?)\n---/m);
  if (!headerMatch) return map;

  const header = headerMatch[1];
  const importRegex =
    /^from\s+["']([^"']+)["']\s+import\s+([A-Za-z_][A-Za-z0-9_]*(?:\s*,\s*[A-Za-z_][A-Za-z0-9_]*)*)/gm;

  let match;
  while ((match = importRegex.exec(header)) !== null) {
    const framework = detectFramework(match[1]);
    if (framework) {
      match[2].split(",").map((n) => n.trim()).forEach((name) => {
        map.set(name, framework);
      });
    }
  }
  return map;
}

export function findComponentRanges(
  document: vscode.TextDocument,
  componentName: string
): vscode.Range[] {
  const ranges: vscode.Range[] = [];
  const text = document.getText();
  const regex = new RegExp(`(<\\/?(${componentName}))(?=[\\s/>])`, "g");

  let match;
  while ((match = regex.exec(text)) !== null) {
    const nameOffset = match[1].startsWith("</") ? 2 : 1;
    const startOffset = match.index + nameOffset;
    const endOffset = startOffset + componentName.length;
    ranges.push(new vscode.Range(
      document.positionAt(startOffset),
      document.positionAt(endOffset)
    ));
  }
  return ranges;
}

// ─── Parse les props déclarées dans le header ─────────────────────────────────
export interface NexyProp {
  name: string;
  type: string;
  defaultValue?: string;
}

export function parseProps(text: string): NexyProp[] {
  const props: NexyProp[] = [];
  const headerMatch = text.match(/^---\s*\n([\s\S]*?)\n---/m);
  if (!headerMatch) return props;

  const header = headerMatch[1];
  const propRegex =
    /^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*prop\[([^\]]*)\](?:\s*=\s*(.+))?/gm;

  let match;
  while ((match = propRegex.exec(header)) !== null) {
    props.push({
      name: match[1],
      type: match[2].trim(),
      defaultValue: match[3]?.trim(),
    });
  }
  return props;
}

// ─── Retourne la section du document (header ou template) ────────────────────
export type NexySection = "header" | "template" | "unknown";

export function getSection(text: string, offset: number): NexySection {
  const headerMatch = text.match(/^---\s*\n([\s\S]*?)\n---/m);
  if (!headerMatch || headerMatch.index === undefined) return "template";

  const headerStart = headerMatch.index;
  const headerEnd = headerMatch.index + headerMatch[0].length;

  if (offset >= headerStart && offset <= headerEnd) return "header";
  return "template";
}
