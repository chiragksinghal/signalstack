FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir sqlalchemy psycopg[binary] requests beautifulsoup4 feedparser

COPY src /app/src

CMD ["python", "-m", "src.run"]


