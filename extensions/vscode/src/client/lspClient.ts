import * as path from "path";
import * as vscode from "vscode";
import {
  LanguageClient,
  LanguageClientOptions,
  ServerOptions,
  TransportKind,
  State,
} from "vscode-languageclient/node";

export class NexyLspClient {
  private client: LanguageClient | undefined;
  private isStarting = false;

  constructor(private context: vscode.ExtensionContext, private isNexyProject: boolean) {}

  public async start() {
    if (this.isStarting || (this.client && this.client.state !== State.Stopped)) {
      return;
    }

    this.isStarting = true;
    try {
      const serverModule = this.context.asAbsolutePath(path.join("dist", "server.js"));

      const serverOptions: ServerOptions = {
        run: { module: serverModule, transport: TransportKind.ipc },
        debug: {
          module: serverModule,
          transport: TransportKind.ipc,
          options: { execArgv: ["--nolazy", "--inspect=6009"] },
        },
      };

      const documentSelector = [{ scheme: "file", language: "nexy" }];
      const fileEvents = [vscode.workspace.createFileSystemWatcher("**/*.nexy")];

      // .mdx seulement dans un projet nexy
      if (this.isNexyProject) {
        documentSelector.push({ scheme: "file", language: "mdx" });
        fileEvents.push(vscode.workspace.createFileSystemWatcher("**/*.mdx"));
      }

      const clientOptions: LanguageClientOptions = {
        documentSelector,
        synchronize: {
          fileEvents,
        },
      };

      this.client = new LanguageClient("nexyLsp", "Nexy LSP", serverOptions, clientOptions);
      await this.client.start();
    } catch (e) {
      console.error("Failed to start Nexy LSP Client", e);
      vscode.window.showErrorMessage(`Nexy LSP failed to start: ${e}`);
    } finally {
      this.isStarting = false;
    }
  }

  public async restart() {
    if (this.isStarting) return;
    
    try {
      if (this.client && this.client.state === State.Running) {
        await this.client.stop();
      }
      await this.start();
      vscode.window.showInformationMessage("Nexy Server restarted! 🚀");
    } catch (e) {
      console.error("Failed to restart Nexy LSP Client", e);
    }
  }

  public async stop() {
    if (this.client && this.client.state === State.Running) {
      return this.client.stop();
    }
  }
}
