
from .settings import *

# Configuración exclusiva para pruebas automatizadas.
# Evita depender del manifiesto de collectstatic.

STORAGES = {
    **STORAGES,
    "staticfiles": {
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
        ),
    },
}
