import * as vscode from "vscode";
import { getSection } from "./shared/nexyParser";

const tokenTypes = new Map<string, number>();
const tokenTypesLegend = [
  "keyword",
  "variable",
  "type",
  "operator",
  "class",
  "property",
  "string",
];
tokenTypesLegend.forEach((t, i) => tokenTypes.set(t, i));

const legend = new vscode.SemanticTokensLegend(tokenTypesLegend, []);

class NexySemanticTokensProvider implements vscode.DocumentSemanticTokensProvider {
  async provideDocumentSemanticTokens(
    document: vscode.TextDocument,
  ): Promise<vscode.SemanticTokens> {
    const builder = new vscode.SemanticTokensBuilder(legend);
    const text = document.getText();

    const lines = text.split(/\r?\n/);

    let inHeader = false;
    let headerStartOffset = 0;
    let offset = 0;

    for (let lineIndex = 0; lineIndex < lines.length; lineIndex++) {
      const line = lines[lineIndex];

      if (/^---\s*$/.test(line)) {
        inHeader = !inHeader || offset === 0;
        headerStartOffset = offset + line.length + 1;
        offset += line.length + 1;
        continue;
      }

      if (inHeader) {
        NexySemanticTokensProvider.tokensPythonLine(builder, lineIndex, line);
      } else {
        NexySemanticTokensProvider.tokensTemplateLine(builder, lineIndex, line);
      }

      offset += line.length + 1;
    }

    return builder.build();
  }

  static push(
    builder: vscode.SemanticTokensBuilder,
    line: number,
    startChar: number,
    length: number,
    tokenType: string,
  ) {
    const idx = tokenTypes.get(tokenType);
    if (idx === undefined) return;
    builder.push(line, startChar, length, idx, 0);
  }

  static tokensPythonLine(
    builder: vscode.SemanticTokensBuilder,
    lineIndex: number,
    line: string,
  ) {
    const kwRegex = /\b(import|from|as|with|def|class|return|True|False|None)\b/g;
    let m: RegExpExecArray | null;
    while ((m = kwRegex.exec(line))) {
      this.push(builder, lineIndex, m.index, m[0].length, "keyword");
    }

    const assign = /^\s*([A-Za-z_]\w*)\s*(?::[^=]+)?\s*=/;
    const am = assign.exec(line);
    if (am) {
      this.push(builder, lineIndex, am.index + am[0].indexOf(am[1]), am[1].length, "variable");
      const eqPos = line.indexOf("=", am.index);
      if (eqPos !== -1) this.push(builder, lineIndex, eqPos, 1, "operator");
    }

    const propDecl = /^\s*([A-Za-z_]\w*)\s*:\s*prop\[/;
    const pm = propDecl.exec(line);
    if (pm) {
      this.push(builder, lineIndex, pm.index + pm[0].indexOf(pm[1]), pm[1].length, "variable");
      const propIdx = line.indexOf("prop", pm.index);
      if (propIdx !== -1) this.push(builder, lineIndex, propIdx, 4, "type");
      const lb = line.indexOf("[", propIdx);
      const rb = line.indexOf("]", lb + 1);
      if (lb !== -1 && rb !== -1 && rb > lb + 1) {
        this.push(builder, lineIndex, lb + 1, rb - lb - 1, "type");
      }
    }

    const importList = /^\s*import\s+(.+)/.exec(line);
    if (importList && importList[1]) {
      let rest = importList[1];
      let idx = line.indexOf(rest);
      const parts = rest.split(/\s*,\s*/);
      for (const p of parts) {
        if (!p) continue;
        const pos = line.indexOf(p, idx);
        if (pos !== -1) {
          this.push(builder, lineIndex, pos, p.length, "class");
          idx = pos + p.length;
        }
      }
    }

    const fromImport = /^\s*from\s+(.+?)\s+import\s+(.+)/.exec(line);
    if (fromImport) {
      const mod = fromImport[1];
      const modPos = line.indexOf(mod);
      if (modPos !== -1) this.push(builder, lineIndex, modPos, mod.length, "class");
      const syms = fromImport[2].split(/\s*,\s*/);
      let idx = line.indexOf(fromImport[2]);
      for (const s of syms) {
        if (!s) continue;
        const pos = line.indexOf(s, idx);
        if (pos !== -1) {
          this.push(builder, lineIndex, pos, s.length, "property");
          idx = pos + s.length;
        }
      }
    }
  }

  static tokensTemplateLine(
    builder: vscode.SemanticTokensBuilder,
    lineIndex: number,
    line: string,
  ) {
    let m: RegExpExecArray | null;
    const compOpen = /<([A-Z][A-Za-z0-9]*)/g;
    while ((m = compOpen.exec(line))) {
      this.push(builder, lineIndex, m.index + 1, m[1].length, "class");
    }

    const attr = /\s([:@\w][\w:.-]*)(?=\s*=|\s|\/?>)/g;
    while ((m = attr.exec(line))) {
      this.push(builder, lineIndex, m.index + 1, m[1].length, "property");
    }

    const eq = /=/g;
    while ((m = eq.exec(line))) {
      this.push(builder, lineIndex, m.index, 1, "operator");
    }

    const str = /"[^"]*"|'[^']*'/g;
    while ((m = str.exec(line))) {
      this.push(builder, lineIndex, m.index, m[0].length, "string");
    }
  }
}

export function registerSemanticTokens(context: vscode.ExtensionContext) {
  const selector = { language: "nexy", scheme: "file" };
  context.subscriptions.push(
    vscode.languages.registerDocumentSemanticTokensProvider(
      selector,
      new NexySemanticTokensProvider(),
      legend,
    ),
  );
}
