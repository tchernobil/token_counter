# Dockerfile & CI/CD Templates

Reference templates for container images and GitHub Actions build pipelines.
See `knowledge/generic/infrastructure/kubernetes_workload_guidelines.md` for runtime constraints.

---

## Multi-Stage Dockerfile — Django (Python)

```dockerfile
# ─── Stage 1: dependency builder ──────────────────────────────
FROM python:3.13-slim-trixie AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# ─── Stage 2: runtime ─────────────────────────────────────────
FROM python:3.13-slim-trixie AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --gid 1001 app && useradd --uid 1001 --gid app --no-create-home app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app
COPY --chown=app:app . .
COPY --from=builder --chown=app:app /build/.venv /app/.venv

USER app
EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

---

## Multi-Stage Dockerfile — Nuxt (Node.js)

```dockerfile
# ─── Stage 1: build ───────────────────────────────────────────
FROM node:22-slim AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --ignore-scripts
COPY . .
RUN npm run build

# ─── Stage 2: runtime ─────────────────────────────────────────
FROM node:22-slim AS runtime

RUN groupadd --gid 1001 app && useradd --uid 1001 --gid app --no-create-home app

WORKDIR /app
COPY --from=builder --chown=app:app /app/.output ./.output

USER app
EXPOSE 3000
CMD ["node", ".output/server/index.mjs"]
```

---

## .dockerignore

```
.git
.github
**/__pycache__
**/*.pyc
**/*.pyo
.pytest_cache
.coverage
htmlcov/
.env
.env.*
*.log
.venv/
.uv/
node_modules/
dist/
.nuxt/
README.md
docs/
```

---

## GitHub Actions — Build & Push to GHCR

```yaml
name: Build and Push Image

on:
  push:
    branches: [main, develop]
    tags: ['v*.*.*']
  pull_request:
    branches: [main, develop]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - uses: actions/checkout@v4

      - name: Set up QEMU
        uses: docker/setup-qemu-action@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to GHCR
        if: github.event_name != 'pull_request'
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha,prefix=sha-,format=short
            type=raw,value=latest,enable=${{ github.ref == 'refs/heads/main' }}

      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

---

## Adding Docker Hub as a Second Registry

```yaml
      - name: Log in to Docker Hub
        if: github.event_name != 'pull_request'
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
```

Extend `images:` in `metadata-action`:
```yaml
          images: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
            docker.io/orgname/imagename
```

---

## Build-Time Secrets (never use ARG for tokens)

```yaml
      - name: Build with secret
        uses: docker/build-push-action@v6
        with:
          secrets: |
            pypi_token=${{ secrets.PYPI_TOKEN }}
```

```dockerfile
RUN --mount=type=secret,id=pypi_token \
    pip install --index-url "https://$(cat /run/secrets/pypi_token)@private.pypi.org/simple/" mypackage
```

---

## Tagging Strategy

| Trigger | Tag | Use |
| :--- | :--- | :--- |
| Push to `main` | `latest` | Production |
| Push to `develop` | `develop` | Staging |
| Git tag `v1.2.3` | `1.2.3`, `1.2` | Pinned release |
| Any push | `sha-abc1234` | Traceability / rollback |

---

## Multi-Architecture: Architecture-Dependent Binary Downloads

```dockerfile
ARG TARGETARCH
RUN curl -fsSL "https://releases.example.com/tool_${TARGETARCH}.tar.gz" | tar xz
```

Do **not** hardcode `FROM --platform=linux/amd64` in the final runtime stage — let `buildx` handle platform targeting.
