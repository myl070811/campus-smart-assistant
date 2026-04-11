#!/usr/bin/env bash
set -e

if command -v docker >/dev/null 2>&1; then
  docker compose up -d --build
else
  echo "Docker is not installed."
  exit 1
fi
