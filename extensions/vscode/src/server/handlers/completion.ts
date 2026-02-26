import {
  CompletionItem,
  CompletionItemKind,
  TextDocumentPositionParams,
  InsertTextFormat,
} from "vscode-languageserver/node";
import { TextDocument } from "vscode-languageserver-textdocument";
import {
  parseHeader,
  getSection,
  getTemplate,
  type NexyImport,
  type NexyProp,
} from "../../shared/nexy.parser";
import { parseNexyConfig, resolveWithAlias } from "../../shared/config.parser";
import * as fs from "fs";
import { fileURLToPath } from "url";
import * as path from "path";

const HTML_TAGS = ["div","span","p","a","h1","h2","h3","h4","h5","h6","ul","ol","li","table","tr","td","th","thead","tbody","form","input","button","select","option","textarea","img","video","audio","source","canvas","svg","header","footer","main","nav","section","article","aside","script","style","link","meta","title","head","body"];
const JINJA_KEYWORDS = ["if","elif","else","endif","for","endfor","in","block","endblock","extends","include","macro","endmacro","set","with","endwith","raw","endraw","import","from","as","not","and","or","is","true","false","none"];
const JINJA_FILTERS = ["abs","attr","batch","capitalize","center","count","default","dictsort","escape","filesizeformat","first","float","forceescape","format","groupby","indent","int","items","join","last","length","list","lower","map","max","min","pprint","random","reject","rejectattr","replace","reverse","round","safe","select","selectattr","slice","sort","string","striptags","sum","title","tojson","trim","truncate","unique","upper","urlencode","urlize","wordcount","wordwrap"];

const HTML_ATTRIBUTES: Record<string, string[]> = {
  "*": ["class","id","style","title","tabindex","hidden","data-*","aria-*","role"],
  "a": ["href","target","rel","download"],
  "img": ["src","alt","width","height","loading"],
  "input": ["type","name","value","placeholder","required","disabled","readonly","checked","min","max","step"],
  "button": ["type","disabled","form"],
};

export class CompletionHandler {
  public handle(params: TextDocumentPositionParams, doc: TextDocument): CompletionItem[] {
    const text = doc.getText();
    const offset = doc.offsetAt(params.position);
    const section = getSection(text, offset);
    const { imports, props } = parseHeader(text);

    if (section === "header") {
      return this.handleHeaderCompletion(text, offset, doc);
    }
    return this.handleTemplateCompletion(text, offset, imports, props, doc);
  }

  private handleHeaderCompletion(text: string, offset: number, doc: TextDocument): CompletionItem[] {
    const lineStart = text.lastIndexOf("\n", offset - 1) + 1;
    const lineText = text.slice(lineStart, offset);

    // Auto-completion des chemins dans from "..."
    const fromPathMatch = lineText.match(/from\s+["']([^"']*)$/);
    if (fromPathMatch) {
      return this.getFileCompletions(doc, fromPathMatch[1]);
    }

    if (/^\w+\s*:\s*prop\[/.test(lineText)) {
      return ["str","int","float","bool","list","dict","callable"].map(t => ({
        label: t, kind: CompletionItemKind.TypeParameter, detail: "Nexy Type"
      }));
    }

    return [
      { label: "prop", kind: CompletionItemKind.Keyword, insertText: "${1:name} : prop[${2:str}] = ${3:\"default\"}", insertTextFormat: InsertTextFormat.Snippet, detail: "Declare a prop" },
      { label: "from", kind: CompletionItemKind.Keyword, insertText: "from \"${1:./components/Component.tsx}\" import ${2:Component}", insertTextFormat: InsertTextFormat.Snippet, detail: "Import a component" },
    ];
  }

  private getFileCompletions(doc: TextDocument, partialPath: string): CompletionItem[] {
    try {
      const docPath = fileURLToPath(doc.uri);
      const currentDir = path.dirname(docPath);
      
      // Trouver la racine du projet pour les alias
      let workspaceRoot = currentDir;
      while (workspaceRoot !== path.parse(workspaceRoot).root) {
        if (fs.existsSync(path.join(workspaceRoot, "nexyconfig.py"))) break;
        workspaceRoot = path.dirname(workspaceRoot);
      }

      const config = parseNexyConfig(workspaceRoot);
      let searchDir = currentDir;
      let isAlias = false;

      // Vérifier si le chemin commence par un alias
      for (const [alias, replacement] of Object.entries(config.useAliases)) {
        if (partialPath.startsWith(alias)) {
          isAlias = true;
          const relativePart = partialPath.slice(alias.length);
          const aliasBaseDir = path.resolve(workspaceRoot, replacement);
          
          if (relativePart.includes("/")) {
            const lastSlash = relativePart.lastIndexOf("/");
            searchDir = path.resolve(aliasBaseDir, relativePart.slice(0, lastSlash + 1));
          } else {
            searchDir = aliasBaseDir;
          }
          break;
        }
      }

      if (!isAlias) {
        if (partialPath.includes("/")) {
          const lastSlash = partialPath.lastIndexOf("/");
          searchDir = path.resolve(currentDir, partialPath.slice(0, lastSlash));
        }
      }

      if (!fs.existsSync(searchDir)) return [];

      const entries = fs.readdirSync(searchDir, { withFileTypes: true });
      const items: CompletionItem[] = entries
        .filter(e => e.isDirectory() || /\.(nexy|vue|tsx|jsx|svelte|py)$/.test(e.name))
        .map(e => ({
          label: e.name,
          kind: e.isDirectory() ? CompletionItemKind.Folder : CompletionItemKind.File,
          insertText: e.name + (e.isDirectory() ? "/" : ""),
          command: e.isDirectory() ? { title: "Suggest", command: "editor.action.triggerSuggest" } : undefined
        }));

      // Si on commence juste la frappe, suggérer aussi les alias
      if (partialPath === "" || (!partialPath.includes("/") && !isAlias)) {
        Object.keys(config.useAliases).forEach(alias => {
          items.push({
            label: alias,
            kind: CompletionItemKind.Reference,
            detail: `Nexy Alias: ${config.useAliases[alias]}`,
            insertText: alias + "/",
            command: { title: "Suggest", command: "editor.action.triggerSuggest" }
          });
        });
      }

      return items;
    } catch {
      return [];
    }
  }

  private handleTemplateCompletion(text: string, offset: number, imports: NexyImport[], props: NexyProp[], doc: TextDocument): CompletionItem[] {
    const lineStart = text.lastIndexOf("\n", offset - 1) + 1;
    const lineText = text.slice(lineStart, offset);
    const charBefore = text[offset - 1];

    if (text.lastIndexOf("{{", offset) > text.lastIndexOf("}}", offset)) {
      return this.getJinjaExpressionItems(props, lineText);
    }

    if (charBefore === "<" || /^<\w*$/.test(lineText.trimStart())) {
      return this.getTagItems(imports);
    }

    return this.getAttributeItems(lineText, imports, doc);
  }

  private getJinjaExpressionItems(props: NexyProp[], lineText: string): CompletionItem[] {
    const items: CompletionItem[] = props.map(p => ({
      label: p.name, kind: CompletionItemKind.Variable, detail: `prop[${p.type}]`
    }));
    if (/\|\s*\w*$/.test(lineText)) {
      JINJA_FILTERS.forEach(f => items.push({ label: f, kind: CompletionItemKind.Function, detail: "Jinja2 Filter" }));
    }
    return items;
  }

  private getTagItems(imports: NexyImport[]): CompletionItem[] {
    const items: CompletionItem[] = imports.map(imp => ({
      label: imp.name, kind: CompletionItemKind.Class, detail: `${imp.framework} Component`,
      insertText: `${imp.name} $1/>`, insertTextFormat: InsertTextFormat.Snippet
    }));
    HTML_TAGS.forEach(tag => items.push({
      label: tag, kind: CompletionItemKind.Property, detail: "HTML",
      insertText: `${tag}>$1</${tag}>`, insertTextFormat: InsertTextFormat.Snippet
    }));
    return items;
  }

  private getAttributeItems(lineText: string, imports: NexyImport[], doc: TextDocument): CompletionItem[] {
    // 1. Détecter si c'est un composant (Commence par une MAJUSCULE)
    const componentMatch = lineText.match(/<([A-Z][A-Za-z0-9]*)\s/);
    if (componentMatch) {
      const imp = imports.find(i => i.name === componentMatch[1]);
      if (imp) {
        const componentProps = this.getComponentProps(doc, imp);
        if (componentProps.length > 0) {
          // Pour un composant Nexy/MDX, on ne suggère QUE ses props (pas d'attributs HTML)
          return componentProps.map(p => ({
            label: p.name, kind: CompletionItemKind.Property, detail: `Prop ${p.name}: prop[${p.type}]`,
            insertText: `${p.name}="$1"`, insertTextFormat: InsertTextFormat.Snippet,
            documentation: p.defaultValue ? `Default: ${p.defaultValue}` : undefined
          }));
        }
      }
      // Si c'est un composant mais qu'on n'a pas trouvé d'import/props, on ne suggère rien (KISS)
      return [];
    }

    // 2. Détecter si c'est une balise HTML (Commence par une minuscule)
    const htmlMatch = lineText.match(/<([a-z][a-zA-Z0-9]*)\s/);
    if (htmlMatch) {
      const tag = htmlMatch[1];
      const attrs = [...(HTML_ATTRIBUTES["*"] || []), ...(HTML_ATTRIBUTES[tag] || [])];
      return attrs.map(a => ({
        label: a, kind: CompletionItemKind.Property, detail: `<${tag}> attribute`,
        insertText: a.endsWith("*") ? `${a.slice(0, -1)}$1="$2"` : `${a}="$1"`, insertTextFormat: InsertTextFormat.Snippet
      }));
    }
    return [];
  }

  private getComponentProps(doc: TextDocument, imp: NexyImport): NexyProp[] {
    try {
      const docPath = fileURLToPath(doc.uri);
      const currentDir = path.dirname(docPath);
      const resolvedPath = path.resolve(currentDir, imp.path);
      
      if (!fs.existsSync(resolvedPath)) return [];
      const source = fs.readFileSync(resolvedPath, "utf8");
      
      if (imp.framework === "nexy") {
        return parseHeader(source).props;
      }
      
      // Support basique pour Vue/React/Svelte (Regex simple pour extraire les props)
      if (imp.framework === "vue") {
        const props: NexyProp[] = [];
        const propsRegex = /props:\s*{([\s\S]*?)}/g;
        const m = propsRegex.exec(source);
        if (m) {
          const propNames = m[1].matchAll(/(\w+)\s*:/g);
          for (const pn of propNames) {
            props.push({ name: pn[1], type: "any" });
          }
        }
        return props;
      }
      
      return [];
    } catch { return []; }
  }
}
