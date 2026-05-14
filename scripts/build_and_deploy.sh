#!/usr/bin/env bash
# Panel — build the v2 frontend, copy into the FastAPI app dir,
# and deploy as a Databricks App via Asset Bundle.
set -euo pipefail

PANEL=/Users/ahmetbarisgunaydin2/panel
V2=/Users/ahmetbarisgunaydin2/panel-v2

echo "── build panel-v2 ──"
cd "$V2" && npm run build

echo "── copy dist → app/static ──"
rm -rf "$PANEL/app/static"
mkdir -p "$PANEL/app/static"
cp -r "$V2/dist/." "$PANEL/app/static/"
echo "  bundled $(find "$PANEL/app/static" -type f | wc -l) files into app/static"

echo "── databricks bundle validate ──"
cd "$PANEL" && databricks bundle validate --target dev

echo "── databricks bundle deploy ──"
databricks bundle deploy --target dev

echo "── done ──"
databricks bundle run panel --target dev 2>&1 | head -20 || true
echo
echo "App URL will appear in workspace → Compute → Apps after deployment finishes."
