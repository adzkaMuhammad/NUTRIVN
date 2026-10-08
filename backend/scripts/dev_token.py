"""Buat JWT uji (HS256) yang meniru access token Supabase — hanya untuk SUPABASE_JWT_MODE=legacy (dev)."""
import os
import sys
import time
from pathlib import Path

import jwt
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

uid = sys.argv[1] if len(sys.argv) > 1 else "11111111-1111-4111-8111-111111111111"
name = sys.argv[2] if len(sys.argv) > 2 else "Asha Pratiwi"
now = int(time.time())
claims = {
    "sub": uid, "aud": "authenticated", "role": "authenticated",
    "iss": f"{os.environ['SUPABASE_URL'].rstrip('/')}/auth/v1",
    "email": f"{name.split()[0].lower()}@example.com",
    "user_metadata": {"full_name": name, "avatar_url": ""},
    "iat": now, "exp": now + 60 * 60 * 24,
}
print(jwt.encode(claims, os.environ["SUPABASE_JWT_SECRET"], algorithm="HS256"))
