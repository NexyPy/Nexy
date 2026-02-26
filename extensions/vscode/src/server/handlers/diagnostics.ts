import {
  Diagnostic,
  DiagnosticSeverity,
  Range,
  DiagnosticTag,
  DiagnosticRelatedInformation,
  Location,
} from "vscode-languageserver/node";
import { TextDocument } from "vscode-languageserver-textdocument";
import {
  parseHeader,
  getTemplate,
  findUsedComponentsInTemplate,
  type NexyImport,
  type NexyProp,
} from "../../shared/nexy.parser";
import { parseNexyConfig, resolveWithAlias } from "../../shared/config.parser";
import * as fs from "fs";
import { fileURLToPath } from "url";
import * as path from "path";

const JINJA_FILTERS = ["abs","attr","batch","capitalize","center","count","default","dictsort","escape","filesizeformat","first","float","forceescape","format","groupby","indent","int","items","join","last","length","list","lower","map","max","min","pprint","random","reject","rejectattr","replace","reverse","round","safe","select","selectattr","slice","sort","string","striptags","sum","title","tojson","trim","truncate","unique","upper","urlencode","urlize","wordcount","wordwrap"];

export class DiagnosticHandler {
  public handle(doc: TextDocument): Diagnostic[] {
    const text = doc.getText();
    const diagnostics: Diagnostic[] = [];
    const { imports, props } = parseHeader(text);
    const template = getTemplate(text);
    const usedComponents = findUsedComponentsInTemplate(text);

    this.checkImportsExistence(doc, text, imports, diagnostics);
    this.checkMissingImports(doc, text, imports, usedComponents, diagnostics);
    this.checkUnusedImports(doc, text, imports, usedComponents, diagnostics);
    this.checkUnusedProps(doc, text, props, template, diagnostics);
    this.checkJinjaFilters(doc, text, template, diagnostics);
    this.checkPropTypeStrict(doc, text, imports, template, diagnostics);

    return diagnostics;
  }

  private checkImportsExistence(doc: TextDocument, text: string, imports: NexyImport[], diags: Diagnostic[]) {
    const docPath = fileURLToPath(doc.uri);
    const currentDir = path.dirname(docPath);
    
    // Trouver la racine du projet pour les alias
    let workspaceRoot = currentDir;
    while (workspaceRoot !== path.parse(workspaceRoot).root) {
      if (fs.existsSync(path.join(workspaceRoot, "nexyconfig.py"))) break;
      workspaceRoot = path.dirname(workspaceRoot);
    }
    const config = parseNexyConfig(workspaceRoot);

    imports.forEach(imp => {
      let resolvedPath = path.resolve(currentDir, imp.path);
      
      // Essayer de résoudre avec les alias
      const aliasResolved = resolveWithAlias(imp.path, workspaceRoot, config.useAliases);
      if (aliasResolved) {
        resolvedPath = aliasResolved;
      }

      if (!fs.existsSync(resolvedPath)) {
        // Chercher l'offset de l'import
        const importRegex = new RegExp(`from\\s+["']${imp.path}["']`, 'g');
        const match = importRegex.exec(text);
        if (match) {
          const pathStart = match.index + match[0].indexOf(imp.path);
          diags.push({
            severity: DiagnosticSeverity.Error,
            range: Range.create(doc.positionAt(pathStart), doc.positionAt(pathStart + imp.path.length)),
            message: `Module not found: ${imp.path}${aliasResolved ? ` (resolved to: ${aliasResolved})` : ""}`,
            source: "nexy"
          });
        }
      }
    });
  }

  private checkPropTypeStrict(doc: TextDocument, text: string, imports: NexyImport[], template: string, diags: Diagnostic[]) {
    const templateStartOffset = text.indexOf(template);
    if (templateStartOffset === -1) return;

    const componentUsageRegex = /<([A-Z][A-Za-z0-9]*)\s+([^>]*)\/?>/g;
    let match: RegExpExecArray | null;

    while ((match = componentUsageRegex.exec(template)) !== null) {
      const componentName = match[1];
      const attrsText = match[2];
      const imp = imports.find(i => i.name === componentName);
      
      if (imp) {
        // Obtenir le contenu du composant pour localiser la définition de la prop
        let propDefinitions: { name: string, start: number, end: number, sourceUri: string }[] = [];
        try {
          const workspaceRoot = this.getWorkspaceRoot(doc);
          const config = parseNexyConfig(workspaceRoot);
          const resolvedPath = resolveWithAlias(imp.path, workspaceRoot, config.useAliases) || path.resolve(path.dirname(fileURLToPath(doc.uri)), imp.path);
          
          if (fs.existsSync(resolvedPath)) {
            const source = fs.readFileSync(resolvedPath, "utf8");
            const parsed = parseHeader(source);
            const sourceUri = "file://" + resolvedPath.split(path.sep).join("/");
            
            parsed.props.forEach(p => {
              const pIdx = source.indexOf(`${p.name} : prop`);
              if (pIdx !== -1) {
                propDefinitions.push({
                  name: p.name,
                  start: pIdx,
                  end: pIdx + p.name.length,
                  sourceUri
                });
              }
            });
          }
        } catch {}

        const componentProps = this.getComponentProps(doc, imp);
        const attrRegex = /([a-zA-Z0-9-]+)="([^"]*)"/g;
        let attrMatch: RegExpExecArray | null;
        while ((attrMatch = attrRegex.exec(attrsText)) !== null) {
          const attrName = attrMatch[1];
          const attrValue = attrMatch[2];
          const propDef = componentProps.find(p => p.name === attrName);
          const propLocation = propDefinitions.find(pd => pd.name === attrName);
          
          if (!propDef) {
            const attrStart = templateStartOffset + match.index + match[0].indexOf(`${attrName}=`);
            diags.push({
              severity: DiagnosticSeverity.Error,
              range: Range.create(doc.positionAt(attrStart), doc.positionAt(attrStart + attrName.length)),
              message: `Prop "${attrName}" is not defined in component "${componentName}".`,
              source: "nexy",
            });
            continue;
          }

          let error = false;
          let expectedType = propDef.type;

          if (propDef.type === "int" && isNaN(Number(attrValue))) error = true;
          if (propDef.type === "bool" && !["true", "false"].includes(attrValue.toLowerCase())) error = true;
          if (propDef.type === "float" && isNaN(parseFloat(attrValue))) error = true;
          
          if (error) {
            const attrValueOffset = match.index + match[0].indexOf(`${attrName}="${attrValue}"`) + attrName.length + 2;
            const diagnostic: Diagnostic = {
              severity: DiagnosticSeverity.Error,
              range: Range.create(doc.positionAt(templateStartOffset + attrValueOffset), doc.positionAt(templateStartOffset + attrValueOffset + attrValue.length)),
              message: `Type '${attrValue}' is not assignable to type '${expectedType}'.`,
              source: "nexy",
            };

            if (propLocation) {
              diagnostic.relatedInformation = [
                DiagnosticRelatedInformation.create(
                  Location.create(propLocation.sourceUri, Range.create(0, 0, 1000, 0)), // Simplifié, idéalement calculé
                  `The expected type comes from property '${attrName}' which is declared here on component '${componentName}'`
                )
              ];
            }
            diags.push(diagnostic);
          }
        }
      }
    }
  }

  private getWorkspaceRoot(doc: TextDocument): string {
    const docPath = fileURLToPath(doc.uri);
    let workspaceRoot = path.dirname(docPath);
    while (workspaceRoot !== path.parse(workspaceRoot).root) {
      if (fs.existsSync(path.join(workspaceRoot, "nexyconfig.py"))) break;
      workspaceRoot = path.dirname(workspaceRoot);
    }
    return workspaceRoot;
  }

  private getComponentProps(doc: TextDocument, imp: NexyImport): NexyProp[] {
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

      let resolvedPath = path.resolve(currentDir, imp.path);
      const aliasResolved = resolveWithAlias(imp.path, workspaceRoot, config.useAliases);
      if (aliasResolved) {
        resolvedPath = aliasResolved;
      }
      
      if (fs.existsSync(resolvedPath)) {
        const source = fs.readFileSync(resolvedPath, "utf8");
        return parseHeader(source).props;
      }
      
      return [];
    } catch { return []; }
  }

  private checkMissingImports(doc: TextDocument, text: string, imports: NexyImport[], used: string[], diags: Diagnostic[]) {
    used.forEach(name => {
      if (!imports.find(i => i.name === name)) {
        const idx = text.indexOf(`<${name}`);
        if (idx !== -1) {
          diags.push({
            severity: DiagnosticSeverity.Warning,
            range: Range.create(doc.positionAt(idx + 1), doc.positionAt(idx + 1 + name.length)),
            message: `<${name}> is not imported.`,
            source: "nexy",
            code: "nexy.missingImport",
          });
        }
      }
    });
  }

  private checkUnusedImports(doc: TextDocument, text: string, imports: NexyImport[], used: string[], diags: Diagnostic[]) {
    imports.forEach(imp => {
      if (!used.includes(imp.name)) {
        // Souligner toute la ligne d'import pour plus de visibilité
        const importRegex = new RegExp(`^.*\\b${imp.name}\\b.*$`, 'm');
        const match = importRegex.exec(text);
        
        if (match) {
          const start = match.index;
          const end = match.index + match[0].length;
          diags.push({
            severity: DiagnosticSeverity.Hint,
            range: Range.create(doc.positionAt(start), doc.positionAt(end)),
            message: `Import "${imp.name}" unused in template.`,
            source: "nexy",
            code: "nexy.unusedImport",
            tags: [DiagnosticTag.Unnecessary]
          });
        }
      }
    });
  }

  private checkUnusedProps(doc: TextDocument, text: string, props: NexyProp[], template: string, diags: Diagnostic[]) {
    props.forEach(prop => {
      if (!new RegExp(`\\b${prop.name}\\b`).test(template)) {
        const idx = text.indexOf(prop.name);
        if (idx !== -1) {
          diags.push({
            severity: DiagnosticSeverity.Hint,
            range: Range.create(doc.positionAt(idx), doc.positionAt(idx + prop.name.length)),
            message: `Prop "${prop.name}" unused.`,
            source: "nexy",
            code: "nexy.unusedProp",
            tags: [DiagnosticTag.Unnecessary]
          });
        }
      }
    });
  }

  private checkJinjaFilters(doc: TextDocument, text: string, template: string, diags: Diagnostic[]) {
    const templateStartOffset = text.indexOf(template);
    const filterRegex = /\|\s*([a-zA-Z_][a-zA-Z0-9_]*)/g;
    let match: RegExpExecArray | null;
    while ((match = filterRegex.exec(template)) !== null) {
      if (!JINJA_FILTERS.includes(match[1])) {
        const start = templateStartOffset + match.index + match[0].indexOf(match[1]);
        diags.push({
          severity: DiagnosticSeverity.Warning,
          range: Range.create(doc.positionAt(start), doc.positionAt(start + match[1].length)),
          message: `Unknown Jinja2 filter "${match[1]}".`,
          source: "nexy",
        });
      }
    }
  }
}
