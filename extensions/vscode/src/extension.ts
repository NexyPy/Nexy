import * as path from "path";
import * as vscode from "vscode";
import {
  LanguageClient,
  LanguageClientOptions,
  ServerOptions,
  TransportKind,
} from "vscode-languageclient/node";
import {
  FRAMEWORK_COLORS,
  detectFramework,
  parseImports,
  findComponentRanges,
} from "./utils";

let client: LanguageClient;

// ─── Decoration types par framework ──────────────────────────────────────────
const decorationTypes: Record<string, vscode.TextEditorDecorationType> =
  Object.fromEntries(
    Object.entries(FRAMEWORK_COLORS).map(([fw, color]) => [
      fw,
      vscode.window.createTextEditorDecorationType({ color }),
    ])
  );

function updateDecorations(editor: vscode.TextEditor) {
  if (editor.document.languageId !== "nexy") return;

  const imports = parseImports(editor.document.getText());

  Object.values(decorationTypes).forEach((dt) =>
    editor.setDecorations(dt, [])
  );

  const byFramework = new Map<string, vscode.Range[]>();
  imports.forEach((framework, componentName) => {
    const ranges = findComponentRanges(editor.document, componentName);
    if (ranges.length === 0) return;
    if (!byFramework.has(framework)) byFramework.set(framework, []);
    byFramework.get(framework)!.push(...ranges);
  });

  byFramework.forEach((ranges, framework) => {
    const dt = decorationTypes[framework];
    if (dt) editor.setDecorations(dt, ranges);
  });
}

export function activate(context: vscode.ExtensionContext) {
  // ── LSP Server ──────────────────────────────────────────────────────────────
  const serverModule = context.asAbsolutePath(
    path.join("dist", "server.js")
  );

  const serverOptions: ServerOptions = {
    run: { module: serverModule, transport: TransportKind.ipc },
    debug: {
      module: serverModule,
      transport: TransportKind.ipc,
      options: { execArgv: ["--nolazy", "--inspect=6009"] },
    },
  };

  const clientOptions: LanguageClientOptions = {
    documentSelector: [{ scheme: "file", language: "nexy" }],
    synchronize: {
      fileEvents: vscode.workspace.createFileSystemWatcher("**/*.nexy"),
    },
  };

  client = new LanguageClient("nexyLsp", "Nexy LSP", serverOptions, clientOptions);
  client.start();

  // ── Décorations framework ───────────────────────────────────────────────────
  if (vscode.window.activeTextEditor) {
    updateDecorations(vscode.window.activeTextEditor);
  }

  context.subscriptions.push(
    vscode.window.onDidChangeActiveTextEditor((editor) => {
      if (editor) updateDecorations(editor);
    }),
    vscode.workspace.onDidChangeTextDocument((event) => {
      const editor = vscode.window.activeTextEditor;
      if (editor && event.document === editor.document) {
        updateDecorations(editor);
      }
    })
  );
}

export function deactivate(): Thenable<void> | undefined {
  Object.values(decorationTypes).forEach((dt) => dt.dispose());
  return client?.stop();
}
