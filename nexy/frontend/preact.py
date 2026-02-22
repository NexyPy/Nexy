from nexy.core.models import FFModel

def preact() -> FFModel:
    return FFModel(
        name="preact",
        render="",
        extension=["jsx", "tsx"]
    )
