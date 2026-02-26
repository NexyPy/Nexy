import {
  CodeAction,
  CodeActionKind,
  CodeActionParams,
} from "vscode-languageserver/node";
import { TextDocument } from "vscode-languageserver-textdocument";
import * as path from "path";
import * as fs from "fs";
import { fileURLToPath } from "url";

export class CodeActionHandler {
  public handle(params: CodeActionParams, doc: TextDocument): CodeAction[] {
    const text = doc.getText();
    const actions: CodeAction[] = [];

    for (const diagnostic of params.context.diagnostics) {
      if (diagnostic.source !== "nexy" || !diagnostic.code) continue;

      if (diagnostic.code === "nexy.missingImport") {
        actions.push(...this.getMissingImportActions(doc, text, diagnostic));
      } else if (diagnostic.code === "nexy.unusedImport" || diagnostic.code === "nexy.unusedProp") {
        actions.push(this.getRemoveUnusedAction(doc, text, diagnostic));
      }
    }
    return actions;
  }

  private getMissingImportActions(doc: TextDocument, text: string, diagnostic: any): CodeAction[] {
    const componentName = text.slice(doc.offsetAt(diagnostic.range.start), doc.offsetAt(diagnostic.range.end));
    const headerMatch = text.match(/^---\s*$/m);
    if (!headerMatch || headerMatch.index === undefined) return [];

    const insertPosition = doc.positionAt(text.indexOf("\n", headerMatch.index) + 1);
    
    // DevX Logic: Search in src/components
    let importPath = `./components/${componentName}.nexy`;
    try {
      const currentFilePath = fileURLToPath(doc.uri);
      const workspaceRoot = currentFilePath.split(path.sep + "src" + path.sep)[0];
      if (workspaceRoot) {
        const componentsDir = path.join(workspaceRoot, "src", "components");
        const exts = [".nexy", ".vue", ".tsx", ".jsx", ".svelte"];
        for (const ext of exts) {
          if (fs.existsSync(path.join(componentsDir, componentName + ext))) {
            const rel = path.relative(path.dirname(currentFilePath), path.join(componentsDir, componentName + ext));
            importPath = (rel.startsWith(".") ? rel : `./${rel}`).split(path.sep).join("/");
            break;
          }
        }
      }
    } catch {}

    return [{
      title: `Ajouter l'import pour "${componentName}" (${importPath})`,
      kind: CodeActionKind.QuickFix,
      diagnostics: [diagnostic],
      edit: { changes: { [doc.uri]: [{ range: { start: insertPosition, end: insertPosition }, newText: `from "${importPath}" import ${componentName}\n` }] } }
    }];
  }

  private getRemoveUnusedAction(doc: TextDocument, text: string, diagnostic: any): CodeAction {
    const start = doc.offsetAt(diagnostic.range.start);
    const lineStart = text.lastIndexOf("\n", start - 1) + 1;
    let lineEnd = text.indexOf("\n", doc.offsetAt(diagnostic.range.end));
    lineEnd = lineEnd === -1 ? text.length : lineEnd + 1;

    return {
      title: diagnostic.code === "nexy.unusedImport" ? "Supprimer l'import inutilisé" : "Supprimer la prop inutilisée",
      kind: CodeActionKind.QuickFix,
      diagnostics: [diagnostic],
      edit: { changes: { [doc.uri]: [{ range: { start: doc.positionAt(lineStart), end: doc.positionAt(lineEnd) }, newText: "" }] } }
    };
  }
}
