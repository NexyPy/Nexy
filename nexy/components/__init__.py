from typing import Any
from nexy.decorators import component

LinkStore = []
@component()
def Link(href: str, caller:Any,**attributes):
    LinkStore.append(href)
    return {"href":href, "caller":caller, **attributes}

@component()
def Import( href :str, caller:Any, **attributes):
    LinkStore.append(href)
    return caller(**attributes)



@component()
def Slot(caller:Any, **attributes):
    return caller(**attributes)




