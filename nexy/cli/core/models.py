# Enums for different project options
from enum import Enum


class ProjectType(str, Enum):
    # API = "API"
    MICROSERVICE = "Microservice"
    WEBAPP = "Web Application"
    # FULLSTACK = "Full Stack Application"

class Database(str, Enum):
    MYSQL = "MySQL"
    POSTGRESQL = "PostgreSQL" 
    SQLITE = "SQLite"
    # MONGODB = "MongoDB"
    # REDIS = "Redis"
    NONE = "None"

class ORM(str, Enum):
    PRISMA = "Prisma"
    SQLALCHEMY = "SQLAlchemy"
    # SQLMODEL = "SQLModel"
    NONE = "None"

class TestFramework(str, Enum):
    PYTEST = "Pytest"
    UNITTEST = "Unittest"
    # ROBOT = "Robot Framework"
    NONE = "None"

class RouterType(str, Enum):
    APP_ROUTER = "App Router"
    MANUAL = "Manual Routing"

class AuthType(str, Enum):
    JWT = "JWT Authentication"
    SESSION = "Session Based"
    OAUTH = "OAuth 2.0"
    NONE = "None"

class CacheType(str, Enum):
    REDIS = "Redis"
    MEMCACHED = "Memcached"
    INMEMORY = "In-Memory"
    NONE = "None"

class Languages(str, Enum):
    ENGLISH = "English"
    FRENCH = "Français"
    SPANISH = "Español"
    ARABIC = "العربية"
    HINDI = "हिन्दी"
    CHINESE = "中文"
    PORTUGUESE = "Português"
    GERMAN = "Deutsch"

class CssFramework(str,Enum):
    TAILWIND = "Tailwindcss"
    # SASS = "Sass"
    # UNOCSS = "Unocss"
    NONE = "None"

class TemplateEngine(str,Enum):
    JINJA2 = "Jinja2"
    MASONITE = "Masonite"
    NONE = "None"

class JsFramework(str,Enum):
    REACT = "React"
    NEXTJS = "Nextjs"
    NUXTJS = "Nuxtjs"
    NONE = "None"