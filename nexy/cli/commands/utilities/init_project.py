import questionary
from nexy.__version__ import __Version__
from nexy.cli.commands.utilities.console import console

class InitProject:
    def __init__(self) -> None:
        version = __Version__().get()
        console.print(f"nexy@{version} init")
        self.config = {}

    def ask_router(self) -> None:
        self.config['router'] = questionary.confirm(
            "Would you like to use the File Based router ?",
            default=True,
            qmark="»",
            instruction="(yes/no) "
        ).ask()

    def ask_project_type(self) -> None:
        # Vrai Select interactif
        choice = questionary.select(
            "Choice the type of project",
            choices=[
                questionary.Choice("Web (monolith web app)", value="web"),
                questionary.Choice("API (restful api)", value="api"),
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
        use_client = questionary.confirm("Would you like to use a client component?", default=True, qmark="»").ask()
        
        if use_client:
            framework = questionary.select(
                "Choice the type of client component",
                choices=["React", "Vue", "Svelte", "Preact", "None"],
                pointer="ʋ",
                qmark="»",
            ).ask()
            self.config['client_framework'] = framework
            self.ask_tailwindcss()


    def ask_tailwindcss(self) -> None:
        self.config['tailwind'] = questionary.confirm("Would you like to use tailwindcss?", default=True, qmark="»").ask()
