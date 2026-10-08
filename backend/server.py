from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone

from data import RECIPES, MOODS, CATEGORIES

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', '')
INSIGHT_PROVIDER = os.environ.get('INSIGHT_MODEL_PROVIDER', 'gemini')
INSIGHT_MODEL = os.environ.get('INSIGHT_MODEL_NAME', 'gemini-3-flash-preview')
VISION_PROVIDER = os.environ.get('VISION_MODEL_PROVIDER', 'gemini')
VISION_MODEL = os.environ.get('VISION_MODEL_NAME', 'gemini-3.1-pro-preview')

app = FastAPI(title="NutriVane API")
api_router = APIRouter(prefix="/api")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("nutrivane")

RECIPE_BY_SLUG = {r["slug"]: r for r in RECIPES}


# ----------------------------- Models -----------------------------
class ScanRequest(BaseModel):
    benchmark_slug: str
    measure: bool = False
    image_base64: Optional[str] = None


class InsightRequest(BaseModel):
    slug: str


# ----------------------------- AI helpers -----------------------------
async def generate_insight_text(recipe: dict) -> str:
    """Simple, cost-efficient AI (standard model) for a short flavor insight."""
    spice_line = ", ".join(f"{s['name']} {s['avg']}{s['unit']}" for s in recipe["spices"][:5])
    fallback = (
        f"Profil rasa {recipe['name'].lower()} didominasi {recipe['spices'][0]['name'].lower()} "
        f"(rata-rata {recipe['spices'][0]['avg']}{recipe['spices'][0]['unit']} dari {len(recipe['sources'])} sumber resep). "
        f"Gunakan angka ini sebagai panduan, bukan takaran mutlak."
    )
    if not EMERGENT_LLM_KEY:
        return fallback
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"insight-{recipe['slug']}",
            system_message=(
                "Kamu asisten kuliner NutriVane. Jawab dalam Bahasa Indonesia yang hangat dan singkat "
                "(maksimal 2 kalimat). Jelaskan karakter rasa dari rata-rata bumbu, tanpa menyuruh atau menghakimi."
            ),
        ).with_model(INSIGHT_PROVIDER, INSIGHT_MODEL)
        prompt = (
            f"Menu: {recipe['name']}. Catatan rasa: {recipe['flavor_note']}. "
            f"Rata-rata bumbu dominan dari {len(recipe['sources'])} sumber resep: {spice_line}. "
            f"Tulis 2 kalimat insight singkat soal profil rasanya."
        )
        resp = await chat.send_message(UserMessage(text=prompt))
        text = (resp or "").strip()
        return text or fallback
    except Exception as e:
        logger.warning(f"insight AI failed, using fallback: {e}")
        return fallback


async def analyze_food_image(image_base64: str) -> str:
    """Stronger AI (vision model) only when the user actually uploads a photo."""
    if not EMERGENT_LLM_KEY:
        return "Analisis foto butuh koneksi AI. Untuk beta, pilih menu benchmark di bawah."
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id="scan-vision",
            system_message=(
                "Kamu asisten NutriVane. Lihat foto makanan dan jawab Bahasa Indonesia singkat (2 kalimat): "
                "sebutkan kemungkinan nama hidangannya dan bumbu/rempah yang kemungkinan dominan. "
                "Jika tidak yakin, katakan dengan jujur."
            ),
        ).with_model(VISION_PROVIDER, VISION_MODEL)
        clean = image_base64.split(",", 1)[-1] if image_base64.startswith("data:") else image_base64
        msg = UserMessage(
            text="Makanan apa ini dan bumbu apa yang mungkin dominan?",
            file_contents=[ImageContent(image_base64=clean)],
        )
        resp = await chat.send_message(msg)
        return (resp or "").strip() or "Belum bisa mengenali makanan ini dengan yakin."
    except Exception as e:
        logger.warning(f"vision AI failed: {e}")
        return "Belum bisa menganalisis foto saat ini. Coba lagi atau pilih menu benchmark."


# ----------------------------- Public data endpoints -----------------------------
def recipe_card(r: dict) -> dict:
    return {
        "slug": r["slug"], "name": r["name"], "category": r["category"],
        "category_label": r["category_label"], "porsi": r["porsi"], "image": r["image"],
        "tagline": r["tagline"], "source_count": len(r["sources"]),
    }


@api_router.get("/")
async def root():
    return {"app": "NutriVane", "status": "ok"}


@api_router.get("/home")
async def home():
    now = datetime.now(timezone.utc)
    hour = now.hour
    part = "pagi" if hour < 11 else ("siang" if hour < 15 else ("sore" if hour < 19 else "malam"))
    plates = await db.scans.count_documents({})
    return {
        "date": now.strftime("%Y-%m-%d"),
        "part_of_day": part,
        "greeting_name": "Asha",
        "headline": "Makan lebih paham, mulai dari satu piring.",
        "subhead": f"Selamat datang kembali, Asha. Yuk kenali isi piringmu {part} ini.",
        "streak_days": 4,
        "plates_recognized": 12 + plates,
        "weekly_delta": 2,
        "featured": {
            "badge": "Beta insight",
            "title": "Apa yang ada di balik rasa rendangmu?",
            "body": "Bandingkan bumbu dari banyak resep, lalu pilih dengan lebih yakin.",
            "slug": "rendang",
        },
        "moods": [{"key": m["key"], "label": m["label"], "emoji": m["emoji"], "subtitle": m["subtitle"]} for m in MOODS],
        "picks": [recipe_card(r) for r in RECIPES],
    }


@api_router.get("/categories")
async def categories():
    return CATEGORIES


@api_router.get("/recipes")
async def list_recipes(category: Optional[str] = None, q: Optional[str] = None):
    items = RECIPES
    if category and category != "semua":
        items = [r for r in items if r["category"] == category]
    if q:
        ql = q.lower()
        items = [r for r in items if ql in r["name"].lower() or ql in r["tagline"].lower()]
    return [recipe_card(r) for r in items]


@api_router.get("/recipes/{slug}")
async def recipe_detail(slug: str):
    r = RECIPE_BY_SLUG.get(slug)
    if not r:
        raise HTTPException(status_code=404, detail="Menu tidak ditemukan")
    max_avg = max(s["avg"] for s in r["spices"]) or 1
    spices = [{**s, "pct": round(s["avg"] / max_avg * 100)} for s in r["spices"]]
    return {
        "slug": r["slug"], "name": r["name"], "category": r["category"],
        "category_label": r["category_label"], "porsi": r["porsi"], "image": r["image"],
        "tagline": r["tagline"], "flavor_note": r["flavor_note"],
        "source_count": len(r["sources"]), "sources": r["sources"], "spices": spices,
    }


@api_router.get("/moods")
async def list_moods():
    return [{"key": m["key"], "label": m["label"], "emoji": m["emoji"],
             "subtitle": m["subtitle"], "question": m["question"], "helper": m["helper"]} for m in MOODS]


@api_router.get("/moods/{key}")
async def mood_detail(key: str):
    m = next((x for x in MOODS if x["key"] == key), None)
    if not m:
        raise HTTPException(status_code=404, detail="Mood tidak ditemukan")
    recs = [recipe_card(RECIPE_BY_SLUG[s]) for s in m["recipe_slugs"] if s in RECIPE_BY_SLUG]
    return {"key": m["key"], "label": m["label"], "emoji": m["emoji"], "question": m["question"],
            "helper": m["helper"], "recipes": recs}


@api_router.get("/insight/{slug}")
async def get_insight(slug: str):
    r = RECIPE_BY_SLUG.get(slug)
    if not r:
        raise HTTPException(status_code=404, detail="Menu tidak ditemukan")
    cached = await db.insights.find_one({"slug": slug}, {"_id": 0})
    if cached and cached.get("text"):
        return {"slug": slug, "text": cached["text"], "cached": True}
    text = await generate_insight_text(r)
    await db.insights.update_one(
        {"slug": slug},
        {"$set": {"slug": slug, "text": text, "updated_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True,
    )
    return {"slug": slug, "text": text, "cached": False}


@api_router.post("/scan")
async def scan(req: ScanRequest):
    r = RECIPE_BY_SLUG.get(req.benchmark_slug)
    if not r:
        raise HTTPException(status_code=404, detail="Menu benchmark tidak ditemukan")

    result = {
        "benchmark_slug": r["slug"],
        "menu_name": r["name"],
        "category_label": r["category_label"],
        "image": r["image"],
        "measure_enabled": req.measure,
        "source_count": len(r["sources"]),
    }

    # Vision AI only runs when a real photo is attached (balanced AI usage).
    if req.image_base64:
        result["vision_note"] = await analyze_food_image(req.image_base64)
    else:
        result["vision_note"] = (
            f"Mode beta: menggunakan benchmark {r['name']}. Arahkan kamera ke makananmu "
            f"saat versi penuh tersedia."
        )

    # Spice meter (pure computation — no AI) only when the measure toggle is on.
    if req.measure:
        max_avg = max(s["avg"] for s in r["spices"]) or 1
        result["spices"] = [{**s, "pct": round(s["avg"] / max_avg * 100)} for s in r["spices"]]

    # Short flavor insight (cost-efficient standard AI, cached).
    cached = await db.insights.find_one({"slug": r["slug"]}, {"_id": 0})
    if cached and cached.get("text"):
        result["insight"] = cached["text"]
    else:
        text = await generate_insight_text(r)
        await db.insights.update_one(
            {"slug": r["slug"]},
            {"$set": {"slug": r["slug"], "text": text, "updated_at": datetime.now(timezone.utc).isoformat()}},
            upsert=True,
        )
        result["insight"] = text

    await db.scans.insert_one({
        "benchmark_slug": r["slug"], "measure": req.measure,
        "had_image": bool(req.image_base64),
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    return result


@api_router.get("/stats")
async def stats():
    plates = await db.scans.count_documents({})
    return {"plates_recognized": 12 + plates, "streak_days": 4, "weekly_delta": 2}


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await db.scans.create_index("created_at")
    await db.insights.create_index("slug", unique=True)
    logger.info("NutriVane API ready")


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
