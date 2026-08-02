FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY backend ./backend
RUN pip install --no-cache-dir .
COPY scripts ./scripts
COPY data ./data
RUN mkdir -p uploads generated
CMD ["uvicorn", "careeros.main:app", "--host", "0.0.0.0", "--port", "8000"]
