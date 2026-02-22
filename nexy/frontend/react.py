from nexy.core.models import FFModel

def react() -> FFModel:
    return FFModel(
        name="react",
        render="",
        extension=["jsx", "tsx"]
    )
