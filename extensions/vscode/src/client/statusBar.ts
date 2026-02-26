import * as vscode from "vscode";
import { parseHeader, getSection } from "../shared/nexy.parser";

export class NexyStatusBar {
  private statusBarItem: vscode.StatusBarItem;

  constructor(private isNexyProject: boolean) {
    this.statusBarItem = vscode.window.createStatusBarItem(
      vscode.StatusBarAlignment.Right,
      100
    );
    this.statusBarItem.command = "nexy.createComponent";
  }

  public update(editor: vscode.TextEditor | undefined) {
    const config = vscode.workspace.getConfiguration("nexy");
    const enabled = config.get<boolean>("statusBar.enabled", true);

    if (!enabled || !editor) {
      this.statusBarItem.hide();
      return;
    }

    const isNexyFile = editor.document.languageId === "nexy";
    const isMdxFile = editor.document.languageId === "mdx";

    // Condition d'activation: .nexy toujours, .mdx seulement dans projet Nexy
    if (!isNexyFile && !(isMdxFile && this.isNexyProject)) {
      this.statusBarItem.hide();
      return;
    }

    const text = editor.document.getText();
    const { imports, props } = parseHeader(text);
    const offset = editor.document.offsetAt(editor.selection.active);
    const section = getSection(text, offset);

    const sectionLabel = section === "header" ? "Header" : (editor.document.languageId === "mdx" ? "Markdown" : "Template");
    const diagnostics = vscode.languages.getDiagnostics(editor.document.uri);
    const errors = diagnostics.filter(d => d.severity === vscode.DiagnosticSeverity.Error).length;
    const warnings = diagnostics.filter(d => d.severity === vscode.DiagnosticSeverity.Warning).length;

    const { mascot, statusText } = this.getMascotAndStatus(errors, warnings);

    this.statusBarItem.text = `${mascot} ${sectionLabel} · ${props.length} props · ${imports.length} imports`;
    this.statusBarItem.tooltip = `${statusText}\nClick to create a new Nexy component.`;
    this.statusBarItem.show();
  }

  private getMascotAndStatus(errors: number, warnings: number) {
    if (errors > 0) {
      return { mascot: "$(error)", statusText: `Nexy: ${errors} errors 😱` };
    } else if (warnings > 0) {
      return { mascot: "$(warning)", statusText: `Nexy: ${warnings} warnings ⚠️` };
    }
    return { mascot: "$(rocket)", statusText: "Nexy: Perfect code! ✨" };
  }

  public dispose() {
    this.statusBarItem.dispose();
  }
}
