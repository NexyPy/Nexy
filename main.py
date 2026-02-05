import ast

class NexyStaticParser(ast.NodeVisitor):
    def __init__(self):
        self.context = {}

    def visit_Assign(self, node):
        # Pour x = 5, on récupère la valeur si c'est une constante
        val = None
        if isinstance(node.value, ast.Constant):
            val = node.value.value
        elif isinstance(node.value, ast.Name):
            val = f"Reference({node.value.id})"
        
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.context[target.id] = val
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        # Pour def user(), la valeur est le nom de la fonction elle-même
        # On pourrait aussi stocker l'objet 'node' pour accéder aux arguments dans Jinja
        self.context[node.name] = node 
        # On ne visite pas le corps de la fonction (évite les variables locales)

    def visit_Import(self, node):
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.context[name] = node

    def visit_ImportFrom(self, node):
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.context[name] = node

# --- Traitement ---
source = """
import os as sys
x = 5
def user(name):
    return name

def add():
    return x + 5
"""

tree = ast.parse(source)
parser = NexyStaticParser()
parser.visit(tree)

# Ton dictionnaire est prêt :

x = 5
def user(name):
    return name

def add():
    return x + 5

jinja_context = parser.context
f = jinja_context["add"].name
print("context:",f)
