#!/bin/bash
# Read-only archive inspection wrapper for the optional AutoMod CLI.
# Usage: bash tools/automod-cli.sh archive <info|list|validate|diff|status> [args] --json
#
# Invokes the pre-built Release DLL directly (no per-call recompile) to avoid the
# MSB1025 / SDK-mismatch failures that `dotnet run` triggered. A global.json in
# tools/automod/ pins SDK 8.0.x (matches the net8.0 TFM); the build is the Cli
# project only (Setup is a WPF net8.0-windows app we don't want in a headless build).
#
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLI_PROJ="$SCRIPT_DIR/automod/src/SpookysAutomod.Cli"
DLL="$CLI_PROJ/bin/Release/net8.0/spookys-automod.dll"

if [ "${1:-}" != "archive" ] || [ -z "${2:-}" ]; then
    echo "ERROR: only read-only archive inspection is enabled in this research harness." >&2
    exit 2
fi
case "$2" in
    info|list|validate|diff|status) ;;
    *)
        echo "ERROR: archive writes/extraction are disabled; use info, list, validate, diff, or status." >&2
        exit 2
        ;;
esac
if ! printf '%s\n' "$@" | grep -q -- '--json'; then
    echo "ERROR: pass --json so results are machine-auditable." >&2
    exit 2
fi

if [ ! -f "$DLL" ]; then
    echo "Built DLL not found at: $DLL" >&2
    echo "Run: bash tools/automod-cli.sh --rebuild" >&2
    exit 1
fi

dotnet "$DLL" "$@"

# Legacy (per-call recompile — caused MSB1025; kept for reference):
# dotnet run --project "$CLI_PROJ" -- "$@"
