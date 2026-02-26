import * as fs from "fs";
import * as path from "path";

export interface NexyConfig {
  useAliases: Record<string, string>;
}

export function parseNexyConfig(workspaceRoot: string): NexyConfig {
  const configPath = path.join(workspaceRoot, "nexyconfig.py");
  const config: NexyConfig = { useAliases: {} };

  if (fs.existsSync(configPath)) {
    const content = fs.readFileSync(configPath, "utf8");
    
    // Extraction simple par Regex de useAliases (KISS)
    // Supporte le format: useAliases: dict[str, str] = {"@": "src/components"}
    const aliasRegex = /useAliases\s*(?::[^=]+)?\s*=\s*({[\s\S]*?})/;
    const match = content.match(aliasRegex);
    
    if (match) {
      try {
        // Nettoyage pour transformer le dictionnaire Python en JSON approximatif
        let jsonStr = match[1]
          .replace(/'/g, '"')          // Simple quotes -> double quotes
          .replace(/#.*$/gm, "")       // Supprimer les commentaires
          .replace(/,\s*}/g, "}");     // Supprimer les virgules traînantes
          
        config.useAliases = JSON.parse(jsonStr);
      } catch (e) {
        console.error("Erreur lors du parsing des alias dans nexyconfig.py", e);
      }
    }
  }

  return config;
}

export function resolveWithAlias(importPath: string, workspaceRoot: string, aliases: Record<string, string>): string | null {
  for (const [alias, replacement] of Object.entries(aliases)) {
    if (importPath === alias || importPath.startsWith(alias + "/")) {
      const relativePart = importPath.slice(alias.length);
      return path.resolve(workspaceRoot, replacement, relativePart.startsWith("/") ? relativePart.slice(1) : relativePart);
    }
  }
  return null;
}
