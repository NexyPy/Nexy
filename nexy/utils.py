import os
import re
import importlib
# 
def deleteFistDotte(string:str)-> str:
    if string.startswith('.'):
        return re.sub(r'^.', '', string)
    else:
        return string
    
def dynamicRoute(route_in:str)-> str:

    # Remplacer [id] par {id}
    route_out = re.sub(r"\[([^\]]+)\]", r"{\1}",route_in)
    # Remplacer {_slug} par {slug:path} pour capturer plusieurs segments
    route_out = re.sub(r"\{_([^\}]+)\}", r"{\1}:path", route_out)

    return route_out

def convertPathToModulePath(path:str)->str:
    return re.sub(r"\\|/", ".", path)

def importModule(path:str):
    try:
        module =importlib.import_module(path) 
    except ModuleNotFoundError as e:
        print(f"Error importing module '{path}': {e}")
    return module




    """
    Trouve le fichier page.html le plus proche dans le dossier courant ou ses parents.
    
    Returns:
        str or None: Le chemin absolu vers page.html si trouvé, None sinon.
    """
    try:
        # Obtenir le chemin absolu du dossier contenant le script actuel
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # D'abord chercher dans le dossier courant
        page_path = os.path.join(current_dir, 'page.html')
        if os.path.isfile(page_path):
            return page_path
        
        # Si pas trouvé, remonter jusqu'au dossier 'app'
        while True:
            # Vérifier si on est dans le dossier 'app'
            if os.path.basename(current_dir) == 'app':
                # Chercher dans le dossier 'app'
                app_page_path = os.path.join(current_dir, 'page.html')
                return app_page_path if os.path.isfile(app_page_path) else None
            
            # Remonter d'un niveau
            parent_dir = os.path.dirname(current_dir)
            
            # Si on est à la racine et qu'on n'a pas trouvé le dossier 'app'
            if parent_dir == current_dir:
                return None
                
            current_dir = parent_dir
            
    except Exception as e:
        print(f"Erreur lors de la recherche de page.html: {e}")
        return None 