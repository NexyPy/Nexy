GETTING_STARTED:list[dict[str,str]] = [
    {"label":"Introduction","href":"", "status":"active"},
    {"label":"Create a Projet","href":"#", "status":"active"},
    {"label":"Projet Structure","href":"#", "status":"active"},
    {"label":"Build and Deploy","href":"#", "status":"active"},
]

FB_ROUTERS:list[dict[str,str]] = [
    {"label":"Introduction","href":"", "status":"active"},
    {"label":"Pages","href":"", "status":"active"},
    {"label":"Layouts","href":"", "status":"active"},
    {"label":"Dependencies","href":"", "status":"active"},
    {"label":"Middlewares","href":"", "status":"active"},
    {"label":"Route Handlers","href":"", "status":"active"},
    {"label":"Route Parameters","href":"", "status":"active"},
    {"label":"Query Parameters","href":"", "status":"active"},
] 

COMPONENTS:list[dict[str,str]] = [
    {"label":"Introduction","href":"", "status":"active"},
    {"label":"Create a Component","href":"", "status":"active"},
    {"label":"Writing markup with nexy","href":"", "status":"active"},
    {"label":"Python in nexy template","href":"", "status":"active"},
    {"label":"Add Properties","href":"", "status":"active"},
    {"label":"Conditional Rendering","href":"", "status":"active"},
    {"label":"nexy modules system","href":"", "status":"active"},
]

SIDE_BAR = [
    {"caption":"BIBIN", "title":"Getting Started","href":"","items":GETTING_STARTED},
    {"caption":"FBR", "title":"File based routing","href":"","items":FB_ROUTERS},
    {"caption":"UI Components", "title":"Describing the UI","href":"","items":COMPONENTS}
]

