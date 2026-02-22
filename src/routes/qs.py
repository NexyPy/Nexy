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
    return ["ddd","eee"]
