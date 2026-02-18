from typing import *
from fastapi import *
from pathlib import Path as __Path
import importlib as __importlib
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
    __inner = str(__Template().render("__nexy__//src/routes/about.md", context))

    __tpl_path = __Path("__nexy__//src/routes/about.md")
    __layouts_dirs = []
    __parts = list(__tpl_path.parent.parts)
    try:
        __idx_routes = __parts.index("routes")
    except ValueError:
        __layouts_dirs = []
    else:
        __base = __parts[: __idx_routes + 1]
        __layouts_dirs.append(__Path(*__base))
        for __extra in __parts[__idx_routes + 1 :]:
            __base = __base + [__extra]
            __layouts_dirs.append(__Path(*__base))

    __is_layout = False
    if __is_layout and __layouts_dirs:
        __target_dirs = __layouts_dirs[:-1]
    else:
        __target_dirs = __layouts_dirs

    for __directory in reversed(__target_dirs):
        __module_path = __directory.as_posix().replace("/", ".") + ".layout"
        try:
            __mod = __importlib.import_module(__module_path)
        except Exception:
            continue
        __layout = getattr(__mod, "Layout", None)
        if callable(__layout):
            __inner = __layout(children=__inner)
            break

    return __inner
