from typing import *
from fastapi import *
from nexy import Template as __Template , Import as __Import

def About() -> str:
        from __nexy__.src.components.user import User
    title = ['About Page', 'About']

    def user():
        return 'John Doe'

    class Main:

        def get():
            pass
    
    context = {"Main": Main, "User": User, "title": title, "user": user}
    # Template Rendering
    __inner = str(__Template().render("__nexy__//src/routes/about.md", context))
    # Layout Wrapping
    return __inner
