import logging
import os
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient

logger = logging.getLogger("nutrivane.auth")

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
JWT_MODE = os.environ.get("SUPABASE_JWT_MODE", "jwks")
JWT_SECRET = os.environ.get("SUPABASE_JWT_SECRET")
ISSUER = f"{SUPABASE_URL}/auth/v1"

_jwks = PyJWKClient(f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json", cache_keys=True) if (SUPABASE_URL and JWT_MODE == "jwks") else None
bearer = HTTPBearer(auto_error=False)


def decode_token(token: str) -> dict:
    if JWT_MODE == "legacy":
        if not JWT_SECRET:
            raise RuntimeError("SUPABASE_JWT_SECRET wajib diisi untuk SUPABASE_JWT_MODE=legacy")
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"], audience="authenticated", issuer=ISSUER)
    if not _jwks:
        raise RuntimeError("SUPABASE_URL belum dikonfigurasi")
    key = _jwks.get_signing_key_from_jwt(token).key
    return jwt.decode(token, key, algorithms=["RS256", "ES256"], audience="authenticated", issuer=ISSUER)


def claims_to_user(claims: dict) -> dict:
    meta = claims.get("user_metadata") or {}
    email = claims.get("email") or meta.get("email")
    name = meta.get("full_name") or meta.get("name") or (email.split("@")[0] if email else "Pengguna")
    return {"id": claims["sub"], "email": email, "name": name, "avatar_url": meta.get("avatar_url") or meta.get("picture")}


async def optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer)) -> Optional[dict]:
    if not credentials or credentials.scheme.lower() != "bearer":
        return None
    try:
        claims = decode_token(credentials.credentials)
    except Exception as e:
        logger.info("token ditolak: %s", e)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token tidak valid atau kedaluwarsa",
                            headers={"WWW-Authenticate": "Bearer"})
    if not claims.get("sub"):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token tanpa subject")
    return claims_to_user(claims)


async def require_user(user: Optional[dict] = Depends(optional_user)) -> dict:
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Silakan masuk terlebih dahulu",
                            headers={"WWW-Authenticate": "Bearer"})
    return user
