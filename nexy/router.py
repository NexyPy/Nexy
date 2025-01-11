import os
from fastapi import APIRouter
from .utils import deleteFistDotte, dynamicRoute,importModule,convertPathToModulePath

# 
def FIND_ROUTES(base_path):
    routes:list = []
    
    # Verify if the 'app' folder exists
    if os.path.exists(base_path) and os.path.isdir(base_path):
        # Explore the 'app' folder and its subfolders
        for root, dirs, files in os.walk(base_path):
            #supprimers des _folder
            dirs[:] = [d for d in dirs if not d.startswith("_")]

            route = {
                "pathname": f"{'/' if os.path.basename(root) == base_path else '/' +  deleteFistDotte(os.path.relpath(root, base_path).replace('\\','/'))}",
                "dirName": root
            }
            controller = os.path.join(root, 'controller.py')

            # Check for files and add to dictionary
            if os.path.exists(controller):
                route["module"] = convertPathToModulePath(f"{root}/controller")    

            routes.append(route)

    return routes




def Router():
    """
    Charge dynamiquement les routes à partir du répertoire 'app'.
    """
    app = APIRouter()
    routes = FIND_ROUTES(base_path="app")
    HTTP_METHODES: tuple = ["DELETE", "GET", "OPTIONS", "PATCH", "POST", "PUT"]

    for route in routes:
        pathname = dynamicRoute(route_in=route["pathname"])

        if "module" in route:
            try:
                # Tentative d'importation du module
                module = importModule(path=route["module"])
                
                for function_name in dir(module):
                    function = getattr(module, function_name)

                    # Vérifie que la fonction est callable et a des annotations
                    if callable(function) and hasattr(function, "__annotations__"):
                        params = getattr(function, "params", {})

                        # Ajout de la route pour chaque méthode HTTP
                        if function_name in HTTP_METHODES:
                            try:
                                app.add_api_route(
                                    path=pathname,
                                    endpoint=function,
                                    methods=[function_name],
                                    **{key: value for key, value in params.items() if key != "tags"},
                                    tags=params.get("tags") if params.get("tags") else [pathname]
                                )
                            except Exception as e:
                                # Capture les erreurs spécifiques à l'ajout de la route
                                print(f"Erreur lors de l'ajout de la route {pathname} pour la méthode {function_name}: {e}")
                                app.add_api_route(
                                    path=pathname,
                                    endpoint=lambda: {"error": f"Erreur lors de la méthode {function_name} pour la route {pathname}. {str(e)}"},
                                    methods=[function_name],
                                    status_code=500
                                )

                        # Ajout d'une route WebSocket si la méthode 'Socket' existe
                        elif function_name == "SOCKET":
                            try:
                                app.add_api_websocket_route(f"{pathname}/ws", function)
                            except Exception as e:
                                print(f"Erreur lors de l'ajout du WebSocket pour la route {pathname}: {e}")
                                app.add_api_websocket_route(
                                    f"{pathname}/ws",
                                    lambda: {"error": f"Erreur lors de la connexion WebSocket pour la route {pathname}. {str(e)}"}
                                )

            except Exception as e:
                # Capture les erreurs d'importation ou d'autres erreurs générales
                print(f"Erreur lors du chargement du module {route['module']}: {e}")
                app.add_api_route(
                    path=pathname,
                    endpoint=lambda: {"error": f"Erreur lors du chargement du module {route['module']}. {str(e)}"},
                    methods=["GET"],
                    status_code=500
                )
    return app