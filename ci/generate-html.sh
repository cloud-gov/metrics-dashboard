#!/usr/bin/env bash
set -euo pipefail

echo "==> Installing dependencies (deterministic)"
npm ci

echo "==> Preparing data.json"
# Data is produced by the previous Concourse task into data
# Keep this explicit for now; we’ll clean the output path next.
cp data/data.json src/data.json

echo "==> Building dashboard (CSS + HTML)"
npm run build

echo "==> Build complete"
