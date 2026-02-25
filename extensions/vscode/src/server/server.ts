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
} from "vscode-languageserver/node";
import { TextDocument } from "vscode-languageserver-textdocument";
import {
  getLanguageService,
  CompletionList,
} from "vscode-html-languageservice";

const connection = createConnection(ProposedFeatures.all);
const documents = new TextDocuments(TextDocument);
const htmlLanguageService = getLanguageService();

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

// ─── Parse le header ──────────────────────────────────────────────────────────
interface NexyImport {
  path: string;
  name: string;
  framework: string;
}

interface NexyProp {
  name: string;
  type: string;
  defaultValue?: string;
}

function detectFramework(importPath: string): string {
  if (importPath.endsWith(".vue"))    return "vue";
  if (importPath.endsWith(".nexy"))   return "nexy";
  if (importPath.endsWith(".jsx") || importPath.endsWith(".tsx")) return "react";
  if (importPath.endsWith(".svelte")) return "svelte";
  return "unknown";
}

function parseHeader(text: string): { imports: NexyImport[]; props: NexyProp[] } {
  const imports: NexyImport[] = [];
  const props: NexyProp[] = [];

  const headerMatch = text.match(/^---\s*\n([\s\S]*?)\n---/m);
  if (!headerMatch) return { imports, props };

  const header = headerMatch[1];

  // Imports
  const importRegex =
    /^from\s+["']([^"']+)["']\s+import\s+([A-Za-z_][A-Za-z0-9_]*(?:\s*,\s*[A-Za-z_][A-Za-z0-9_]*)*)/gm;
  let m: RegExpExecArray | null;
  while ((m = importRegex.exec(header)) !== null) {
    const fw = detectFramework(m[1]);
    m[2].split(",").map((n) => n.trim()).forEach((name) => {
      imports.push({ path: m?.[1] || "", name, framework: fw });
    });
  }

  // Props
  const propRegex =
    /^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*prop\[([^\]]*)\](?:\s*=\s*(.+))?/gm;
  while ((m = propRegex.exec(header)) !== null) {
    props.push({ name: m[1], type: m[2].trim(), defaultValue: m[3]?.trim() });
  }

  return { imports, props };
}

function getSection(text: string, offset: number): "header" | "template" {
  const headerMatch = text.match(/^---\s*\n([\s\S]*?)\n---/m);
  if (!headerMatch || headerMatch.index === undefined) return "template";
  const end = headerMatch.index + headerMatch[0].length;
  return offset <= end ? "header" : "template";
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

  // Attributs HTML → après un espace dans une balise
  const tagMatch = lineText.match(/<([a-z][a-zA-Z0-9]*)\s/);
  if (tagMatch) {
    const tag = tagMatch[1];
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

  return [];
});

// ─── Hover ────────────────────────────────────────────────────────────────────
connection.onHover((params: TextDocumentPositionParams): Hover | null => {
  const doc = documents.get(params.textDocument.uri);
  if (!doc) return null;

  const text = doc.getText();
  const offset = doc.offsetAt(params.position);
  const { imports, props } = parseHeader(text);

  // Mot sous le curseur
  const wordMatch = text.slice(Math.max(0, offset - 50), offset + 50)
    .match(/[A-Za-z_][A-Za-z0-9_]*/g);
  if (!wordMatch) return null;

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
      vue: "🟢", nexy: "🟩", react: "🔵", svelte: "🟠",
    };
    return {
      contents: {
        kind: MarkupKind.Markdown,
        value: `**${imp.name}** ${colors[imp.framework] ?? ""} \`${imp.framework}\`\n\nImporté depuis \`${imp.path}\``,
      },
    };
  }

  // Prop
  const prop = props.find((p) => p.name === word);
  if (prop) {
    return {
      contents: {
        kind: MarkupKind.Markdown,
        value: `**${prop.name}** : \`prop[${prop.type}]\`${prop.defaultValue ? `\n\nDéfaut : \`${prop.defaultValue}\`` : ""}`,
      },
    };
  }

  return null;
});

// ─── Diagnostics ─────────────────────────────────────────────────────────────
documents.onDidChangeContent((change) => {
  const doc = change.document;
  const text = doc.getText();
  const diagnostics: Diagnostic[] = [];
  const { imports } = parseHeader(text);

  // Cherche les composants utilisés dans le template mais non importés
  const templateMatch = text.match(/^---[\s\S]*?---\n([\s\S]*)$/m);
  if (templateMatch) {
    const template = templateMatch[1];
    const usedComponents = [...template.matchAll(/<([A-Z][A-Za-z0-9]*)/g)]
      .map((m) => m[1]);

    usedComponents.forEach((name) => {
      if (!imports.find((i) => i.name === name)) {
        // Trouve la position dans le document complet
        const idx = text.indexOf(`<${name}`);
        if (idx !== -1) {
          const start = doc.positionAt(idx + 1);
          const end = doc.positionAt(idx + 1 + name.length);
          diagnostics.push({
            severity: DiagnosticSeverity.Warning,
            range: Range.create(start, end),
            message: `Composant "${name}" utilisé mais non importé dans le header`,
            source: "nexy",
          });
        }
      }
    });
  }

  connection.sendDiagnostics({ uri: doc.uri, diagnostics });
});

documents.listen(connection);
connection.listen();
