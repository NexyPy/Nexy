class Console:
    @staticmethod
    def banner(title: str) -> None:
        line = "─" * max(20, len(title) + 4)


    @staticmethod
    def info(message: str) -> None:
        print(f"{message}")

    @staticmethod
    def success(message: str) -> None:
        print(f"✔ {message}")

    @staticmethod
    def warn(message: str) -> None:
        print(f"⚠ {message}")

    @staticmethod
    def error(message: str) -> None:
        print(f"✖ {message}")
