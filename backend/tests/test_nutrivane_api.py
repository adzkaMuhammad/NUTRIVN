"""Backend tests for NutriVane API."""
import os
import base64
import io
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://bumbu-genius-1.preview.emergentagent.com').rstrip('/')
API = f"{BASE_URL}/api"


@pytest.fixture(scope="module")
def client():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


# --- Home ---
def test_home(client):
    r = client.get(f"{API}/home", timeout=30)
    assert r.status_code == 200
    d = r.json()
    for k in ["greeting_name", "streak_days", "plates_recognized", "featured", "moods", "picks"]:
        assert k in d
    assert len(d["moods"]) == 4
    assert len(d["picks"]) == 3
    assert d["featured"].get("slug")


# --- Categories ---
def test_categories(client):
    r = client.get(f"{API}/categories", timeout=30)
    assert r.status_code == 200
    keys = {c["key"] for c in r.json()}
    assert {"semua", "menu-utama", "perut-nyaman", "menu-cepat"}.issubset(keys)


# --- Recipes list ---
def test_recipes_list(client):
    r = client.get(f"{API}/recipes", timeout=30)
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 3
    slugs = {x["slug"] for x in data}
    assert {"rendang", "sayur-sop-ayam", "nasi-goreng"} == slugs


@pytest.mark.parametrize("cat,expected_slug", [
    ("menu-utama", "rendang"),
    ("perut-nyaman", "sayur-sop-ayam"),
    ("menu-cepat", "nasi-goreng"),
])
def test_recipes_filter(client, cat, expected_slug):
    r = client.get(f"{API}/recipes", params={"category": cat}, timeout=30)
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["slug"] == expected_slug


def test_recipes_search(client):
    r = client.get(f"{API}/recipes", params={"q": "rendang"}, timeout=30)
    assert r.status_code == 200
    data = r.json()
    assert any(x["slug"] == "rendang" for x in data)


# --- Recipe detail ---
@pytest.mark.parametrize("slug", ["rendang", "sayur-sop-ayam", "nasi-goreng"])
def test_recipe_detail(client, slug):
    r = client.get(f"{API}/recipes/{slug}", timeout=30)
    assert r.status_code == 200
    d = r.json()
    assert d["slug"] == slug
    assert "sources" in d and d["source_count"] == len(d["sources"])
    assert len(d["spices"]) > 0
    for s in d["spices"]:
        assert "avg" in s and "unit" in s and "pct" in s
        assert 0 <= s["pct"] <= 100


def test_recipe_detail_404(client):
    r = client.get(f"{API}/recipes/not-a-real-slug", timeout=30)
    assert r.status_code == 404


# --- Moods ---
def test_moods_list(client):
    r = client.get(f"{API}/moods", timeout=30)
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 4


def test_mood_detail(client):
    r = client.get(f"{API}/moods/berenergi", timeout=30)
    assert r.status_code == 200
    d = r.json()
    assert d["key"] == "berenergi"
    assert len(d["recipes"]) >= 1


def test_mood_404(client):
    r = client.get(f"{API}/moods/unknown", timeout=30)
    assert r.status_code == 404


# --- Insight (AI + cache) ---
def test_insight_and_cache(client):
    r1 = client.get(f"{API}/insight/rendang", timeout=120)
    assert r1.status_code == 200
    d1 = r1.json()
    assert d1["text"] and len(d1["text"]) > 5
    r2 = client.get(f"{API}/insight/rendang", timeout=30)
    assert r2.status_code == 200
    d2 = r2.json()
    assert d2.get("cached") is True


def test_insight_404(client):
    r = client.get(f"{API}/insight/nope", timeout=30)
    assert r.status_code == 404


# --- Scan ---
def test_scan_with_measure(client):
    r = client.post(f"{API}/scan", json={"benchmark_slug": "rendang", "measure": True}, timeout=120)
    assert r.status_code == 200
    d = r.json()
    assert d["menu_name"]
    assert d.get("insight")
    assert "spices" in d and len(d["spices"]) > 0


def test_scan_without_measure(client):
    r = client.post(f"{API}/scan", json={"benchmark_slug": "nasi-goreng", "measure": False}, timeout=120)
    assert r.status_code == 200
    d = r.json()
    assert "spices" not in d
    assert d.get("insight")


def test_scan_invalid_slug(client):
    r = client.post(f"{API}/scan", json={"benchmark_slug": "nope", "measure": True}, timeout=30)
    assert r.status_code == 404


def _make_jpeg_b64():
    """Build a tiny JPEG with real visual features (colored stripes + noise)."""
    try:
        from PIL import Image
        import random
        img = Image.new("RGB", (120, 120))
        px = img.load()
        for y in range(120):
            for x in range(120):
                base = (x * 2 % 255, y * 2 % 255, (x + y) % 255)
                noise = random.randint(0, 20)
                px[x, y] = (min(255, base[0] + noise), min(255, base[1] + noise), min(255, base[2] + noise))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=80)
        return base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return None


def test_scan_with_image(client):
    b64 = _make_jpeg_b64()
    if not b64:
        pytest.skip("PIL not available")
    r = client.post(f"{API}/scan", json={"benchmark_slug": "rendang", "measure": False, "image_base64": b64}, timeout=180)
    assert r.status_code == 200
    d = r.json()
    assert d.get("vision_note") and len(d["vision_note"]) > 5


# --- Stats ---
def test_stats(client):
    r = client.get(f"{API}/stats", timeout=30)
    assert r.status_code == 200
    d = r.json()
    assert "plates_recognized" in d and "streak_days" in d
