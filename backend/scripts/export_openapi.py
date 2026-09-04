import yaml
from fastapi.openapi.utils import get_openapi
from services.api.main import app

def export_openapi():
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
    )
    with open("../contract/openapi.yaml", "w") as f:
        yaml.dump(openapi_schema, f, default_flow_style=False, sort_keys=False)

if __name__ == "__main__":
    export_openapi()
