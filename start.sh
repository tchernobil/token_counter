#!/usr/bin/env bash
exec env PYTHONPATH="$(dirname "$0")${PYTHONPATH:+:$PYTHONPATH}" python3 -m token_counter "$@"
