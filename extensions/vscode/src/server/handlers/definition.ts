import {
  Definition,
  Location,
  Range,
  TextDocumentPositionParams,
} from "vscode-languageserver/node";
import { TextDocument } from "vscode-languageserver-textdocument";
import {
  parseHeader,
  getSection,
  type NexyImport,
  type NexyProp,
} from "../../shared/nexy.parser";
import { parseNexyConfig, resolveWithAlias } from "../../shared/nexy.config.parser";
import * as fs from "fs";
import { fileURLToPath, pathToFileURL } from "url";
import * as path from "path";

export class DefinitionHandler {
  public handle(params: TextDocumentPositionParams, doc: TextDocument): Definition | null {
    const text = doc.getText();
    const offset = doc.offsetAt(params.position);
    const { imports, props } = parseHeader(text);

    let start = offset;
    while (start > 0 && /[\w./-]/.test(text[start - 1])) start--;
    let end = offset;
    while (end < text.length && /[\w./-]/.test(text[end])) end++;
    const word = text.slice(start, end);

    // 1. Check if it's an imported component
    const imp = imports.find(i => i.name === word);
    if (imp) {
      return this.getComponentDefinition(doc, imp);
    }

    // 2. Check if it's a prop defined in header
    const prop = props.find(p => p.name === word);
    if (prop) {
      const propRegex = new RegExp(`^\\s*${prop.name}\\s*:`, "m");
      const match = text.match(propRegex);
      if (match && match.index !== undefined) {
        const pos = doc.positionAt(match.index);
        return Location.create(doc.uri, Range.create(pos, pos));
      }
    }

    // 3. Check if it's a path in a "from" statement
    const lineStart = text.lastIndexOf("\n", offset - 1) + 1;
    const lineEnd = text.indexOf("\n", offset);
    const lineText = text.slice(lineStart, lineEnd === -1 ? text.length : lineEnd);
    const pathMatch = lineText.match(/from\s+["']([^"']+)["']/);
    if (pathMatch && (word.includes("/") || word.includes("."))) {
       return this.getPathDefinition(doc, pathMatch[1]);
    }

    return null;
  }

  private getComponentDefinition(doc: TextDocument, imp: NexyImport): Definition | null {
    const docPath = fileURLToPath(doc.uri);
    const currentDir = path.dirname(docPath);
    
    let workspaceRoot = currentDir;
    while (workspaceRoot !== path.parse(workspaceRoot).root) {
      if (fs.existsSync(path.join(workspaceRoot, "nexyconfig.py"))) break;
      workspaceRoot = path.dirname(workspaceRoot);
    }

    const config = parseNexyConfig(workspaceRoot);
    const aliasResolved = resolveWithAlias(imp.path, workspaceRoot, config.useAliases);
    const finalPath = aliasResolved || path.resolve(currentDir, imp.path);

    if (fs.existsSync(finalPath)) {
      return Location.create(pathToFileURL(finalPath).toString(), Range.create(0, 0, 0, 0));
    }
    return null;
  }

  private getPathDefinition(doc: TextDocument, filePath: string): Definition | null {
    const docPath = fileURLToPath(doc.uri);
    const currentDir = path.dirname(docPath);
    
    let workspaceRoot = currentDir;
    while (workspaceRoot !== path.parse(workspaceRoot).root) {
      if (fs.existsSync(path.join(workspaceRoot, "nexyconfig.py"))) break;
      workspaceRoot = path.dirname(workspaceRoot);
    }

    const config = parseNexyConfig(workspaceRoot);
    const aliasResolved = resolveWithAlias(filePath, workspaceRoot, config.useAliases);
    const finalPath = aliasResolved || path.resolve(currentDir, filePath);

    if (fs.existsSync(finalPath)) {
      return Location.create(pathToFileURL(finalPath).toString(), Range.create(0, 0, 0, 0));
    }
    return null;
  }
}
