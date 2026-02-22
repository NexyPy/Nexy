def add_middleware(app: FastAPI):
    app.middleware("http")(nexyHmrPlugin())

    