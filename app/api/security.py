
# app/api/security.py

import secrets

from fastapi import Depends, Header, HTTPException

from app.api.dependencies import Settings, get_settings


def verify_api_key(
    x_api_key: str | None = Header(default=None),
    settings: Settings = Depends(get_settings)
):
    # Check whether the API key was provided.
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="API key is missing"
        )

    # Securely compare the supplied key with the expected key.
    if not secrets.compare_digest(
        x_api_key,
        settings.expected_api_key
    ):
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )

    return x_api_key
