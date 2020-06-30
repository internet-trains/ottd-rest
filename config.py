import os
from libottdadmin2.constants import NETWORK_ADMIN_PORT

basedir = os.path.abspath(os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

class Config(object):
    OTTD_GS_HOST = os.environ.get("OTTD_GS_HOST", "127.0.0.1")
    OTTD_GS_PORT = int(os.environ.get("OTTD_GS_PORT", NETWORK_ADMIN_PORT))
    OTTD_GS_PASSWORD = os.environ.get("OTTD_GS_PASSWORD", "password")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    OPENAPI_VERSION = "3.0.2"
    OPENAPI_JSON_PATH = "api.json"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_REDOC_PATH = "/redoc"
    OPENAPI_REDOC_URL = (
        "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"
    )
    OPENAPI_SWAGGER_UI_PATH = "/swagger-ui"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    NO_WORKER = bool(os.environ.get("NO_WORKER", False))



config = Config()