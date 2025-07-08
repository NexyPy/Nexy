"""
Author: Espoir Loém

This module provides a ProjectBuilder class to facilitate the creation of project structures
with specified configurations such as project type, database, ORM, test framework, and features.
"""

from typing import List, Optional
from nexy.cli.core.models import CssFramework, ProjectType, Database, ORM, TestFramework
from nexy.cli.core.utils import create_project_structure, setup_virtualenv
from InquirerPy import inquirer

class ProjectBuilder:
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.project_type: Optional[ProjectType] = ProjectType.DEFAULT
        self.database: Optional[Database] = Database.NONE
        self.orm: Optional[ORM] = ORM.NONE
        self.test_framework: Optional[TestFramework] = TestFramework.NONE
        self.css_framework: Optional[CssFramework] = None
        self.features: List[str] = []

    def set_project_type(self, project_type: ProjectType) -> 'ProjectBuilder':
        self.project_type = project_type
        return self

    def set_database(self, database: Database) -> 'ProjectBuilder':
        self.database = database
        return self

    def set_orm(self, orm: ORM) -> 'ProjectBuilder':
        self.orm = orm
        return self

    def set_test_framework(self, test_framework: TestFramework) -> 'ProjectBuilder':
        self.test_framework = test_framework
        return self

    def set_css_framework(self, css_framework: CssFramework) -> 'ProjectBuilder':
        self.css_framework = css_framework
        return self

    def add_feature(self, feature: str) -> 'ProjectBuilder':
        self.features.append(feature)
        return self

    def build(self) -> None:
        """Creates the project structure with the specified configurations."""
        self.add_feature("validation")
        # if inquirer.confirm(message="Voulez-vous ajouter le support CORS?").execute():
        #     self.add_feature("cors")
        # if self.project_type == ProjectType.MICROSERVICE and inquirer.confirm(
        #     message="Voulez-vous ajouter la documentation Swagger?"
        # ).execute():
        #     self.add_feature("swagger")

        create_project_structure(
            project_name=self.project_name,
            project_type=self.project_type,
            database=self.database,
            orm=self.orm,
            test_framework=self.test_framework,
            features=self.features
        )
        setup_virtualenv(self.project_name, '.venv', f'{self.project_name}/requirements.txt')

# Example usage:
# builder = ProjectBuilder("MyProject")
# builder.set_project_type(ProjectType.WEB).set_database(Database.POSTGRESQL).add_feature("authentication").build()