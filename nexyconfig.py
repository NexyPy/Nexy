from nexy import Nexy

app = Nexy(
    title="My Nexy App",
    config={
        "debug": True,
        "docs_path": "api_docs"
    }
)()

from fastapi.middleware.cors import CORSMiddleware

# Add CORS middleware to allow requests from specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Adjust this to the specific origin you want to allow
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    
)


