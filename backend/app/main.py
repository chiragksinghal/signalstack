import os
from typing import Optional

from fastapi import FastAPI, Query
from sqlalchemy import create_engine, text

app = FastAPI(title="SignalStack API")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/health/db")
def health_db():
    """
    Checks that the API can connect to the database.
    """
    with engine.begin() as conn:
        val = conn.execute(text("SELECT 1")).scalar_one()
    return {"ok": True, "db": "ok", "value": val}

# Backwards-compatible alias (so nothing breaks if you already used /db_check somewhere)
@app.get("/db_check")
def db_check():
    return health_db()

@app.get("/items")
def list_items(
    q: Optional[str] = Query(default=None),
    page: int = 1,
    page_size: int = 20,
):
    """
    Returns items ingested by the worker, with simple search + pagination.
    """
    offset = (page - 1) * page_size

    params = {"limit": page_size, "offset": offset}
    where = ""
    if q and q.strip():
        where = "WHERE title ILIKE :q OR source ILIKE :q"
        params["q"] = f"%{q.strip()}%"

    sql = f"""
    SELECT id, source, title, url, published_at, fetched_at
    FROM items
    {where}
    ORDER BY published_at DESC NULLS LAST, fetched_at DESC
    LIMIT :limit OFFSET :offset
    """

    count_sql = f"SELECT COUNT(*) FROM items {where}"

    with engine.begin() as conn:
        rows = conn.execute(text(sql), params).mappings().all()
        total = conn.execute(text(count_sql), params).scalar_one()

    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "items": list(rows),
    }

