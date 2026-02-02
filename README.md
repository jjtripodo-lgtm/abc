# abc

A Peter Lynch-inspired stock screener with a FastAPI UI and deterministic stub data.

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.lock
python -m uvicorn src.app:app --reload
```

Open `http://localhost:8000` and run the screen using the stub universe.

## Offline install

See [docs/offline_install.md](docs/offline_install.md) for vendored wheel instructions or use the Dockerfile.

## CLI (Yahoo Finance)

```bash
python src/cli.py AAPL MSFT --risk balanced
```

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
