# Local development

## Backend

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env
alembic upgrade head
uvicorn kall.main:app --reload
```

API documentation is available at `http://localhost:8000/docs`.

## Web

```bash
cd apps/web
npm install
npm run dev
```

The web client runs at `http://localhost:3000`.

## Checks

```bash
ruff check .
python -m compileall -q backend tests scripts migrations
pytest --cov=kall
cd apps/web && npm run build
```

## Production notes

Set `APP_ENV=production`, `AUTO_CREATE_TABLES=false`, use PostgreSQL, and run
`alembic upgrade head` during deployment. Production startup refuses the default secret,
SQLite, or a missing sensitive-data encryption key.
