class TemplateResolver:
    """Resolves the template folder path based on project configuration."""

    @staticmethod
    def resolve(config: dict[str, object]) -> str:
        """
        Resolves the template path.
        Structure: templates/[project_type]-[router]-[client_framework]
        """
        router = "fbr" if config.get('FBRouter') else "modular"
        project_type = config.get('project_type', 'web')
        client_framework = str(config.get('client_framework', 'none')).lower()
        
        if project_type == "api":
            return f"templates/api-{router}"
        
        return f"templates/{project_type}-{router}-{client_framework}"
