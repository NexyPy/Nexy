import questionary
from nexy.cli.commands.utilities.console import console

class InitProject:
    def __init__(self) -> None:
        console.print("[bold blue]A. nexy init[/bold blue]\n")
        self.config = {}

    def ask_router(self) -> None:
        self.config['router'] = questionary.confirm(
            "Would you like to use the File Based router ?",
            default=True,
            qmark="»»",
            instruction="(yes/no) "
        ).ask()

    def ask_project_type(self) -> None:
        # Vrai Select interactif
        choice = questionary.select(
            "C. choice the type of project",
            choices=[
                questionary.Choice("web (monolith web app)", value="web"),
                questionary.Choice("api (restful api)", value="api"),
            ],
            pointer="❯"
        ).ask()
        self.config['project_type'] = choice

    def ask_client_component(self) -> None:
        use_client = questionary.confirm("C. Would you like to use a client component?").ask()
        
        if use_client:
            framework = questionary.select(
                "C1. choice the type of client component",
                choices=["React", "Vue", "Svelte", "Preact", "None"],
                pointer="❯"
            ).ask()
            self.config['client_framework'] = framework
        else:
            self.config['client_framework'] = None

    def ask_tailwindcss(self) -> None:
        self.config['tailwind'] = questionary.confirm("C2. Would you like to use tailwindcss?").ask()
