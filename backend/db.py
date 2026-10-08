import json
import logging
import os
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from data import CATEGORIES, MOODS, RECIPES

logger = logging.getLogger("nutrivane.db")
SCHEMA_SQL = Path(__file__).resolve().parent.parent / "supabase" / "schema.sql"


def _build_engine():
    parts = urlsplit(os.environ["DATABASE_URL"])
    scheme = parts.scheme
    if scheme in ("postgres", "postgresql"):
        scheme = "postgresql+asyncpg"
    query = dict(parse_qsl(parts.query))
    ssl_mode = query.pop("sslmode", None) or query.pop("ssl", None)
    url = urlunsplit((scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))
    local = parts.hostname in ("localhost", "127.0.0.1")
    connect_args = {"statement_cache_size": 0}  # aman untuk Supabase pooler (pgbouncer)
    if ssl_mode not in (None, "disable") or not local:
        connect_args["ssl"] = "require"
    return create_async_engine(url, pool_pre_ping=True, pool_size=5, max_overflow=10, connect_args=connect_args)


engine = _build_engine()
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        raw = await conn.get_raw_connection()
        await raw.driver_connection.execute(SCHEMA_SQL.read_text())
    await seed()


async def seed():
    async with SessionLocal() as s:
        for i, c in enumerate(CATEGORIES):
            await s.execute(text(
                "insert into categories(key,label,sort_order) values(:key,:label,:i) "
                "on conflict (key) do update set label=excluded.label, sort_order=excluded.sort_order"
            ), {**c, "i": i})
        for i, r in enumerate(RECIPES):
            await s.execute(text(
                "insert into recipes(slug,name,category,category_label,porsi,image,tagline,flavor_note,spices,sources,sort_order,updated_at) "
                "values(:slug,:name,:category,:category_label,:porsi,:image,:tagline,:flavor_note,"
                "cast(:spices as jsonb),cast(:sources as jsonb),:i,now()) "
                "on conflict (slug) do update set name=excluded.name, category=excluded.category, "
                "category_label=excluded.category_label, porsi=excluded.porsi, image=excluded.image, "
                "tagline=excluded.tagline, flavor_note=excluded.flavor_note, spices=excluded.spices, "
                "sources=excluded.sources, sort_order=excluded.sort_order, updated_at=now()"
            ), {**r, "spices": json.dumps(r["spices"]), "sources": json.dumps(r["sources"]), "i": i})
        for i, m in enumerate(MOODS):
            await s.execute(text(
                "insert into moods(key,label,emoji,subtitle,question,helper,recipe_slugs,sort_order) "
                "values(:key,:label,:emoji,:subtitle,:question,:helper,cast(:recipe_slugs as jsonb),:i) "
                "on conflict (key) do update set label=excluded.label, emoji=excluded.emoji, subtitle=excluded.subtitle, "
                "question=excluded.question, helper=excluded.helper, recipe_slugs=excluded.recipe_slugs, sort_order=excluded.sort_order"
            ), {**m, "recipe_slugs": json.dumps(m["recipe_slugs"]), "i": i})
        await s.commit()
    logger.info("seeded %d categories, %d recipes, %d moods", len(CATEGORIES), len(RECIPES), len(MOODS))


def row_dict(row) -> dict:
    d = dict(row._mapping)
    for k, v in d.items():
        if isinstance(v, str) and k in ("spices", "sources", "recipe_slugs"):
            d[k] = json.loads(v)
    return d
