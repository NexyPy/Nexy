import questionary
from typing import Any
from nexy.i18n import t

class ProjectPrompter:
    """Handles all interactive questions for project initialization."""

    def __init__(self) -> None:
        self.config: dict[str, Any] = {}

    def ask_all(self) -> dict[str, Any]:
        """Runs the full questionnaire and returns the configuration dictionary."""
        self.ask_router()
        self.ask_project_type()
        return self.config

    def ask_router(self) -> None:
        self.config['FBRouter'] = questionary.confirm(
            t("init.ask.router", "Use file-based router?"),
            default=True,
            qmark="»",
            instruction="(yes/no) "
        ).ask()

    def ask_project_type(self) -> None:
        choice = questionary.select(
            t("init.ask.project_type", "Choose the type of project"),
            choices=[
                questionary.Choice(t("init.choice.web", "Web (monolith web app)"), value="web"),
                questionary.Choice(t("init.choice.api", "API (RESTful API)"), value="api"),
            ],
            pointer="ʋ",
            qmark="»",
            show_description=True,
            show_selected=True,
        ).ask()
        
        self.config['project_type'] = choice
        
        if choice == "web":
            self.ask_client_component()

    def ask_client_component(self) -> None:
        use_client = questionary.confirm(
            t("init.ask.client_component", "Use a client component?"), 
            default=True, 
            qmark="»"
        ).ask()
        
        if use_client:
            framework = questionary.select(
                t("init.ask.framework", "Choose the client framework"),
                choices=["React", "Vue", "Svelte", "Preact", "None"],
                pointer="ʋ",
                qmark="»",
            ).ask()
            self.config['client_framework'] = framework
            if framework != "None":
                self.ask_tailwindcss()
        else:
            self.config['client_framework'] = "none"

    def ask_tailwindcss(self) -> None:
        self.config['tailwind'] = questionary.confirm(
            t("init.ask.tailwind", "Use Tailwind CSS?"), 
            default=True, 
            qmark="»"
        ).ask()
