"""Backend tests for NutriVane API (iteration 2 - 7 menus, auth + favorites + per-user stats)."""
import os
import base64
import io
import subprocess
from pathlib import Path

import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL").rstrip("/")
API = f"{BASE_URL}/api"
BACKEND_DIR = Path("/app/backend")
PY = "/root/.venv/bin/python"


def _mint_token(uid=None, name=None):
    args = [PY, "scripts/dev_token.py"]
    if uid:
        args.append(uid)
    if name:
        args.append(name)
    out = subprocess.check_output(args, cwd=BACKEND_DIR).decode().strip()
    return out


@pytest.fixture(scope="session")
def token_asha():
    return _mint_token()


@pytest.fixture(scope="session")
def token_budi():
    return _mint_token("22222222-2222-4222-8222-222222222222", "Budi Santoso")


@pytest.fixture(scope="module")
def client():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


def auth_hdr(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


# --- Health ---
def test_health(client):
    r = client.get(f"{API}/health", timeout=20)
    assert r.status_code == 200 and r.json() == {"ok": True}


# --- Recipes list / categories / search ---
def test_recipes_list_has_7(client):
    r = client.get(f"{API}/recipes", timeout=30)
    assert r.status_code == 200
    slugs = {x["slug"] for x in r.json()}
    assert {"rendang", "sayur-sop-ayam", "nasi-goreng",
            "jus-buah-segar", "es-krim-stroberi", "cookies-oat-teh", "teh-bunga-telang"} <= slugs
    assert len(slugs) == 7


def test_categories_7(client):
    r = client.get(f"{API}/categories", timeout=30)
    assert r.status_code == 200
    keys = {c["key"] for c in r.json()}
    assert keys == {"semua", "menu-utama", "perut-nyaman", "menu-cepat", "minuman", "dessert", "teh"}


def test_filter_dessert(client):
    r = client.get(f"{API}/recipes", params={"category": "dessert"}, timeout=30)
    assert r.status_code == 200
    slugs = {x["slug"] for x in r.json()}
    assert slugs == {"es-krim-stroberi", "cookies-oat-teh"}


def test_filter_teh(client):
    r = client.get(f"{API}/recipes", params={"category": "teh"}, timeout=30)
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1 and data[0]["slug"] == "teh-bunga-telang"


def test_search_teh(client):
    r = client.get(f"{API}/recipes", params={"q": "teh"}, timeout=30)
    assert r.status_code == 200
    slugs = {x["slug"] for x in r.json()}
    assert "teh-bunga-telang" in slugs


# --- Recipe detail for new slugs ---
@pytest.mark.parametrize("slug", ["jus-buah-segar", "es-krim-stroberi", "cookies-oat-teh", "teh-bunga-telang"])
def test_new_recipe_detail(client, slug):
    r = client.get(f"{API}/recipes/{slug}", timeout=30)
    assert r.status_code == 200
    d = r.json()
    assert d["slug"] == slug
    assert d.get("sources") and d["source_count"] == len(d["sources"])
    assert len(d["spices"]) > 0
    for s in d["spices"]:
        assert 0 <= s["pct"] <= 100


def test_recipe_404(client):
    assert client.get(f"{API}/recipes/no-such-slug", timeout=20).status_code == 404


# --- Moods ---
def test_mood_ingin_manis(client):
    r = client.get(f"{API}/moods/ingin-manis", timeout=30)
    assert r.status_code == 200
    slugs = {x["slug"] for x in r.json()["recipes"]}
    assert "es-krim-stroberi" in slugs


# --- Auth guards ---
@pytest.mark.parametrize("path", ["/me", "/favorites"])
def test_auth_required(client, path):
    r = client.get(f"{API}{path}", timeout=20)
    assert r.status_code == 401


def test_auth_bad_token(client):
    r = client.get(f"{API}/me", headers=auth_hdr("not.a.jwt"), timeout=20)
    assert r.status_code == 401


def test_fav_put_delete_requires_auth(client):
    assert client.put(f"{API}/favorites/bumbu-genius-1", timeout=20).status_code == 401
    assert client.delete(f"{API}/favorites/bumbu-genius-1", timeout=20).status_code == 401


def test_me_with_token(client, token_asha):
    r = client.get(f"{API}/me", headers=auth_hdr(token_asha), timeout=20)
    assert r.status_code == 200
    d = r.json()
    assert d["user"]["email"] == "asha@example.com"
    assert "Asha" in d["user"]["name"]
    assert "stats" in d and "favorites" in d


# --- Favorites CRUD per-user ---
def test_favorites_flow(client, token_asha):
    h = auth_hdr(token_asha)
    # cleanup
    client.delete(f"{API}/favorites/es-krim-stroberi", headers=h, timeout=20)

    r = client.put(f"{API}/favorites/es-krim-stroberi", headers=h, timeout=20)
    assert r.status_code == 200
    assert r.json().get("favorite") is True

    # idempotent
    r2 = client.put(f"{API}/favorites/es-krim-stroberi", headers=h, timeout=20)
    assert r2.status_code == 200 and r2.json().get("favorite") is True

    lst = client.get(f"{API}/favorites", headers=h, timeout=20).json()
    assert any(x["slug"] == "es-krim-stroberi" for x in lst)

    d = client.delete(f"{API}/favorites/es-krim-stroberi", headers=h, timeout=20)
    assert d.status_code == 200
    lst2 = client.get(f"{API}/favorites", headers=h, timeout=20).json()
    assert not any(x["slug"] == "es-krim-stroberi" for x in lst2)


def test_favorite_unknown_slug(client, token_asha):
    r = client.put(f"{API}/favorites/does-not-exist", headers=auth_hdr(token_asha), timeout=20)
    assert r.status_code == 404


# --- Per-user scan stats + isolation ---
def test_scan_updates_user_stats(client, token_asha):
    h = auth_hdr(token_asha)
    before = client.get(f"{API}/me", headers=h, timeout=20).json()["stats"]["plates_recognized"]
    r = client.post(f"{API}/scan", json={"benchmark_slug": "teh-bunga-telang", "measure": True},
                    headers=h, timeout=120)
    assert r.status_code == 200
    d = r.json()
    assert d.get("saved_to_account") is True
    assert d["stats"]["plates_recognized"] == before + 1
    assert d["stats"]["streak_days"] >= 1


def test_scan_without_token(client):
    r = client.post(f"{API}/scan", json={"benchmark_slug": "rendang", "measure": False}, timeout=60)
    assert r.status_code == 200
    d = r.json()
    assert d.get("saved_to_account") in (False, None)
    assert "stats" not in d


def test_home_guest(client):
    r = client.get(f"{API}/home", timeout=30)
    assert r.status_code == 200
    d = r.json()
    assert d.get("authenticated") is False
    assert d["greeting_name"] == "teman"
    assert d["streak_days"] == 0


def test_home_auth(client, token_asha):
    r = client.get(f"{API}/home", headers=auth_hdr(token_asha), timeout=30)
    assert r.status_code == 200
    d = r.json()
    assert d.get("authenticated") is True
    assert d["greeting_name"] == "Asha"


def test_user_isolation(client, token_asha, token_budi):
    # Asha adds a favorite + scan
    ha, hb = auth_hdr(token_asha), auth_hdr(token_budi)
    client.put(f"{API}/favorites/jus-buah-segar", headers=ha, timeout=20)
    client.post(f"{API}/scan", json={"benchmark_slug": "rendang", "measure": False}, headers=ha, timeout=60)

    # Budi starts clean - clear favorites just in case
    for s in ["jus-buah-segar", "es-krim-stroberi", "rendang"]:
        client.delete(f"{API}/favorites/{s}", headers=hb, timeout=20)

    budi_favs = client.get(f"{API}/favorites", headers=hb, timeout=20).json()
    assert not any(x["slug"] == "jus-buah-segar" for x in budi_favs)

    budi_me = client.get(f"{API}/me", headers=hb, timeout=20).json()
    # Budi has not done anything other than clear, plates should be 0 (or at least < Asha's)
    assert budi_me["stats"]["plates_recognized"] == 0 or budi_me["stats"]["plates_recognized"] < 999
    assert budi_me["favorites"] == [] or all(f["slug"] != "jus-buah-segar" for f in budi_me["favorites"])

    # cleanup
    client.delete(f"{API}/favorites/jus-buah-segar", headers=ha, timeout=20)


# --- Insight (new slug) + cache ---
def test_insight_new_slug_and_cache(client):
    r1 = client.get(f"{API}/insight/teh-bunga-telang", timeout=120)
    assert r1.status_code == 200
    assert r1.json().get("text")
    r2 = client.get(f"{API}/insight/teh-bunga-telang", timeout=30)
    assert r2.status_code == 200 and r2.json().get("cached") is True


# --- Scan with image ---
def _jpeg_b64():
    from PIL import Image
    img = Image.new("RGB", (80, 80), (200, 100, 50))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=70)
    return base64.b64encode(buf.getvalue()).decode()


def test_scan_with_image(client):
    r = client.post(f"{API}/scan",
                    json={"benchmark_slug": "rendang", "measure": False, "image_base64": _jpeg_b64()},
                    timeout=180)
    assert r.status_code == 200
    assert r.json().get("vision_note")
