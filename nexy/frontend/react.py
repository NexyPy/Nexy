from nexy.core.models import FFModel


source = """    import React from 'react';
    import ReactDOM from 'react-dom';
    """
def react()->FFModel:
    return FFModel(
        name="react",
        render=source,
        extension=["jsx", "tsx"]
    )
