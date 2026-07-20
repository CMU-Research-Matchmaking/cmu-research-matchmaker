# Two-stage build. Convention: the container is the unit of truth — ingestion
# and embedding run here at build time, and the FAISS index ships in the image.

FROM python:3.12-slim AS builder

# HF_HOME pins the embedding-model cache to a copyable path so the runtime
# stage can load the model without network access.
ENV HF_HOME=/opt/hf-cache \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

# CPU-only torch first: the default PyPI wheels bundle CUDA libraries
# (gigabytes) that this service never uses.
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ src/

# Data prep: writes /build/data/{index.faiss,profiles.json}. Real OpenAlex
# ingestion replaces the fake records inside this entrypoint, not here.
RUN python -m src.ingest.build_index /build/data


FROM python:3.12-slim

ENV DATA_DIR=/app/data \
    HF_HOME=/opt/hf-cache

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /opt/hf-cache /opt/hf-cache
COPY --from=builder /build/data /app/data
COPY src/ src/

EXPOSE 8000
CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
