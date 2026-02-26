import * as path from "path";
import * as vscode from "vscode";
import {
  LanguageClient,
  LanguageClientOptions,
  ServerOptions,
  TransportKind,
} from "vscode-languageclient/node";

export class NexyLspClient {
  private client: LanguageClient | undefined;

  constructor(private context: vscode.ExtensionContext, private isNexyProject: boolean) {}

  public async start() {
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
  }

  public async restart() {
    if (this.client) {
      await this.client.stop();
      await this.start();
      vscode.window.showInformationMessage("Nexy Server restarted! 🚀");
    }
  }

  public async stop() {
    return this.client?.stop();
  }
}
