from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

from src.constants import API_KEY_NAME, API_KEY


async def get_api_key(
    api_key_header: str = Security(APIKeyHeader(name=API_KEY_NAME, auto_error=True)),
):
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(status_code=403, detail="API key is not valid")
