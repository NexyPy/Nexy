from fastapi import HTTPException, Header, Depends, Request
from typing import Optional

# 1. Une fonction de dépendance standard (FastAPI style)
async def verify_admin_token():
    """Vérifie si le token admin est présent dans les headers."""
    print("load verify_admin_token")

# 2. Une autre dépendance pour logger les accès
async def log_admin_activity(request: Request):
    """Log l'IP de l'utilisateur qui tente d'accéder à la zone admin."""
    print(f"🛡️ Admin Access Attempt: {request.client.host} on {request.url.path}")


dependencies = [
    log_admin_activity,
    verify_admin_token,
]