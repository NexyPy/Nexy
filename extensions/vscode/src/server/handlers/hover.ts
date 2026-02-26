import {
  Hover,
  MarkupKind,
  TextDocumentPositionParams,
} from "vscode-languageserver/node";
import { TextDocument } from "vscode-languageserver-textdocument";
import {
  parseHeader,
  type NexyImport,
  type NexyProp,
} from "../../shared/nexy.parser";
import { parseNexyConfig, resolveWithAlias } from "../../shared/nexy.config.parser";
import * as fs from "fs";
import { fileURLToPath } from "url";
import * as path from "path";

export class HoverHandler {
  public handle(params: TextDocumentPositionParams, doc: TextDocument): Hover | null {
    const text = doc.getText();
    const offset = doc.offsetAt(params.position);
    const { imports, props } = parseHeader(text);

    let start = offset;
    while (start > 0 && /\w/.test(text[start - 1])) start--;
    let end = offset;
    while (end < text.length && /\w/.test(text[end])) end++;
    const word = text.slice(start, end);

    const imp = imports.find(i => i.name === word);
    if (imp) {
      return this.getComponentHover(doc, imp);
    }

    const prop = props.find(p => p.name === word);
    if (prop) {
      return {
        contents: {
          kind: MarkupKind.Markdown,
          value: `**${prop.name}** : \`prop[${prop.type}]\`${prop.defaultValue ? `\n\nDefault: \`${prop.defaultValue}\`` : ""}`
        }
      };
    }

    return null;
  }

  private getComponentHover(doc: TextDocument, imp: NexyImport): Hover {
    const colors: Record<string, string> = { vue: "🟢", nexy: "🟩", react: "🔵", svelte: "🟠" };
    
    // Résolution du chemin avec alias
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

    let value = `**${imp.name}** ${colors[imp.framework] || ""} \`${imp.framework}\`\n\nImported from \`${imp.path}\`${aliasResolved ? `\n(resolved to: \`${aliasResolved}\`)` : ""}`;

    if (imp.framework === "nexy") {
      try {
        if (fs.existsSync(finalPath)) {
          const source = fs.readFileSync(finalPath, "utf8");
          const componentProps = parseHeader(source).props;
          if (componentProps.length > 0) {
            const propsLines = componentProps.map(p => `- \`${p.name}\`: \`prop[${p.type}]\`${p.defaultValue ? ` (default: \`${p.defaultValue}\`)` : ""}`);
            value += `\n\n**Props**:\n${propsLines.join("\n")}`;
          }
        }
      } catch {}
    }

    return { contents: { kind: MarkupKind.Markdown, value } };
  }
}
