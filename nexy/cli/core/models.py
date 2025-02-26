"""
Author: Espoir Loém

This module defines various Enum classes to represent different configuration options
for projects, such as project type, database, ORM, test framework, and more.
These Enums are used to standardize and simplify the selection of these options
throughout the application.
"""

from enum import Enum

class ProjectType(str, Enum):
    """Enum for different types of projects."""
    MICROSERVICE = "Microservice"
    WEBAPP = "Web Application"

class Database(str, Enum):
    """Enum for supported database types."""
    MYSQL = "MySQL"
    POSTGRESQL = "PostgreSQL"
    MONGODB = "MongoDB"
    SQLITE = "SQLite"
    NONE = "None"

class ORM(str, Enum): 
    """Enum for supported ORM frameworks."""
    PRISMA = "Prisma"
    SQLALCHEMY = "SQLAlchemy"
    NONE = "None"

class TestFramework(str, Enum):
    """Enum for supported test frameworks."""
    PYTEST = "Pytest"
    UNITTEST = "Unittest"
    NONE = "None"

class RouterType(str, Enum):
    """Enum for router configuration types."""
    APP_ROUTER = "App Router"
    MANUAL = "Manual Routing"

class AuthType(str, Enum):
    """Enum for authentication methods."""
    JWT = "JWT Authentication"
    SESSION = "Session Based"
    OAUTH = "OAuth 2.0"
    NONE = "None"

class CacheType(str, Enum):
    """Enum for caching strategies."""
    REDIS = "Redis"
    MEMCACHED = "Memcached"
    INMEMORY = "In-Memory"
    NONE = "None"

class Languages(str, Enum):
    """Enum for supported languages."""
    ENGLISH = "English"
    FRENCH = "Français"
    SPANISH = "Español"
    ARABIC = "العربية"
    HINDI = "हिन्दी"
    CHINESE = "中文"
    PORTUGUESE = "Português"
    GERMAN = "Deutsch"

class CssFramework(str, Enum):
    """Enum for CSS frameworks."""
    TAILWIND = "Tailwindcss"
    NONE = "None"

class TemplateEngine(str, Enum):
    """Enum for template engines."""
    JINJA2 = "Jinja2"
    MASONITE = "Masonite"
    NONE = "None"

class JsFramework(str, Enum):
    """Enum for JavaScript frameworks."""
    REACT = "React"
    NEXTJS = "Nextjs"
    NUXTJS = "Nuxtjs"
    NONE = "None"