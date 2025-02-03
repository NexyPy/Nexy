from typing import List, Optional
from nexy.cli.core.models import CssFramework, ProjectType, Database, ORM, TestFramework

class ProjectBuilder:
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.project_type: Optional[ProjectType] = None
        self.database: Optional[Database] = None
        self.orm: Optional[ORM] = None
        self.test_framework: Optional[TestFramework] = None
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
    def set_css_framework(self, css_framework:CssFramework) -> 'ProjectBuilder':
        self.css_framework = css_framework
        return self


    def add_feature(self, feature: str) -> 'ProjectBuilder':
        self.features.append(feature)
        return self
    
    

    def build(self) -> None:
        """Crée la structure du projet avec les configurations spécifiées"""
        from nexy.cli.core.utils import create_project_structure, setup_virtualenv
        
        create_project_structure(
            project_name=self.project_name,
            project_type=self.project_type or ProjectType.API,
            database=self.database or Database.NONE,
            orm=self.orm or ORM.NONE,
            test_framework=self.test_framework or TestFramework.NONE,
            features=self.features
        ) 
        setup_virtualenv(self.project_name,'nexy_env', f'{self.project_name}/requirements.txt')