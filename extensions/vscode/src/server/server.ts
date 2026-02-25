import {
  createConnection,
  TextDocuments,
  ProposedFeatures,
  InitializeParams,
  CompletionItem,
  CompletionItemKind,
  TextDocumentPositionParams,
  TextDocumentSyncKind,
  InitializeResult,
  InsertTextFormat,
  Hover,
  MarkupKind,
  Diagnostic,
  DiagnosticSeverity,
  Range,
  CodeAction,
  CodeActionKind,
  CodeActionParams,
} from "vscode-languageserver/node";
import * as fs from "fs";
import * as path from "path";
import { fileURLToPath } from "url";
import { TextDocument } from "vscode-languageserver-textdocument";
import {
  detectFramework,
  parseHeader,
  getSection,
  type NexyImport,
  type NexyProp,
  findUsedComponentsInTemplate,
  getTemplate,
} from "../shared/nexyParser";

const connection = createConnection(ProposedFeatures.all);
const documents = new TextDocuments(TextDocument);

// ─── HTML tags courants ───────────────────────────────────────────────────────
const HTML_TAGS = [
  "div","span","p","a","h1","h2","h3","h4","h5","h6",
  "ul","ol","li","table","tr","td","th","thead","tbody",
  "form","input","button","select","option","textarea",
  "img","video","audio","source","canvas","svg",
  "header","footer","main","nav","section","article","aside",
  "script","style","link","meta","title","head","body",
];

const HTML_ATTRIBUTES: Record<string, string[]> = {
  "*":      ["class","id","style","title","tabindex","hidden","data-*","aria-*","role"],
  "a":      ["href","target","rel","download"],
  "img":    ["src","alt","width","height","loading"],
  "input":  ["type","name","value","placeholder","required","disabled","readonly","checked","min","max","step"],
  "button": ["type","disabled","form"],
  "form":   ["action","method","enctype","novalidate"],
  "video":  ["src","autoplay","controls","loop","muted","poster"],
  "audio":  ["src","autoplay","controls","loop","muted"],
  "link":   ["rel","href","type"],
  "script": ["src","type","defer","async"],
  "meta":   ["name","content","charset","http-equiv"],
};

// ─── Jinja keywords ───────────────────────────────────────────────────────────
const JINJA_KEYWORDS = [
  "if","elif","else","endif",
  "for","endfor","in",
  "block","endblock",
  "extends","include",
  "macro","endmacro",
  "set","with","endwith",
  "raw","endraw",
  "import","from","as",
  "not","and","or","is",
  "true","false","none",
];

const JINJA_FILTERS = [
  "abs","attr","batch","capitalize","center","count","default",
  "dictsort","escape","filesizeformat","first","float","forceescape",
  "format","groupby","indent","int","items","join","last","length",
  "list","lower","map","max","min","pprint","random","reject",
  "rejectattr","replace","reverse","round","safe","select","selectattr",
  "slice","sort","string","striptags","sum","title","tojson","trim",
  "truncate","unique","upper","urlencode","urlize","wordcount","wordwrap",
];

function resolveImportPath(docUri: string, imp: NexyImport): string | null {
  if (!imp.path || !docUri.startsWith("file:")) {
    return null;
  }

  let currentFsPath: string;
  try {
    currentFsPath = fileURLToPath(docUri);
  } catch {
    return null;
  }

  const baseDir = path.dirname(currentFsPath);
  return path.resolve(baseDir, imp.path);
}

function getComponentPropsFromImport(
  doc: TextDocument,
  imp: NexyImport,
): NexyProp[] {
  if (imp.framework !== "nexy") {
    return [];
  }

  const resolvedPath = resolveImportPath(doc.uri, imp);
  if (!resolvedPath) {
    return [];
  }

  let source: string;
  try {
    source = fs.readFileSync(resolvedPath, "utf8");
  } catch {
    return [];
  }

  const { props } = parseHeader(source);
  return props;
}

// ─── Initialize ───────────────────────────────────────────────────────────────
connection.onInitialize((_params: InitializeParams): InitializeResult => {
  return {
    capabilities: {
      textDocumentSync: TextDocumentSyncKind.Incremental,
      completionProvider: {
        resolveProvider: false,
        triggerCharacters: ["<", "/", ".", ":", "{", "%", "#", "|", " ", "\"", "'"],
      },
      hoverProvider: true,
    },
  };
});

// ─── Completion ───────────────────────────────────────────────────────────────
connection.onCompletion((params: TextDocumentPositionParams): CompletionItem[] => {
  const doc = documents.get(params.textDocument.uri);
  if (!doc) return [];

  const text = doc.getText();
  const offset = doc.offsetAt(params.position);
  const section = getSection(text, offset);
  const { imports, props } = parseHeader(text);

  // ── Section HEADER ──────────────────────────────────────────────────────────
  if (section === "header") {
    const lineStart = text.lastIndexOf("\n", offset - 1) + 1;
    const lineText = text.slice(lineStart, offset);

    // après "from "
    if (/^from\s+["'][^"']*$/.test(lineText)) {
      return []; // on pourrait suggérer des fichiers mais nécessite fs
    }

    // après "import "
    if (/^from\s+["'][^"']*["']\s+import\s+\w*$/.test(lineText)) {
      return [];
    }

    // suggestions prop
    if (/^\w+\s*:\s*prop\[/.test(lineText)) {
      return [
        "str","int","float","bool","list","dict","callable",
        "str | None","int | None","bool | None",
      ].map((t) => ({
        label: t,
        kind: CompletionItemKind.TypeParameter,
        detail: "Type Nexy",
      }));
    }

    // début de ligne → suggère prop / from
    return [
      {
        label: "prop",
        kind: CompletionItemKind.Keyword,
        insertText: "${1:name} : prop[${2:str}] = ${3:\"default\"}",
        insertTextFormat: InsertTextFormat.Snippet,
        detail: "Déclarer une prop Nexy",
      },
      {
        label: "from",
        kind: CompletionItemKind.Keyword,
        insertText: "from \"${1:./components/Component.tsx}\" import ${2:Component}",
        insertTextFormat: InsertTextFormat.Snippet,
        detail: "Importer un composant",
      },
    ];
  }

  // ── Section TEMPLATE ────────────────────────────────────────────────────────
  const lineStart = text.lastIndexOf("\n", offset - 1) + 1;
  const lineText = text.slice(lineStart, offset);
  const charBefore = text[offset - 1];

  // Dans {{ }} → Python + Jinja filters
  const inJinjaExpr = (text.lastIndexOf("{{", offset) > text.lastIndexOf("}}", offset));
  if (inJinjaExpr) {
    const items: CompletionItem[] = [];

    // Variables/props disponibles
    props.forEach((p) => {
      items.push({
        label: p.name,
        kind: CompletionItemKind.Variable,
        detail: `prop[${p.type}]`,
        documentation: p.defaultValue ? `Valeur par défaut : ${p.defaultValue}` : undefined,
      });
    });

    // Après | → filtres Jinja
    if (/\|\s*\w*$/.test(lineText)) {
      JINJA_FILTERS.forEach((f) => {
        items.push({ label: f, kind: CompletionItemKind.Function, detail: "Filtre Jinja2" });
      });
    }

    return items;
  }

  // Dans {% %} → keywords Jinja
  const inJinjaBlock = (text.lastIndexOf("{%", offset) > text.lastIndexOf("%}", offset));
  if (inJinjaBlock) {
    return JINJA_KEYWORDS.map((k) => ({
      label: k,
      kind: CompletionItemKind.Keyword,
      detail: "Jinja2 keyword",
    }));
  }

  // Balise ouvrante <
  if (charBefore === "<" || /^<\w*$/.test(lineText.trimStart())) {
    const items: CompletionItem[] = [];

    // Composants importés
    imports.forEach((imp) => {
      items.push({
        label: imp.name,
        kind: CompletionItemKind.Class,
        detail: `Composant ${imp.framework} — ${imp.path}`,
        insertText: `${imp.name} $1/>`,
        insertTextFormat: InsertTextFormat.Snippet,
      });
    });

    // Tags HTML
    HTML_TAGS.forEach((tag) => {
      items.push({
        label: tag,
        kind: CompletionItemKind.Property,
        detail: "HTML",
        insertText: `${tag}>$1</${tag}>`,
        insertTextFormat: InsertTextFormat.Snippet,
      });
    });

    return items;
  }

  // Attributs HTML ou props de composant → après un espace dans une balise
  const htmlTagMatch = lineText.match(/<([a-z][a-zA-Z0-9]*)\s/);
  if (htmlTagMatch) {
    const tag = htmlTagMatch[1];
    const attrs = [
      ...(HTML_ATTRIBUTES["*"] ?? []),
      ...(HTML_ATTRIBUTES[tag] ?? []),
    ];
    return attrs.map((a) => ({
      label: a,
      kind: CompletionItemKind.Property,
      detail: `Attribut HTML <${tag}>`,
      insertText: a.endsWith("*") ? `${a.slice(0, -1)}$1="$2"` : `${a}="$1"`,
      insertTextFormat: InsertTextFormat.Snippet,
    }));
  }

  const componentTagMatch = lineText.match(/<([A-Z][A-Za-z0-9]*)\s/);
  if (componentTagMatch) {
    const tag = componentTagMatch[1];
    const imp = imports.find((i) => i.name === tag);

    if (imp) {
      const componentProps = getComponentPropsFromImport(doc, imp);
      if (componentProps.length > 0) {
        return componentProps.map((p) => ({
          label: p.name,
          kind: CompletionItemKind.Property,
          detail: `Prop ${p.name}: prop[${p.type}]`,
          insertText: `${p.name}="$1"`,
          insertTextFormat: InsertTextFormat.Snippet,
          documentation: p.defaultValue
            ? `Valeur par défaut : ${p.defaultValue}`
            : undefined,
        }));
      }
    }

    // Fallback: attributs HTML génériques sur un composant (class, id, data-*, aria-*)
    const genericAttrs = HTML_ATTRIBUTES["*"] ?? [];
    return genericAttrs.map((a) => ({
      label: a,
      kind: CompletionItemKind.Property,
      detail: `Attribut HTML générique pour <${tag}>`,
      insertText: a.endsWith("*") ? `${a.slice(0, -1)}$1="$2"` : `${a}="$1"`,
      insertTextFormat: InsertTextFormat.Snippet,
    }));
  }

  return [];
});

// ─── Hover ────────────────────────────────────────────────────────────────────
connection.onHover(
  async (params: TextDocumentPositionParams): Promise<Hover | null> => {
    const doc = documents.get(params.textDocument.uri);
    if (!doc) {
      return null;
    }

    const text = doc.getText();
    const offset = doc.offsetAt(params.position);
    const { imports, props } = parseHeader(text);

    // Mot sous le curseur
    const wordMatch = text
      .slice(Math.max(0, offset - 50), offset + 50)
      .match(/[A-Za-z_][A-Za-z0-9_]*/g);
    if (!wordMatch) {
      return null;
    }

    // Cherche le mot exact à la position
    let start = offset;
    while (start > 0 && /\w/.test(text[start - 1])) start--;
    let end = offset;
    while (end < text.length && /\w/.test(text[end])) end++;
    const word = text.slice(start, end);

    // Composant importé
    const imp = imports.find((i) => i.name === word);
    if (imp) {
      const colors: Record<string, string> = {
        vue: "🟢",
        nexy: "🟩",
        react: "🔵",
        svelte: "🟠",
      };

      let value = `**${imp.name}** ${
        colors[imp.framework] ?? ""
      } \`${imp.framework}\`\n\nImporté depuis \`${imp.path}\``;

      if (imp.framework === "nexy") {
        const componentProps = getComponentPropsFromImport(doc, imp);
        if (componentProps.length > 0) {
          const propsLines = componentProps.map((p) => {
            const def =
              p.defaultValue !== undefined
                ? ` (défaut: \`${p.defaultValue}\`)`
                : "";
            return `- \`${p.name}\`: \`prop[${p.type}]\`${def}`;
          });
          value += `\n\n**Props**:\n${propsLines.join("\n")}`;
        }
      }

      return {
        contents: {
          kind: MarkupKind.Markdown,
          value,
        },
      };
    }

    // Prop locale
    const prop = props.find((p) => p.name === word);
    if (prop) {
      return {
        contents: {
          kind: MarkupKind.Markdown,
          value: `**${prop.name}** : \`prop[${prop.type}]\`${
            prop.defaultValue ? `\n\nDéfaut : \`${prop.defaultValue}\`` : ""
          }`,
        },
      };
    }

    return null;
  },
);

// ─── Diagnostics ─────────────────────────────────────────────────────────────
documents.onDidChangeContent((change) => {
  const doc = change.document;
  const text = doc.getText();
  const diagnostics: Diagnostic[] = [];
  const { imports, props } = parseHeader(text);

  const usedComponents = findUsedComponentsInTemplate(text);
  const template = getTemplate(text);

  // Composants utilisés mais non importés
  usedComponents.forEach((name) => {
    if (!imports.find((i) => i.name === name)) {
      const idx = text.indexOf(`<${name}`);
      if (idx !== -1) {
        const start = doc.positionAt(idx + 1);
        const end = doc.positionAt(idx + 1 + name.length);
        diagnostics.push({
          severity: DiagnosticSeverity.Warning,
          range: Range.create(start, end),
          message: `Composant "${name}" utilisé mais non importé dans le header`,
          source: "nexy",
          code: "nexy.missingImport",
        });
      }
    }
  });

  // Imports inutilisés
  imports.forEach((imp) => {
    if (!usedComponents.includes(imp.name)) {
      const idx = text.indexOf(imp.name);
      if (idx !== -1) {
        const start = doc.positionAt(idx);
        const end = doc.positionAt(idx + imp.name.length);
        diagnostics.push({
          severity: DiagnosticSeverity.Hint,
          range: Range.create(start, end),
          message: `Import "${imp.name}" non utilisé dans le template`,
          source: "nexy",
          code: "nexy.unusedImport",
        });
      }
    }
  });

  // Props déclarées mais jamais utilisées
  props.forEach((prop) => {
    const usageRegex = new RegExp(`\\b${prop.name}\\b`);
    if (!usageRegex.test(template)) {
      const idx = text.indexOf(prop.name);
      if (idx !== -1) {
        const start = doc.positionAt(idx);
        const end = doc.positionAt(idx + prop.name.length);
        diagnostics.push({
          severity: DiagnosticSeverity.Hint,
          range: Range.create(start, end),
          message: `Prop "${prop.name}" déclarée mais jamais utilisée dans le template`,
          source: "nexy",
          code: "nexy.unusedProp",
        });
      }
    }
  });

  connection.sendDiagnostics({ uri: doc.uri, diagnostics });
});

connection.onCodeAction((params: CodeActionParams): CodeAction[] => {
  const doc = documents.get(params.textDocument.uri);
  if (!doc) {
    return [];
  }

  const text = doc.getText();
  const actions: CodeAction[] = [];

  for (const diagnostic of params.context.diagnostics) {
    if (diagnostic.source !== "nexy" || !diagnostic.code) {
      continue;
    }

    if (diagnostic.code === "nexy.missingImport") {
      const startOffset = doc.offsetAt(diagnostic.range.start);
      const endOffset = doc.offsetAt(diagnostic.range.end);
      const componentName = text.slice(startOffset, endOffset);

      const headerMatch = text.match(/^---\s*$/m);
      if (!headerMatch || headerMatch.index === undefined) {
        continue;
      }

      const headerLineEndOffset = text.indexOf("\n", headerMatch.index);
      const insertOffset =
        headerLineEndOffset === -1 ? text.length : headerLineEndOffset + 1;
      const insertPosition = doc.positionAt(insertOffset);

      const importLine = `from "./components/${componentName}.nexy" import ${componentName}\n`;

      actions.push({
        title: `Ajouter l'import pour "${componentName}"`,
        kind: CodeActionKind.QuickFix,
        diagnostics: [diagnostic],
        edit: {
          changes: {
            [params.textDocument.uri]: [
              {
                range: {
                  start: insertPosition,
                  end: insertPosition,
                },
                newText: importLine,
              },
            ],
          },
        },
      });
    } else if (
      diagnostic.code === "nexy.unusedImport" ||
      diagnostic.code === "nexy.unusedProp"
    ) {
      const startOffset = doc.offsetAt(diagnostic.range.start);
      const endOffset = doc.offsetAt(diagnostic.range.end);

      const lineStartIdx = text.lastIndexOf("\n", startOffset - 1);
      const deleteStartOffset = lineStartIdx === -1 ? 0 : lineStartIdx + 1;

      let lineEndIdx = text.indexOf("\n", endOffset);
      if (lineEndIdx === -1) {
        lineEndIdx = text.length;
      } else {
        lineEndIdx += 1;
      }

      const deleteStart = doc.positionAt(deleteStartOffset);
      const deleteEnd = doc.positionAt(lineEndIdx);

      const titlePrefix =
        diagnostic.code === "nexy.unusedImport"
          ? "Supprimer l'import inutilisé"
          : "Supprimer la prop inutilisée";

      actions.push({
        title: titlePrefix,
        kind: CodeActionKind.QuickFix,
        diagnostics: [diagnostic],
        edit: {
          changes: {
            [params.textDocument.uri]: [
              {
                range: {
                  start: deleteStart,
                  end: deleteEnd,
                },
                newText: "",
              },
            ],
          },
        },
      });
    }
  }

  return actions;
});

documents.listen(connection);
connection.listen();
