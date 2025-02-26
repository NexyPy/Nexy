"""
Author: Espoir Loém

This module defines various UI components for the Nexy framework. Each component can have children, styles, events, and attributes.
"""

class Styled:
    """Represents the style properties for a component."""
    def __init__(self):
        pass

class Component:
    """Base class for all UI components."""
    def __init__(self, children=None, style=None, events=None, **attributes):
        self.children = children or []
        self.style = style or Styled()
        self.events = events or {}
        self.attributes = attributes

    def __str__(self):
        children_html = ''.join(str(child) for child in self.children)
        attrs = ' '.join(f'{k.replace("_", "-")}="{v}"' for k, v in self.attributes.items())
        return f'<{self.__class__.__name__.lower()} {attrs}>{children_html}</{self.__class__.__name__.lower()}>'

class Text(Component):
    """Represents a text component."""
    def __init__(self, content=None, **attributes):
        super().__init__(children=[content] if content else [], **attributes)

class Button(Component):
    """Represents a button component."""
    def __init__(self, children=None, on_click=None, **attributes):
        events = {'on_click': on_click} if on_click else {}
        super().__init__(children=children or [], events=events, **attributes)

class Link(Component):
    """Represents a hyperlink component."""
    def __init__(self, children=None, **attributes):
        super().__init__(children=children or [], **attributes)

class Container(Component):
    """Represents a container component."""
    def __init__(self, children=None, **attributes):
        super().__init__(children=children or [], **attributes)

class Image(Component):
    """Represents an image component."""
    def __init__(self, **attributes):
        super().__init__(**attributes)

class Audio(Component):
    """Represents an audio component."""
    def __init__(self, **attributes):
        super().__init__(**attributes)

class Video(Component):
    """Represents a video component."""
    def __init__(self, **attributes):
        super().__init__(**attributes)

class Column(Component):
    """Represents a column component."""
    def __init__(self, children=None, **attributes):
        super().__init__(children=children or [], **attributes)

class Row(Component):
    """Represents a row component."""
    def __init__(self, children=None, **attributes):
        super().__init__(children=children or [], **attributes)

class Flex(Component):
    """Represents a flexbox component."""
    def __init__(self, children=None, **attributes):
        super().__init__(children=children or [], **attributes)

class Grid(Component):
    """Represents a grid component."""
    def __init__(self, children=None, **attributes):
        super().__init__(children=children or [], **attributes)

class Table(Component):
    """Represents a table component."""
    def __init__(self, children=None, **attributes):
        super().__init__(children=children or [], **attributes)

class Head(Component):
    """Represents a head component."""
    def __init__(self, children=None, **attributes):
        super().__init__(children=children or [], **attributes)

class Media(Component):
    """Represents a media component."""
    def __init__(self, children=None, **attributes):
        super().__init__(children=children or [], **attributes)

class Dialog(Component):
    """Represents a dialog component."""
    def __init__(self, children=None, **attributes):
        super().__init__(children=children or [], **attributes)

class Form(Component):
    """Represents a form component."""
    def __init__(self, children=None, **attributes):
        super().__init__(children=children or [], **attributes)

class Section(Component):
    """Represents a section component."""
    def __init__(self, children=None, **attributes):
        super().__init__(children=children or [], **attributes)

class Header(Component):
    """Represents a header component."""
    def __init__(self, children=None, **attributes):
        super().__init__(children=children or [], **attributes)

# Example usage:
# button = Button(children=[Text(content="Click me")], on_click="handleClick", class_name="btn-primary")
# print(button)
