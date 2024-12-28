class Component:
    def __init__(self, children=None, tagName: str = "", tagNameList = [],  **attributes):
        self.type = tagName
        self.children = children or []
        self.attributes = attributes
        self.tagNameList= tagNameList 

    def __str__(self):
        # Convertir chaque enfant en sa représentation HTML
        children_html = ''.join(str(child) for child in self.children)
        # Générer les attributs de la balise
        attrs = ' '.join(f'{k.replace("_", "-")}="{v}"' for k, v in self.attributes.items())
        # Retourner la balise complète
        
        return f'<{self.type} {attrs}>{children_html}</{self.type}>'
    

class Text(Component):
    def __init__(self, content=None, type="span", **attributes):
        super().__init__(tagName=type, children=content,**attributes)

class Button(Component):
    def __init__(self, children=None,  type="button", **attributes):
        super().__init__(tagName="button", children=children, type=type ,**attributes)


class Link(Component):
    pass
class Container(Component):
    pass

class Image(Component):
    pass

class Audio(Component):
    pass

class Video(Component):
    pass

class Column(Component):
    pass

class Row(Component):
    pass

class Flex(Component):
    pass

class Grid(Component):
    pass

class Table(Component):
    pass

class Head(Component):
    pass

class Media(Component):
    pass

class Dialog(Component):
    pass

class Form(Component):
    pass

class Section(Component):
    pass

class Header(Component):
    pass