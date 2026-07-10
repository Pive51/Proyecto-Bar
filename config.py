# config.py
import os

CONNECTION_STRING = os.getenv("DATABASE_URL")

if not CONNECTION_STRING:
    raise ValueError(
        "La variable de entorno DATABASE_URL no está configurada."
    )