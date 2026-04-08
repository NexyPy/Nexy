import questionary

from nexy.__version__ import __Version__
from nexy.cli.commands.utilities.console import console
from nexy.i18n import t


class InitProject:
    def __init__(self) -> None:
        self.version = __Version__().get()
        self.config = {}

    def ask_questions(self) -> None:
        """Triggers the interactive questions to collect configuration."""
        console.print(t("init.title", "nexy init").format(version=self.version))
        self.ask_router()
        self.ask_project_type()

    def ask_router(self) -> None:
        self.config['FBRouter'] = questionary.confirm(
            t("init.ask.router", "Use file-based router?"),
            default=True,
            qmark="»",
            instruction="(yes/no) "
        ).ask()

    def ask_project_type(self) -> None:
        # Vrai Select interactif
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
        if choice == "web":
            self.ask_client_component()

        self.config['project_type'] = choice


    def ask_client_component(self) -> None:
        use_client = questionary.confirm(t("init.ask.client_component", "Use a client component?"), default=True, qmark="»").ask()
        
        if use_client:
            framework = questionary.select(
                t("init.ask.framework", "Choose the client framework"),
                choices=["React", "Vue", "Svelte", "Preact", "None"],
                pointer="ʋ",
                qmark="»",
            ).ask()
            self.config['client_framework'] = framework
            self.ask_tailwindcss()


    def ask_tailwindcss(self) -> None:
        self.config['tailwind'] = questionary.confirm(t("init.ask.tailwind", "Use Tailwind CSS?"), default=True, qmark="»").ask()


__all__ = ["InitProject"]
