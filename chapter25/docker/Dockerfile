# Multi-stage build: the "builder" stage installs dependencies into a virtualenv;
# the final stage copies ONLY that virtualenv + app code, not build tools,
# caches, or compilers -- meaningfully smaller and more secure final image.

FROM python:3.12-slim AS builder

WORKDIR /build
COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt


FROM python:3.12-slim

# Run as a non-root user -- a container running as root that gets compromised
# gives an attacker root inside the container; unnecessary risk for no benefit.
RUN useradd --create-home appuser
WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY app/ ./app/
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Healthcheck lets `docker ps` and orchestrators see container health directly,
# independent of readiness/liveness probes configured at the k8s/orchestrator level.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Gunicorn manages multiple Uvicorn worker PROCESSES (not just async tasks) --
# this is how you use multiple CPU cores, since a single Python process is
# still limited by the GIL for CPU-bound work.
CMD ["gunicorn", "app.main:app", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "-w", "4", \
     "-b", "0.0.0.0:8000", \
     "--graceful-timeout", "30", \
     "--timeout", "60"]
