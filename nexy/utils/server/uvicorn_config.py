import linecache
import logging
import os
import traceback
from typing import cast

# ANSI colors for terminal
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

# Uvicorn system messages to hide for a cleaner console
IGNORED_MESSAGES = [
    "Started server process",
    "Waiting for application startup",
    "Application startup complete",
    "Uvicorn running on",
    "Finished server process",
    "Stopping reloader process",
    "Will watch for changes",
]

# Signs associated with main HTTP status codes (no emojis)
status_indicators = {
    200: "✓",
    201: "+",
    304: "*",
    307: ">",
    400: "!",
    404: "o",
    422: "x",
    500: "!!",
}


class NexyFilter(logging.Filter):
    """Cleaning filter to block redundant initialization logs."""

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        return not any(ignored in msg for ignored in IGNORED_MESSAGES)


class NexyAccessFormatter(logging.Formatter):
    """Ultra-readable formatter for HTTP requests and WebSocket connections."""

    def format(self, record: logging.LogRecord) -> str:
        msg = record.getMessage()
        if not record.args or len(record.args) < 5:
            return f"  {C['blue']}ŋ{C['reset']} {C['dim']}[Info]{C['reset']} {msg}"

        args = record.args
        if isinstance(args, tuple):
            arg0, arg1, arg2, arg_last = args[0], args[1], args[2], args[-1]
        elif isinstance(args, dict):
            arg0 = args.get("a", "")
            arg1 = args.get("b", "")
            arg2 = args.get("c", "")
            arg_last = args.get("d", 0)
        else:
            return f"  {C['blue']}ŋ{C['reset']} {msg}"

        addr = str(arg0) if arg0 else "unknown"
        host = addr.split(":")[0] if ":" in addr else addr
        port = addr.split(":")[-1] if ":" in addr else "3000"

        method = str(arg1)
        path = str(arg2)

        try:
            status_code = int(cast(int, arg_last))
        except (ValueError, TypeError):
            status_code = 200

        color = C["green"]
        if 300 <= status_code < 400:
            color = C["cyan"]
        elif 400 <= status_code < 500:
            color = C["yellow"]
        elif status_code >= 500:
            color = C["red"]

        is_socket = "ws" in path or "socket" in path or status_code == 101
        label = f"{C['magenta']}ws{C['reset']} »" if is_socket else f"{color}{method}{C['reset']} »"

        indicator = status_indicators.get(status_code, "!")

        return f"{label} {C['dim']}{host}{C['reset']}:{C['blue']}{port}{C['reset']} {color}{path}{C['reset']} , {color}{status_code}{C['reset']} © {indicator}"


class NexyDefaultFormatter(logging.Formatter):
    """Universal formatter handling errors based on function, class, or module level."""

    def format(self, record: logging.LogRecord) -> str:
        msg = record.getMessage()
        level = record.levelname.capitalize()

        color = C["red"] if record.levelno >= 40 else C["dim"]
        prefix = f"{color}{level}{C['reset']} »"
        result = f"{prefix} {msg}"

        if record.exc_info:
            tb_frames = traceback.extract_tb(record.exc_info[2])
            if tb_frames:
                frame = tb_frames[-1]

                try:
                    file_name = os.path.relpath(frame.filename, start=os.getcwd())
                except Exception:
                    file_name = os.path.basename(frame.filename)

                line_no = frame.lineno or 0
                scope_name = frame.name or "<module>"

                result += f'\n  File "{file_name}", line {line_no}, in {scope_name}\n'

                # --- STRATÉGIE DE DÉTECTION DU BLOC CONTEXTUEL ---
                start_line = line_no
                block_indent = None
                is_global_scope = scope_name == "<module>"

                if not is_global_scope:
                    # On remonte pour chercher le début de la fonction ou de la classe
                    while start_line > 1:
                        prev_line = linecache.getline(frame.filename, start_line).rstrip("\n")
                        stripped = prev_line.lstrip()
                        if stripped.startswith(("def ", "class ")):
                            block_indent = len(prev_line) - len(stripped)
                            break
                        start_line -= 1

                # Si on est au niveau global du module ou qu'aucune structure n'a été trouvée
                if block_indent is None:
                    start_line = max(1, line_no - 4)
                    end_line = line_no + 4
                else:
                    # On descend pour trouver la fin de la fonction ou de la classe basée sur l'indentation
                    end_line = line_no
                    while True:
                        next_line = linecache.getline(frame.filename, end_line + 1)
                        if not next_line:
                            break

                        next_stripped = next_line.rstrip("\n")
                        if next_stripped.strip():  # Ignore les lignes vides pour le calcul
                            current_indent = len(next_stripped) - len(next_stripped.lstrip())
                            # Fin du bloc si l'indentation baisse ou revient au niveau de la fonction/classe
                            if current_indent <= block_indent and end_line >= line_no:
                                break
                        end_line += 1

                # Garde-fou visuel : Si le bloc (fonction/classe) est trop massif, on restreint la vue
                if (end_line - start_line) > 16:
                    start_line = max(1, line_no - 4)
                    end_line = line_no + 4

                # --- RENDU DE L'EXTRAIT DE CODE ---
                for current_line in range(start_line, end_line + 1):
                    raw_line = linecache.getline(frame.filename, current_line)
                    if not raw_line:
                        continue

                    clean_line = raw_line.rstrip("\n")

                    if current_line == line_no:
                        indent = len(clean_line) - len(clean_line.lstrip())
                        code_part = clean_line[indent:]
                        caret_indent = " " * (indent + 6)
                        caret = "~" * max(1, len(code_part)) + "^~"

                        result += (
                            f"    {C['red']}➔{C['reset']}  {C['red']}{clean_line}{C['reset']}\n"
                        )
                        result += f"{caret_indent}{C['red']}{caret}{C['reset']}\n"
                    else:
                        result += f"       {C['dim']}{clean_line}{C['reset']}\n"

        return result.rstrip("\n")


# Configuration prête pour uvicorn.run()
NEXY_LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"nexy_filter": {"()": NexyFilter}},
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
