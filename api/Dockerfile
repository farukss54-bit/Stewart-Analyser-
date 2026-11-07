# Stewart Asit-Baz Analizi: API imajı (FastAPI)
# Derleme bağlamı depo köküdür (docker-compose.yml bunu ayarlar). Streamlit imajı kökteki Dockerfile'dır.
FROM python:3.12-slim

WORKDIR /app

# Yalnızca çalışma zamanı bağımlılıkları (Streamlit, Plotly, test araçları yok)
COPY api/requirements-runtime.txt api/requirements-runtime.txt
RUN pip install --no-cache-dir -r api/requirements-runtime.txt

# API'nin ihtiyaç duyduğu dosyalar: hesaplama çekirdeği ve doğrulama + API katmanı
COPY __init__.py core.py constants.py validation.py services.py logger.py ./
COPY api ./api

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

ENV PYTHONUNBUFFERED=1

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=3)" || exit 1

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
