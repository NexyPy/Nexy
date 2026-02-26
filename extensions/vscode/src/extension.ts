import * as vscode from "vscode";
import { NexyLspClient } from "./client/lspClient";
import { NexyStatusBar } from "./client/statusBar";
import { NexyDecorations } from "./client/decorations";
import { registerNexyCommands } from "./client/commands";
import { 
  EmbedContentProvider, 
  PY_SCHEME, 
  HTML_SCHEME, 
  CSS_SCHEME, 
  JS_SCHEME 
} from "./client/providers/embedded.provider";
import { registerServiceDelegation } from "./client/providers/service.delegation";
import { registerSemanticTokens } from "./semantic.tokens";

let lspClient: NexyLspClient;
let statusBar: NexyStatusBar;
let decorations: NexyDecorations;
let isNexyProject = false;

async function checkNexyProject(): Promise<boolean> {
  const workspaceFolders = vscode.workspace.workspaceFolders;
  if (!workspaceFolders) return false;

  for (const folder of workspaceFolders) {
    // Détection stricte d'un projet Nexy
    const configUri = vscode.Uri.joinPath(folder.uri, "nexyconfig.py");
    const internalUri = vscode.Uri.joinPath(folder.uri, "___nexy__");

    try {
      // Un projet Nexy doit avoir nexyconfig.py ET ___nexy__/
      await vscode.workspace.fs.stat(configUri);
      await vscode.workspace.fs.stat(internalUri);
      return true;
    } catch {
      continue;
    }
  }
  return false;
}

const providers = {
  [PY_SCHEME]: new EmbedContentProvider(),
  [HTML_SCHEME]: new EmbedContentProvider(),
  [CSS_SCHEME]: new EmbedContentProvider(),
  [JS_SCHEME]: new EmbedContentProvider(),
  "nexy-mdx-markdown": new EmbedContentProvider(),
};

export async function activate(context: vscode.ExtensionContext) {
  // 0. Check if this is a Nexy project
  isNexyProject = await checkNexyProject();

  // 1. Initialize LSP Client (S'adapte dynamiquement à .nexy / .mdx)
  lspClient = new NexyLspClient(context, isNexyProject);
  await lspClient.start();

  // 2. Initialize UI Components
  statusBar = new NexyStatusBar(isNexyProject);
  decorations = new NexyDecorations(isNexyProject);
  context.subscriptions.push(statusBar, decorations);

  // 3. Register Commands
  registerNexyCommands(context, isNexyProject);
  context.subscriptions.push(
    vscode.commands.registerCommand("nexy.restartLSP", () => lspClient.restart())
  );

  // 4. Register Virtual Document Providers
  Object.entries(providers).forEach(([scheme, provider]) => {
    context.subscriptions.push(
      vscode.workspace.registerTextDocumentContentProvider(scheme, provider)
    );
  });

  // 5. Register Service Delegation (IntelliSense, Hover, Definition)
  registerServiceDelegation(context, providers, isNexyProject);

  // 6. Global Listeners
  const editor = vscode.window.activeTextEditor;
  if (editor) {
    decorations.update(editor);
    statusBar.update(editor);
  }

  context.subscriptions.push(
    vscode.window.onDidChangeActiveTextEditor((e) => {
      decorations.update(e);
      statusBar.update(e);
    }),
    vscode.workspace.onDidChangeTextDocument((event) => {
      const activeEditor = vscode.window.activeTextEditor;
      if (activeEditor && event.document === activeEditor.document) {
        decorations.update(activeEditor);
        statusBar.update(activeEditor);
      }
    }),
    vscode.window.onDidChangeTextEditorSelection((event) => {
      statusBar.update(event.textEditor);
    }),
    vscode.languages.onDidChangeDiagnostics(() => {
      const activeEditor = vscode.window.activeTextEditor;
      if (activeEditor) {
        statusBar.update(activeEditor);
      }
    })
  );

  // 7. Nexy Welcome Message
  const nexyFiles = await vscode.workspace.findFiles("**/*.nexy", null, 1);
  if (nexyFiles.length > 0) {
    vscode.window.showInformationMessage("Nexy is ready to lift off! 🚀 Happy coding!");
  }

  registerSemanticTokens(context);
}

export function deactivate(): Thenable<void> | undefined {
  statusBar?.dispose();
  decorations?.dispose();
  return lspClient?.stop();
}
