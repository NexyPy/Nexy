import logging

C = {
    "reset": "\033[0m",
    "dim": "\033[2m",
    "blue": "\033[34m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "red": "\033[31m",
    "cyan": "\033[36m",
    "magenta": "\033[35m",
}

# Liste des messages natifs d'Uvicorn à masquer totalement
IGNORED_MESSAGES = [
    "Started server process",
    "Waiting for application startup",
    "Application startup complete",
    "Uvicorn running on",
    "Finished server process",
    "Stopping reloader process",
    "Will watch for changes"
]

class NexyFilter(logging.Filter):
    def filter(self, record):
        # On bloque le log si l'un des messages interdits est présent
        msg = record.getMessage()
        return not any(ignored in msg for ignored in IGNORED_MESSAGES)

class NexyAccessFormatter(logging.Formatter):
    def format(self, record):
        # Sécurité : si record.args n'est pas ce qu'on attend, on fallback sur le message standard
        if not record.args or len(record.args) < 5:
            return f"  {C['blue']}ŋ{C['reset']} {C['dim']}[Info]{C['reset']} {record.getMessage()}"

        # On extrait les arguments de manière dynamique
        # Uvicorn envoie généralement : (host, port, method, path, http_version, status_code)
        # Mais parfois http_version manque.
        args = record.args

        host = str(args[0]).split(":")[0]
        port = str(args[0]).split(":")[-1]
        method = args[1]
        path = args[2]

        # Le status code est presque toujours le dernier élément
        status_code = args[-1] 
        
        method_label = str(method).capitalize()
        # Logique de couleur
        color = C["green"]
        
        if isinstance(status_code, int) and status_code >= 400: color = C["yellow"]
        
        # Détection Socket améliorée
        is_socket = "ws" in path or "socket" in path or status_code == 101
        label = f"{C['magenta']}ws »{C['reset']}" if is_socket else f"{color}{method} »{C['reset']}"

        return f"{label} © {host}:{port}  ® {C['dim']}{path}{C['reset']} , {color}{status_code}{C['reset']} OK"
class NexyDefaultFormatter(logging.Formatter):
    def format(self, record):
        # Pour les erreurs réelles
        level = record.levelname.capitalize()
        label = f"{C['red']}[{level}]{C['reset']}"
        return f"  {C['blue']}ŋ{C['reset']} {label} {record.getMessage()}"

NEXY_LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "nexy_filter": {"()": NexyFilter}
    },
    "formatters": {
        "access": {"()": NexyAccessFormatter},
        "default": {"()": NexyDefaultFormatter},
    },
    "handlers": {
        "access": {
            "class": "logging.StreamHandler",
            "formatter": "access",
            "filters": ["nexy_filter"],
        },
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "filters": ["nexy_filter"],
        },
    },
    "loggers": {
        "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "uvicorn.error": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
    },
}