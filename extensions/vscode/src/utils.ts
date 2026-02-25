import * as vscode from "vscode";
import {
  detectFramework,
  parseHeader,
  type NexyFramework,
  type NexyProp,
  type NexySection,
  getSection,
} from "./shared/nexyParser";

export const FRAMEWORK_COLORS: Record<NexyFramework, string> = {
  vue: "#42b883",
  nexy: "#a8ff78",
  react: "#61dafb",
  svelte: "#ff3e00",
  unknown: "#cccccc",
};

export { detectFramework, parseHeader, type NexyProp, type NexySection, getSection };

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

export function findComponentRanges(
  document: vscode.TextDocument,
  componentName: string,
): vscode.Range[] {
  const ranges: vscode.Range[] = [];
  const text = document.getText();
  const regex = new RegExp(`(<\\/?(${componentName}))(?=[\\s/>])`, "g");

  let match: RegExpExecArray | null;
  while ((match = regex.exec(text)) !== null) {
    const nameOffset = match[1].startsWith("</") ? 2 : 1;
    const startOffset = match.index + nameOffset;
    const endOffset = startOffset + componentName.length;
    ranges.push(
      new vscode.Range(
        document.positionAt(startOffset),
        document.positionAt(endOffset),
      ),
    );
  }
  return ranges;
}

