const esbuild = require("esbuild");

const production = process.argv.includes("--production");
const watch = process.argv.includes("--watch");

async function main() {
  const baseConfig = {
    bundle: true,
    external: ["vscode"],
    format: "cjs",
    platform: "node",
    sourcemap: !production,
    minify: production,
    mainFields: ["module", "main"], // Préférer les versions ESM des libs pour le bundling
  };

  // ── Client (extension principale) ──────────────────────────────────────────
  const clientCtx = await esbuild.context({
    ...baseConfig,
    entryPoints: ["src/extension.ts"],
    outfile: "dist/extension.js",
  });

  // ── Serveur LSP ────────────────────────────────────────────────────────────
  const serverCtx = await esbuild.context({
    ...baseConfig,
    entryPoints: ["src/server/server.ts"],
    outfile: "dist/server.js",
  });

  if (watch) {
    await Promise.all([clientCtx.watch(), serverCtx.watch()]);
    console.log("Watching...");
  } else {
    await Promise.all([clientCtx.rebuild(), serverCtx.rebuild()]);
    await Promise.all([clientCtx.dispose(), serverCtx.dispose()]);
    console.log("Build done.");
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
