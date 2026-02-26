import * as vscode from "vscode";
import { parseImports } from "../shared/nexy.parser";
import { FRAMEWORK_COLORS } from "../shared/constants";

export class NexyDecorations {
  private decorationTypes: Record<string, vscode.TextEditorDecorationType>;

  constructor(private isNexyProject: boolean) {
    this.decorationTypes = Object.fromEntries(
      Object.entries(FRAMEWORK_COLORS).map(([fw, color]) => [
        fw,
        vscode.window.createTextEditorDecorationType({ color }),
      ])
    );
  }

  public update(editor: vscode.TextEditor | undefined) {
    if (!editor) return;

    const isNexyFile = editor.document.languageId === "nexy";
    const isMdxFile = editor.document.languageId === "mdx";

    // Condition d'activation: .nexy toujours, .mdx seulement dans projet Nexy
    if (!isNexyFile && !(isMdxFile && this.isNexyProject)) {
      this.clear(editor);
      return;
    }

    const config = vscode.workspace.getConfiguration("nexy");
    const enabled = config.get<boolean>("decorations.enableFrameworkColors", true);

    if (!enabled) {
      this.clear(editor);
      return;
    }

    const imports = parseImports(editor.document.getText());
    this.clear(editor);

    const byFramework = new Map<string, vscode.Range[]>();
    imports.forEach((framework, componentName) => {
      const ranges = this.findComponentRanges(editor.document, componentName);
      if (ranges.length === 0) return;
      if (!byFramework.has(framework)) byFramework.set(framework, []);
      byFramework.get(framework)!.push(...ranges);
    });

    byFramework.forEach((ranges, framework) => {
      const dt = this.decorationTypes[framework];
      if (dt) {
        editor.setDecorations(dt, ranges);
      }
    });
  }

  private findComponentRanges(document: vscode.TextDocument, componentName: string): vscode.Range[] {
    const ranges: vscode.Range[] = [];
    const text = document.getText();
    const regex = new RegExp(`(<\\/?(${componentName}))(?=[\\s/>])`, "g");

    let match: RegExpExecArray | null;
    while ((match = regex.exec(text)) !== null) {
      const nameOffset = match[1].startsWith("</") ? 2 : 1;
      const startOffset = match.index + nameOffset;
      const endOffset = startOffset + componentName.length;
      ranges.push(new vscode.Range(document.positionAt(startOffset), document.positionAt(endOffset)));
    }
    return ranges;
  }

  private clear(editor: vscode.TextEditor) {
    Object.values(this.decorationTypes).forEach((dt) =>
      editor.setDecorations(dt, [])
    );
  }

  public dispose() {
    Object.values(this.decorationTypes).forEach((dt) => dt.dispose());
  }
}
