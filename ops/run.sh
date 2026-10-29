#!/bin/bash
set -euo pipefail
exec /usr/bin/python3 "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/run.py" "$@"
