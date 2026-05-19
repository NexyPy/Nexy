class TemplateResolver:
    """Resolves the template folder name based on project configuration."""

    @staticmethod
    def resolve(config: dict[str, object]) -> str:
        """
        Resolves the template directory name.
        Structure: [project_type]-[router]
        Client framework suffix filtering is handled by the renderer.
        """
        router = "fbr" if config.get("FBRouter") else "modular"
        project_type = config.get("project_type", "web")

        return f"{project_type}-{router}"
