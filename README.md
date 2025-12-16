# SignalStack

Small multi-service demo app that pulls RSS items into Postgres, serves them through a FastAPI backend, and displays them in a Next.js frontend.

The goal of this project was to practice wiring together a worker, API, database, and frontend using Docker Compose.

## What runs
- Postgres – stores ingested items
- Worker – fetches RSS feeds and inserts items into the database
- FastAPI backend – exposes read-only endpoints with search and pagination
- Next.js frontend – displays a live feed backed by the API

Data flow:
worker → Postgres → FastAPI → Next.js

## Run locally

```bash
docker compose up --build
```
Open:
- Frontend: http://localhost:3000
- API health: http://localhost:8000/health
- DB health: http://localhost:8000/health/db

Stop everything with:
```bash
docker compose down
```

## API endpoints
- GET /items
 - q – optional search string (matches title or source)
 - page – page number
 - page_size – items per page
- GET /health
- GET /health/db

## Notes
- Services use Docker healthchecks to avoid startup race conditions.
- Database data is persisted using a named Docker volume.
- The frontend talks to the API via an environment variable (NEXT_PUBLIC_API_BASE).