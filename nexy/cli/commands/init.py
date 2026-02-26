from nexy.cli.commands.utilities.init_project import InitProject


def init() -> None:
    # Initialize the nexy project
    project = InitProject()
    project.ask_router()
    project.ask_project_type()
