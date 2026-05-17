import os; 
def pycache() -> None:
    os.makedirs("./__pycache__", exist_ok=True); 
    os.environ["PYTHONPYCACHEPREFIX"] = "./__pycache__"
