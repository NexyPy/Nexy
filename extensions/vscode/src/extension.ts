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
  parseHeader,
  getSection,
} from "./utils";

let client: LanguageClient;
let statusBarItem: vscode.StatusBarItem | undefined;

// ─── Decoration types par framework ──────────────────────────────────────────
const decorationTypes: Record<string, vscode.TextEditorDecorationType> =
  Object.fromEntries(
    Object.entries(FRAMEWORK_COLORS).map(([fw, color]) => [
      fw,
      vscode.window.createTextEditorDecorationType({ color }),
    ]),
  );

function updateDecorations(editor: vscode.TextEditor) {
  if (editor.document.languageId !== "nexy") {
    return;
  }

  const config = vscode.workspace.getConfiguration("nexy");
  const enabled = config.get<boolean>("decorations.enableFrameworkColors", true);

  if (!enabled) {
    Object.values(decorationTypes).forEach((dt) =>
      editor.setDecorations(dt, []),
    );
    return;
  }

  const imports = parseImports(editor.document.getText());

  Object.values(decorationTypes).forEach((dt) =>
    editor.setDecorations(dt, []),
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

function updateStatusBar(editor: vscode.TextEditor | undefined) {
  if (!statusBarItem) {
    return;
  }

  const config = vscode.workspace.getConfiguration("nexy");
  const enabled = config.get<boolean>("statusBar.enabled", true);

  if (!enabled || !editor || editor.document.languageId !== "nexy") {
    statusBarItem.hide();
    return;
  }

  const text = editor.document.getText();
  const { imports, props } = parseHeader(text);

  const offset = editor.document.offsetAt(editor.selection.active);
  const section = getSection(text, offset);

  const importsCount = imports.length;
  const propsCount = props.length;

  const sectionLabel = section === "header" ? "Header" : "Template";

  statusBarItem.text = `Nexy $(symbol-structure) ${sectionLabel} · ${propsCount} props · ${importsCount} imports`;
  statusBarItem.tooltip = "Nexy — résumé du fichier courant";
  statusBarItem.show();
}

type ComponentKind = "page" | "layout" | "component";

async function createComponentCommand() {
  const items: (vscode.QuickPickItem & { value: ComponentKind })[] = [
    {
      label: "Page",
      description: "Page Nexy avec titre",
      value: "page",
    },
    {
      label: "Layout",
      description: "Layout Nexy avec slot children",
      value: "layout",
    },
    {
      label: "Component UI",
      description: "Petit composant UI réutilisable",
      value: "component",
    },
  ];

  const kind = await vscode.window.showQuickPick(
    items,
    {
      title: "Type de composant Nexy",
      placeHolder: "Choisissez le type de composant à créer",
    },
  );

  if (!kind) {
    return;
  }

  const name = await vscode.window.showInputBox({
    title: "Nom du composant Nexy",
    placeHolder: "Ex: Sidebar",
    validateInput: (value) =>
      value.trim().length === 0 ? "Le nom du composant ne peut pas être vide." : undefined,
  });

  if (!name) {
    return;
  }

  const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
  const defaultUri = workspaceFolder
    ? vscode.Uri.joinPath(workspaceFolder.uri, "src", "components", `${name}.nexy`)
    : undefined;

  const targetUri = await vscode.window.showSaveDialog({
    defaultUri,
    filters: { Nexy: ["nexy"] },
    saveLabel: "Créer le composant Nexy",
  });

  if (!targetUri) {
    return;
  }

  const templateLines: string[] = [];
  templateLines.push("---");

  if (kind.value === "layout") {
    templateLines.push("children : prop[callable]");
  } else if (kind.value === "page") {
    templateLines.push('title : prop[str] = "Titre de page"');
  } else {
    templateLines.push('label : prop[str] = "Label"');
  }

  templateLines.push("---", "");

  if (kind.value === "layout") {
    templateLines.push(
      "<div>",
      "  <header>",
      '    {{ title if title is defined else "Layout" }}',
      "  </header>",
      "  <main>",
      "    {{ children() }}",
      "  </main>",
      "</div>",
      "",
    );
  } else if (kind.value === "page") {
    templateLines.push(
      "<main>",
      "  <h1>{{ title }}</h1>",
      "  <div>",
      "    <!-- Contenu de la page -->",
      "  </div>",
      "</main>",
      "",
    );
  } else {
    templateLines.push(
      "<button>",
      "  {{ label }}",
      "</button>",
      "",
    );
  }

  const content = templateLines.join("\n");
  const encoder = new TextEncoder();
  await vscode.workspace.fs.writeFile(targetUri, encoder.encode(content));

  const doc = await vscode.workspace.openTextDocument(targetUri);
  await vscode.window.showTextDocument(doc, { preview: false });
}

async function insertHeaderCommand() {
  const editor = vscode.window.activeTextEditor;
  if (!editor || editor.document.languageId !== "nexy") {
    return;
  }

  const documentText = editor.document.getText();
  if (/^---\s*$/m.test(documentText)) {
    void vscode.window.showInformationMessage("Ce fichier semble déjà contenir un header Nexy.");
    return;
  }

  const snippet = new vscode.SnippetString(
    [
      "---",
      'from "${1:./components/Component.nexy}" import ${2:Component}',
      "",
      '${3:title} : prop[${4:str}] = "${5:default}"',
      "---",
      "",
      "$0",
    ].join("\n"),
  );

  await editor.insertSnippet(snippet, new vscode.Position(0, 0));
}

async function wrapWithComponentCommand() {
  const editor = vscode.window.activeTextEditor;
  if (!editor || editor.document.languageId !== "nexy") {
    return;
  }

  const selection = editor.selection;
  if (selection.isEmpty) {
    void vscode.window.showInformationMessage("Sélectionnez d'abord le contenu à envelopper.");
    return;
  }

  const selectedText = editor.document.getText(selection);

  const componentName = await vscode.window.showInputBox({
    title: "Nom du composant Nexy",
    placeHolder: "Ex: Card",
    validateInput: (value) =>
      value.trim().length === 0 ? "Le nom du composant ne peut pas être vide." : undefined,
  });

  if (!componentName) {
    return;
  }

  await editor.edit((editBuilder) => {
    const wrapped = `<${componentName}>\n${selectedText}\n</${componentName}>`;
    editBuilder.replace(selection, wrapped);
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

  statusBarItem = vscode.window.createStatusBarItem(
    vscode.StatusBarAlignment.Right,
    100,
  );
  statusBarItem.command = "nexy.createComponent";
  context.subscriptions.push(statusBarItem);

  // ── Décorations framework ───────────────────────────────────────────────────
  if (vscode.window.activeTextEditor) {
    updateDecorations(vscode.window.activeTextEditor);
    updateStatusBar(vscode.window.activeTextEditor);
  }

  context.subscriptions.push(
    vscode.window.onDidChangeActiveTextEditor((editor) => {
      if (editor) {
        updateDecorations(editor);
        updateStatusBar(editor);
      } else {
        updateStatusBar(undefined);
      }
    }),
    vscode.workspace.onDidChangeTextDocument((event) => {
      const editor = vscode.window.activeTextEditor;
      if (editor && event.document === editor.document) {
        updateDecorations(editor);
        updateStatusBar(editor);
      }
    }),
    vscode.window.onDidChangeTextEditorSelection((event) => {
      updateStatusBar(event.textEditor);
    }),
    vscode.commands.registerCommand("nexy.createComponent", createComponentCommand),
    vscode.commands.registerCommand("nexy.insertHeader", insertHeaderCommand),
    vscode.commands.registerCommand("nexy.wrapWithComponent", wrapWithComponentCommand),
  );
}

export function deactivate(): Thenable<void> | undefined {
  Object.values(decorationTypes).forEach((dt) => dt.dispose());
  statusBarItem?.dispose();
  return client?.stop();
}
