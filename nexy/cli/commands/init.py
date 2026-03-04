from nexy.cli.commands.utilities.init_project import InitProject


def init() -> None:
    # Initialize the nexy project
    project = InitProject()
    print(project.config)
