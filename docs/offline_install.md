# Offline Install Guide

This repo supports an offline install path using a local wheelhouse.

## Python version

Use **Python 3.10** to match the Docker image and dependency pins.

## Option A: Vendor wheels (offline)

1. On a machine with internet access, build a wheelhouse:

```bash
python -m pip download -r requirements.lock -d vendor/wheels
```

2. (Optional) generate a hashed lockfile for reproducibility:

```bash
python -m pip hash vendor/wheels/*.whl > requirements.hashes
```

3. Copy `vendor/wheels` into this repo on the offline machine.

4. Install offline:

```bash
python -m pip install --no-index --find-links vendor/wheels -r requirements.lock
```

## Option B: Docker

If you can build Docker images with network access, use the Dockerfile:

```bash
docker build -t lynch-screener .
docker run -p 8000:8000 lynch-screener
```

If building in a restricted network, populate `vendor/wheels` first so Docker installs
from the local wheelhouse instead of reaching the internet.
