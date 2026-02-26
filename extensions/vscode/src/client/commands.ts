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
    { label: "Page", description: "Page Nexy avec titre", value: "page" },
    { label: "Layout", description: "Layout Nexy avec slot children", value: "layout" },
    { label: "Component UI", description: "Petit composant UI réutilisable", value: "component" },
  ];

  const kind = await vscode.window.showQuickPick(items, {
    title: "Type de composant Nexy",
    placeHolder: "Choisissez le type de composant à créer",
  });

  if (!kind) return;

  const name = await vscode.window.showInputBox({
    title: "Nom du composant Nexy",
    placeHolder: "Ex: Sidebar",
    validateInput: (value) =>
      value.trim().length === 0 ? "Le nom du composant ne peut pas être vide." : undefined,
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
    saveLabel: "Créer le composant Nexy",
  });

  if (!targetUri) return;

  const templateLines: string[] = ["---", "# Header Nexy: Définition des propriétés et imports"];

  if (kind.value === "layout") {
    templateLines.push("children : prop[callable] # Slot principal");
  } else if (kind.value === "page") {
    templateLines.push('title : prop[str] = "Titre de page"');
  } else {
    templateLines.push('label : prop[str] = "Label" # Exemple de prop');
  }

  templateLines.push("---", "");

  if (kind.value === "layout") {
    templateLines.push("<!-- Layout Nexy: Structure réutilisable -->", "<div>", "  <header>", '    {{ title if title is defined else "Layout" }}', "  </header>", "  <main>", "    {{ children() }}", "  </main>", "</div>", "");
  } else if (kind.value === "page") {
    templateLines.push("<!-- Page Nexy: Route de votre application -->", "<main>", "  <h1>{{ title }}</h1>", "  <div>", "    <!-- Contenu de la page -->", "  </div>", "</main>", "");
  } else {
    templateLines.push("<!-- Composant UI: Petit et efficace -->", "<button class=\"nexy-btn\">", "  {{ label }}", "</button>", "", "<style>", "  .nexy-btn { padding: 8px 16px; }", "</style>", "");
  }

  const content = templateLines.join("\n");
  await vscode.workspace.fs.writeFile(targetUri, new TextEncoder().encode(content));

  const doc = await vscode.workspace.openTextDocument(targetUri);
  await vscode.window.showTextDocument(doc, { preview: false });
  vscode.window.showInformationMessage(`Composant "${name}.nexy" créé avec succès ! ✨`);
}

async function insertHeaderCommand() {
  const editor = vscode.window.activeTextEditor;
  if (!editor || (editor.document.languageId !== "nexy" && editor.document.languageId !== "mdx")) return;

  const documentText = editor.document.getText();
  if (/^---\s*$/m.test(documentText)) {
    void vscode.window.showInformationMessage("Ce fichier semble déjà contenir un header Nexy.");
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
    void vscode.window.showInformationMessage("Sélectionnez d'abord le contenu à envelopper.");
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
