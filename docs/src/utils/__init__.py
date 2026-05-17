import os
is_vercel = os.environ.get('VERCEL')

def resolve_url(src, srcset=None):
    if is_vercel and src.startswith("/public/"):
    # On nettoie le chemin : on remplace "/public/" par "/"
        src = src.replace("/public/", "/")
        srcset = srcset.replace("/public/", "/") if srcset else None

    return src, srcset