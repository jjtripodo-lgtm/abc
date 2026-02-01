# abc

A Peter Lynch-inspired stock screener with a FastAPI UI and deterministic stub data.

## Quickstart

```bash
pip install -r requirements.lock
python -m uvicorn src.app:app --reload
```

Open `http://localhost:8000` and run the screen using the stub universe.

## Validation recipe (offline-friendly)

1. Build a wheelhouse on a networked machine:

```bash
python -m pip download -r requirements.lock -d vendor/wheels
```

2. Install offline and run tests:

```bash
python -m pip install --no-index --find-links vendor/wheels -r requirements.lock
python -m pytest
```

3. Run a deterministic CLI demo (stub data):

```bash
python src/cli.py render-ui --provider stub --out dist
```

## Offline install

See [docs/offline_install.md](docs/offline_install.md) for vendored wheel instructions or use the Dockerfile.

## Docker

- **Online build**: `docker build -t lynch-screener .`
- **Offline build**: pre-populate `vendor/wheels` and the Dockerfile will install from it.

## CLI (Yahoo Finance)

```bash
python src/cli.py screen AAPL MSFT --risk balanced
```

> Note: Yahoo Finance is optional and not used by tests or the default UI flow.

## API

- `GET /health` returns `{ "status": "ok" }`.
- `GET /api/hello` returns a hello message.
- `POST /api/screen` with JSON:
  ```json
  {
    "tickers": ["AAPL", "MSFT"],
    "risk_tolerance": "balanced",
    "universe": "stub"
  }
  ```

## Tests

```bash
python -m pytest
```

## Notes

This tool uses simplified rules inspired by Peter Lynch principles and is not
investment advice.
