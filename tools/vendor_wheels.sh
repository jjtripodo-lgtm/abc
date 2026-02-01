#!/usr/bin/env bash
set -euo pipefail

python -m pip download -r requirements.lock -d vendor/wheels
