# MotionScope backend: FastAPI + analysis pipeline (DIP-23).
# Build and run everything with:  docker compose up --build
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# libgl/libglib: needed by the opencv-python wheel that Ultralytics pulls in
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# CPU-only PyTorch keeps the image ~2 GB smaller than the default CUDA build
RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
COPY requirements.txt requirements-ml.txt ./
RUN pip install -r requirements.txt -r requirements-ml.txt

# Download the model weights at build time, so analysis needs no network (NFR-03)
RUN python -c "from ultralytics import YOLO; YOLO('yolo11n.pt')"

COPY src ./src
COPY config ./config
COPY docs/schemas ./docs/schemas

RUN useradd --create-home --uid 1000 app && mkdir -p /data && chown -R app /data /app
USER app

ENV MOVDET_DATA_DIR=/data \
    MOVDET_PROCESSOR=pipeline \
    YOLO_OFFLINE=1

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health')"
CMD ["uvicorn", "src.backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
