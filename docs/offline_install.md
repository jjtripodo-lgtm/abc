# Offline Install Guide

This repo supports an offline install path using a local wheelhouse.

## Option A: Vendor wheels (offline)

1. On a machine with internet access, build a wheelhouse:

```bash
python -m pip download -r requirements.lock -d vendor/wheels
```

2. Copy `vendor/wheels` into this repo on the offline machine.

3. Install offline:

```bash
python -m pip install --no-index --find-links vendor/wheels -r requirements.lock
```

## Option B: Docker

If you can build Docker images with network access, use the Dockerfile:

```bash
docker build -t lynch-screener .
docker run -p 8000:8000 lynch-screener
```
