#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_DIR="$ROOT_DIR/dist/windows"
PACKAGE_DIR="$DIST_DIR/acc_log_sentinel"
ZIP_NAME="acc_log_sentinel-windows-amd64.zip"
export GOCACHE="${GOCACHE:-/tmp/acc_log_sentinel-gocache}"
export GOMODCACHE="${GOMODCACHE:-/tmp/acc_log_sentinel-gomodcache}"

echo "[package] building Windows binary"
mkdir -p "$ROOT_DIR/bin"
GOOS=windows GOARCH=amd64 go build -o "$ROOT_DIR/bin/sentinel.exe" "$ROOT_DIR/cmd/sentinel"

echo "[package] preparing release directory"
rm -rf "$PACKAGE_DIR"
mkdir -p "$PACKAGE_DIR/data"

cp "$ROOT_DIR/bin/sentinel.exe" "$PACKAGE_DIR/sentinel.exe"
cp "$ROOT_DIR/setup.bat" "$PACKAGE_DIR/setup.bat"
cp "$ROOT_DIR/sentinel.env.example" "$PACKAGE_DIR/sentinel.env.example"
cp "$ROOT_DIR/deploy/windows/INSTALL-WINDOWS.txt" "$PACKAGE_DIR/INSTALL-WINDOWS.txt"

echo "[package] writing zip archive"
rm -f "$DIST_DIR/$ZIP_NAME"
(
	cd "$DIST_DIR"
	zip -rq "$ZIP_NAME" "acc_log_sentinel"
)

echo "[package] done"
echo "  folder: $PACKAGE_DIR"
echo "  zip:    $DIST_DIR/$ZIP_NAME"
