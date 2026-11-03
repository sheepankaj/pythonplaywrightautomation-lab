import os


def get_api_auth_headers() -> dict:
    return {"api_key": os.environ.get("PETSTORE_API_KEY", "")}
