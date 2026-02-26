import * as vscode from "vscode";
import * as path from "path";
import * as fs from "fs";

export function registerNexyCommands(context: vscode.ExtensionContext, isNexyProject: boolean) {
  const isEligible = (doc: vscode.TextDocument) => {
    const isNexyFile = doc.languageId === "nexy";
    const isMdxFile = doc.languageId === "mdx";
    return isNexyFile || (isMdxFile && isNexyProject);
  };

  context.subscriptions.push(
    vscode.commands.registerCommand("nexy.createComponent", () => {
       if (vscode.window.activeTextEditor && isEligible(vscode.window.activeTextEditor.document)) {
         return createComponentCommand();
       }
    }),
    vscode.commands.registerCommand("nexy.insertHeader", () => {
      if (vscode.window.activeTextEditor && isEligible(vscode.window.activeTextEditor.document)) {
        return insertHeaderCommand();
      }
    }),
    vscode.commands.registerCommand("nexy.wrapWithComponent", () => {
      if (vscode.window.activeTextEditor && isEligible(vscode.window.activeTextEditor.document)) {
        return wrapWithComponentCommand();
      }
    }),
    vscode.commands.registerCommand("nexy.openDocs", openDocsCommand),
  );
}

async function createComponentCommand() {
  const items: (vscode.QuickPickItem & { value: string })[] = [
    { label: "Page", description: "Nexy Page with title", value: "page" },
    { label: "Layout", description: "Nexy Layout with children slot", value: "layout" },
    { label: "Component UI", description: "Small reusable UI component", value: "component" },
  ];

  const kind = await vscode.window.showQuickPick(items, {
    title: "Nexy Component Type",
    placeHolder: "Choose the type of component to create",
  });

  if (!kind) return;

  const name = await vscode.window.showInputBox({
    title: "Nexy Component Name",
    placeHolder: "Ex: Sidebar",
    validateInput: (value) =>
      value.trim().length === 0 ? "Component name cannot be empty." : undefined,
  });

  if (!name) return;

  const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
  let defaultUri: vscode.Uri | undefined;
  
  if (workspaceFolder) {
    const componentsPath = vscode.Uri.joinPath(workspaceFolder.uri, "src", "components");
    try {
      await vscode.workspace.fs.stat(componentsPath);
      defaultUri = vscode.Uri.joinPath(componentsPath, `${name}.nexy`);
    } catch {
      defaultUri = vscode.Uri.joinPath(workspaceFolder.uri, `${name}.nexy`);
    }
  }

  const targetUri = await vscode.window.showSaveDialog({
    defaultUri,
    filters: { Nexy: ["nexy"] },
    saveLabel: "Create Nexy Component",
  });

  if (!targetUri) return;

  const templateLines: string[] = ["---", "# Nexy Header: Define properties and imports"];

  if (kind.value === "layout") {
    templateLines.push("children : prop[callable] # Main slot");
  } else if (kind.value === "page") {
    templateLines.push('title : prop[str] = "Page Title"');
  } else {
    templateLines.push('label : prop[str] = "Label" # Example prop');
  }

  templateLines.push("---", "");

  if (kind.value === "layout") {
    templateLines.push("<!-- Nexy Layout: Reusable structure -->", "<div>", "  <header>", '    {{ title if title is defined else "Layout" }}', "  </header>", "  <main>", "    {{ children() }}", "  </main>", "</div>", "");
  } else if (kind.value === "page") {
    templateLines.push("<!-- Nexy Page: Route of your application -->", "<main>", "  <h1>{{ title }}</h1>", "  <div>", "    <!-- Page content -->", "  </div>", "</main>", "");
  } else {
    templateLines.push("<!-- UI Component: Small and efficient -->", "<button class=\"nexy-btn\">", "  {{ label }}", "</button>", "", "<style>", "  .nexy-btn { padding: 8px 16px; }", "</style>", "");
  }

  const content = templateLines.join("\n");
  await vscode.workspace.fs.writeFile(targetUri, new TextEncoder().encode(content));

  const doc = await vscode.workspace.openTextDocument(targetUri);
  await vscode.window.showTextDocument(doc, { preview: false });
  vscode.window.showInformationMessage(`Component "${name}.nexy" created successfully! ✨`);
}

async function insertHeaderCommand() {
  const editor = vscode.window.activeTextEditor;
  if (!editor || (editor.document.languageId !== "nexy" && editor.document.languageId !== "mdx")) return;

  const documentText = editor.document.getText();
  if (/^---\s*$/m.test(documentText)) {
    void vscode.window.showInformationMessage("This file already seems to contain a Nexy header.");
    return;
  }

  const snippet = new vscode.SnippetString(["---", 'from "${1:./components/Component.nexy}" import ${2:Component}', "", '${3:title} : prop[${4:str}] = "${5:default}"', "---", "", "$0"].join("\n"));
  await editor.insertSnippet(snippet, new vscode.Position(0, 0));
}

async function wrapWithComponentCommand() {
  const editor = vscode.window.activeTextEditor;
  if (!editor || (editor.document.languageId !== "nexy" && editor.document.languageId !== "mdx")) return;

  const selection = editor.selection;
  if (selection.isEmpty) {
    void vscode.window.showInformationMessage("Select content to wrap first.");
    return;
  }

  const componentName = await vscode.window.showInputBox({
    title: "Nom du composant Nexy",
    placeHolder: "Ex: Card",
    validateInput: (value) => value.trim().length === 0 ? "Le nom du composant ne peut pas être vide." : undefined,
  });

  if (!componentName) return;

  const selectedText = editor.document.getText(selection);
  await editor.edit((editBuilder) => {
    editBuilder.replace(selection, `<${componentName}>\n${selectedText}\n</${componentName}>`);
  });
}

async function openDocsCommand() {
  vscode.env.openExternal(vscode.Uri.parse("https://nexy-framework.org/docs"));
}
