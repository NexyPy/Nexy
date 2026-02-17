from fastapi.responses import JSONResponse
from nexy.decorators import useRoute, UseResponse


@useRoute(
    name="qs-custom",
    tags=["demo"],
)
@UseResponse(
    status_code=201,
)
def POST():
    return JSONResponse(
        {"message": "POST done"},
        headers={"X-Nexy-Route": "custom"},
    )
