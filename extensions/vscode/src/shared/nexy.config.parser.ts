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
    
    // Simple Regex extraction for useAliases (KISS)
    // Supports: useAliases: dict[str, str] = {"@": "src/components"}
    const aliasRegex = /useAliases\s*(?::[^=]+)?\s*=\s*({[\s\S]*?})/;
    const match = content.match(aliasRegex);
    
    if (match) {
      try {
        // Clean up Python dict string to approximate JSON
        let jsonStr = match[1]
          .replace(/'/g, '"')          // Single quotes -> double quotes
          .replace(/#.*$/gm, "")       // Remove comments
          .replace(/,\s*}/g, "}");     // Remove trailing commas
          
        config.useAliases = JSON.parse(jsonStr);
      } catch (e) {
        console.error("Error parsing aliases in nexyconfig.py", e);
      }
    }
  }

  return config;
}

export function resolveWithAlias(importPath: string, workspaceRoot: string, aliases: Record<string, string>): string | null {
  // Sort aliases by length descending to match longest prefix first
  const sortedAliases = Object.entries(aliases).sort((a, b) => b[0].length - a[0].length);

  for (const [alias, replacement] of sortedAliases) {
    if (importPath === alias || importPath.startsWith(alias)) {
      const relativePart = importPath.slice(alias.length);
      // Handle cases where alias doesn't end with / but import does (e.g., @ -> src/ and @components)
      const cleanRelativePart = relativePart.startsWith("/") ? relativePart.slice(1) : relativePart;
      return path.resolve(workspaceRoot, replacement, cleanRelativePart);
    }
  }
  return null;
}
