#!/bin/bash
set -euo pipefail
exec /usr/bin/python3 /root/linkedin-script-writer/ops/run.py "$@"
