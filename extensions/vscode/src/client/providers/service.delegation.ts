import * as vscode from "vscode";
import { 
  EmbedContentProvider, 
  getRegionAtPosition, 
  getDocumentRegions,
  PY_SCHEME, 
  HTML_SCHEME, 
  CSS_SCHEME, 
  JS_SCHEME 
} from "./embedded.provider";

export function registerServiceDelegation(
  context: vscode.ExtensionContext,
  providers: Record<string, EmbedContentProvider>,
  isNexyProject: boolean
) {
  const selector = [{ language: "nexy", scheme: "file" }];
  if (isNexyProject) {
    selector.push({ language: "mdx", scheme: "file" });
  }

  const toRel = (document: vscode.TextDocument, baseStart: number, pos: vscode.Position) => {
    const text = document.getText().slice(baseStart, document.offsetAt(pos));
    const lines = text.split(/\r?\n/);
    return new vscode.Position(lines.length - 1, lines[lines.length - 1].length);
  };

  const triggers = ['.', '"', "'", ' ', '<', '/', ':', '{', '%', '|', '='];

  context.subscriptions.push(
    // 1. Completion
    vscode.languages.registerCompletionItemProvider(
      selector,
      {
        async provideCompletionItems(document, position, token, contextParam) {
          // Double vérification pour .mdx
          if (document.languageId === "mdx" && !isNexyProject) return null;

          const region = getRegionAtPosition(document, position);
          if (!region) return null;

          const provider = providers[region.scheme];
          if (!provider) return null;

          const uri = vscode.Uri.parse(`${region.scheme}://${document.uri.path}.${region.languageId}`);
          provider.set(uri, region.content);

          const relPos = toRel(document, region.start, position);
          
          // Force activation des extensions cibles si nécessaire
          if (region.languageId === "python") {
             await vscode.extensions.getExtension("ms-python.python")?.activate();
          } else if (region.languageId === "css") {
             await vscode.extensions.getExtension("vscode.css-language-features")?.activate();
          } else if (region.languageId === "javascript") {
             await vscode.extensions.getExtension("vscode.typescript-language-features")?.activate();
          }

          const list = (await vscode.commands.executeCommand(
            "vscode.executeCompletionItemProvider",
            uri,
            relPos,
            contextParam.triggerCharacter
          )) as vscode.CompletionList | vscode.CompletionItem[];

          if (!list) return null;
          const items = Array.isArray(list) ? list : list.items;
          
          return items.map(sanitizeCompletionItem);
        }
      },
      ...triggers
    ),

    // 2. Hover
    vscode.languages.registerHoverProvider(
      selector,
      {
        async provideHover(document, position) {
          if (document.languageId === "mdx" && !isNexyProject) return null;

          const region = getRegionAtPosition(document, position);
          if (!region) return null;

          const provider = providers[region.scheme];
          if (!provider) return null;

          const uri = vscode.Uri.parse(`${region.scheme}://${document.uri.path}.${region.languageId}`);
          provider.set(uri, region.content);

          const relPos = toRel(document, region.start, position);
          const hover = (await vscode.commands.executeCommand(
            "vscode.executeHoverProvider",
            uri,
            relPos
          )) as vscode.Hover[];

          if (!hover || hover.length === 0) return null;
          return hover[0];
        }
      }
    ),

    // 3. Definition
    vscode.languages.registerDefinitionProvider(
      selector,
      {
        async provideDefinition(document, position) {
          if (document.languageId === "mdx" && !isNexyProject) return null;

          const region = getRegionAtPosition(document, position);
          if (!region) return null;

          const provider = providers[region.scheme];
          if (!provider) return null;

          const uri = vscode.Uri.parse(`${region.scheme}://${document.uri.path}.${region.languageId}`);
          provider.set(uri, region.content);

          const relPos = toRel(document, region.start, position);
          const definitions = (await vscode.commands.executeCommand(
            "vscode.executeDefinitionProvider",
            uri,
            relPos
          )) as vscode.Location | vscode.Location[];

          if (!definitions) return null;
          
          const mapLocation = (loc: vscode.Location) => {
            if (loc.uri.toString() === uri.toString()) {
              const start = document.positionAt(region.start + (loc.range.start.line > 0 ? region.content.split("\n").slice(0, loc.range.start.line).join("\n").length + 1 : 0) + loc.range.start.character);
              const end = document.positionAt(region.start + (loc.range.end.line > 0 ? region.content.split("\n").slice(0, loc.range.end.line).join("\n").length + 1 : 0) + loc.range.end.character);
              return new vscode.Location(document.uri, new vscode.Range(start, end));
            }
            return loc;
          };

          return Array.isArray(definitions) ? definitions.map(mapLocation) : mapLocation(definitions);
        }
      }
    )
  );

  // 4. Diagnostics Delegation
  const diagnosticCollection = vscode.languages.createDiagnosticCollection("nexy-embedded");
  context.subscriptions.push(diagnosticCollection);

  context.subscriptions.push(
    vscode.languages.onDidChangeDiagnostics(e => {
      e.uris.forEach(uri => {
        if (providers[uri.scheme]) {
          const originalUriStr = uri.path.split(".").slice(0, -1).join(".");
          const originalUri = vscode.Uri.file(originalUriStr);
          const document = vscode.workspace.textDocuments.find(d => d.uri.fsPath === originalUri.fsPath);
          
          if (document) {
            // Vérification stricte Nexy
            const isNexyFile = document.languageId === "nexy";
            const isMdxFile = document.languageId === "mdx";
            if (!isNexyFile && !(isMdxFile && isNexyProject)) return;

            const regions = getDocumentRegions(document);
            const region = regions.find(r => uri.scheme === r.scheme);
            
            if (region) {
              const diagnostics = vscode.languages.getDiagnostics(uri);
              const mappedDiagnostics = diagnostics.map(d => {
                const start = document.positionAt(region.start + (d.range.start.line > 0 ? region.content.split("\n").slice(0, d.range.start.line).join("\n").length + 1 : 0) + d.range.start.character);
                const end = document.positionAt(region.start + (d.range.end.line > 0 ? region.content.split("\n").slice(0, d.range.end.line).join("\n").length + 1 : 0) + d.range.end.character);
                const newDiagnostic = new vscode.Diagnostic(new vscode.Range(start, end), d.message, d.severity);
                newDiagnostic.source = `nexy (${region.languageId})`;
                newDiagnostic.code = d.code;
                newDiagnostic.relatedInformation = d.relatedInformation;
                newDiagnostic.tags = d.tags;
                return newDiagnostic;
              });
              diagnosticCollection.set(originalUri, mappedDiagnostics);
            }
          }
        }
      });
    })
  );
}

function sanitizeCompletionItem(item: vscode.CompletionItem): vscode.CompletionItem {
  const out = new vscode.CompletionItem(item.label, item.kind);
  out.detail = item.detail;
  out.documentation = item.documentation;
  out.sortText = item.sortText;
  out.filterText = item.filterText;
  out.insertText = item.insertText ?? (typeof (item as any).textEdit?.newText === "string"
    ? (item as any).textEdit.newText
    : undefined);
  out.additionalTextEdits = undefined;
  (out as any).textEdit = undefined;
  out.command = item.command;
  return out;
}
