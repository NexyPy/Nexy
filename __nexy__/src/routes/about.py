from typing import *
from fastapi import *
from nexy import Template as __Template , Import as __Import

def About() -> str:
        title = ['About Page', 'About']

    def user():
        return 'John Doe'

    class Main:

        def get():
            pass
    
    context = {"Main": Main, "title": title, "user": user}
    # Template Rendering
    __inner = __Template().render("__nexy__/src/routes/about.md", context)
    # Layout Wrapping
    return __inner
