import {
  CodeAction,
  CodeActionKind,
  CodeActionParams,
} from "vscode-languageserver/node";
import { TextDocument } from "vscode-languageserver-textdocument";
import { parseNexyConfig } from "../../shared/nexy.config.parser";
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
    
    // DevX Logic: Search in src/components or via Aliases
    let importPath = `./components/${componentName}.nexy`;
    try {
      const currentFilePath = fileURLToPath(doc.uri);
      const currentDir = path.dirname(currentFilePath);
      
      // Find workspace root
      let workspaceRoot = currentDir;
      while (workspaceRoot !== path.parse(workspaceRoot).root) {
        if (fs.existsSync(path.join(workspaceRoot, "nexyconfig.py"))) break;
        workspaceRoot = path.dirname(workspaceRoot);
      }

      const config = parseNexyConfig(workspaceRoot);
      const componentsDir = path.join(workspaceRoot, "src", "components");
      const exts = [".nexy", ".vue", ".tsx", ".jsx", ".svelte"];
      
      for (const ext of exts) {
        const fullPath = path.join(componentsDir, componentName + ext);
        if (fs.existsSync(fullPath)) {
          // Check if we can use an alias
          let usedAlias = false;
          for (const [alias, replacement] of Object.entries(config.useAliases)) {
            const aliasFullPath = path.resolve(workspaceRoot, replacement);
            if (fullPath.startsWith(aliasFullPath)) {
              const relativeToAlias = path.relative(aliasFullPath, fullPath).split(path.sep).join("/");
              importPath = `${alias}/${relativeToAlias}`;
              usedAlias = true;
              break;
            }
          }

          if (!usedAlias) {
            const rel = path.relative(currentDir, fullPath);
            importPath = (rel.startsWith(".") ? rel : `./${rel}`).split(path.sep).join("/");
          }
          break;
        }
      }
    } catch {}

    return [{
      title: `Add import for "${componentName}" (${importPath})`,
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
      title: diagnostic.code === "nexy.unusedImport" ? "Remove unused import" : "Remove unused prop",
      kind: CodeActionKind.QuickFix,
      diagnostics: [diagnostic],
      edit: { changes: { [doc.uri]: [{ range: { start: doc.positionAt(lineStart), end: doc.positionAt(lineEnd) }, newText: "" }] } }
    };
  }
}
