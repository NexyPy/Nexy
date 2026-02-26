import {
  createConnection,
  TextDocuments,
  ProposedFeatures,
  TextDocumentSyncKind,
  InitializeParams,
  InitializeResult,
} from "vscode-languageserver/node";
import { TextDocument } from "vscode-languageserver-textdocument";
import { getLanguageService } from "vscode-html-languageservice";
import { CompletionHandler } from "./handlers/completion";
import { HoverHandler } from "./handlers/hover";
import { DiagnosticHandler } from "./handlers/diagnostics";
import { CodeActionHandler } from "./handlers/code.actions";
import { DefinitionHandler } from "./handlers/definition";

class NexyLspServer {
  private connection = createConnection(ProposedFeatures.all);
  private documents = new TextDocuments(TextDocument);
  private htmlLanguageService = getLanguageService();
  
  private completionHandler = new CompletionHandler(this.htmlLanguageService);
  private hoverHandler = new HoverHandler();
  private diagnosticHandler = new DiagnosticHandler();
  private codeActionHandler = new CodeActionHandler();
  private definitionHandler = new DefinitionHandler();

  constructor() {
    this.setupHandlers();
    this.documents.listen(this.connection);
    this.connection.listen();
  }

  private setupHandlers() {
    this.connection.onInitialize((_params: InitializeParams): InitializeResult => ({
      capabilities: {
        textDocumentSync: TextDocumentSyncKind.Incremental,
        completionProvider: {
          resolveProvider: false,
          triggerCharacters: ["<", "/", ".", ":", "{", "%", "#", "|", " ", "\"", "'", "="],
        },
        hoverProvider: true,
        codeActionProvider: true,
        definitionProvider: true,
      },
    }));

    this.connection.onCompletion((params) => {
      const doc = this.documents.get(params.textDocument.uri);
      return doc ? this.completionHandler.handle(params, doc) : [];
    });

    this.connection.onHover((params) => {
      const doc = this.documents.get(params.textDocument.uri);
      return doc ? this.hoverHandler.handle(params, doc) : null;
    });

    this.connection.onDefinition((params) => {
      const doc = this.documents.get(params.textDocument.uri);
      return doc ? this.definitionHandler.handle(params, doc) : null;
    });

    this.connection.onCodeAction((params) => {
      const doc = this.documents.get(params.textDocument.uri);
      return doc ? this.codeActionHandler.handle(params, doc) : [];
    });

    this.documents.onDidChangeContent((change) => {
      const diagnostics = this.diagnosticHandler.handle(change.document);
      this.connection.sendDiagnostics({ uri: change.document.uri, diagnostics });
    });
  }
}

new NexyLspServer();
