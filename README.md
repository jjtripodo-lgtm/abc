# abc

A Peter Lynch-inspired stock screener with a FastAPI UI and deterministic stub data.

## Quickstart

```bash
pip install -r requirements.txt
python -m uvicorn src.web_app:app --reload
```

Open `http://localhost:8000` and run the screen using the stub universe.

## API

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
