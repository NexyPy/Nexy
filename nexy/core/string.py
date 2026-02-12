import re

class Pathname:
    def __init__(self, pathname: str) -> None:
        self.pathname = "/" + pathname.strip("/")

    def _dynamic_pathname(self, path: str = None) -> str:
        """Transforme [slug] en {slug}."""
        target = path or self.pathname
        # Regex: cherche ce qui est entre crochets, sauf si ça commence par '...'
        return re.sub(r'\[(?!(\.\.\.))([^\]]+)\]', r'{\2}', target)

    def _catch_all(self, path: str = None) -> str:
        """Transforme [...slug] en {slug:path}."""
        target = path or self.pathname
        return re.sub(r'\[\.\.\.([^\]]+)\]', r'{\1:path}', target)

    def _group_pathname(self, path: str = None) -> str:
        """Supprime les segments entre parenthèses comme /(user)/."""
        target = path or self.pathname
        # Supprime /(group) et gère les doubles slashes résultants
        cleaned = re.sub(r'/\([^)]+\)', '', target)
        return cleaned if cleaned else "/"

    def _normalize_pathname(self, path: str = None) -> str:
        target = path or self.pathname
        # Next.js : /docs/index -> /docs et /index -> /
        if target.endswith("/index"):
            target = target[:-6] # Retire "/index"
        return target if target else "/"


    def process(self) -> str:
        """Exécute toutes les transformations dans l'ordre logique."""
        res = self._group_pathname()      # 1. Enlever les groupes (ex: (auth))
        res = self._normalize_pathname(res) # 2. Gérer les index
        res = self._catch_all(res)        # 3. Transformer [...slug]
        res = self._dynamic_pathname(res)  # 4. Transformer [slug]
        
        # Nettoyage final des slashes doubles
        res = re.sub(r'/+', '/', res)
        return res if (res == "/" or not res.endswith("/")) else res.rstrip("/")



class StringTranform :
    def __init__(self): pass

    @staticmethod
    def resolve_pathname(self, pathname: str) -> str:
        return pathname.replace("/", "")
    
    def get_component_name(self, pathname: str) -> str:
        component_name = pathname.split("/")[-1]
        first_letter = component_name[0].capitalize()
        component_name = first_letter + component_name[1:]

        return component_name
    
    

class ComponentString :
    def __init__(self ,pathname: str): 
        self.pathname = pathname

    def get_name(self) -> str:
        component_name = self.pathname.split("/")[-1]
        first_letter = component_name[0].capitalize()
        component_name = first_letter + component_name[1:]
        return component_name