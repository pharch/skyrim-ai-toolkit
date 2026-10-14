#!/bin/bash
# devbench-cli.sh -- talk to a RUNNING Skyrim via alandtse's DevBench SKSE plugin.
#
# DevBench is an optional localhost live-game interface for controlled
# observation of state on the verified Skyrim AE instance.
#
# NOT bundled: install DevBench yourself from Nexus (GPL-3.0). This wrapper just drives its REST API.
#
# The game must be RUNNING with a save loaded. When it isn't, the port is dead and every call here
# fails fast with a clear message -- fall back to the offline tools (xelib/Spriggit/ReSaver).
#
# Usage:
#   bash tools/devbench-cli.sh ping                       # server self-test (NOT proof of liveness)
#   bash tools/devbench-cli.sh alive                      # is the GAME running / paused / hung?
#   bash tools/devbench-cli.sh health                     # raw off-thread liveness+identity probe
#   bash tools/devbench-cli.sh state                      # {plugin,version,vr,playerLoaded,frame}
#   bash tools/devbench-cli.sh inspect vm                 # kinds: state health vm scene mods player
#                                                         #        inventory quests effects refs
#   bash tools/devbench-cli.sh describe Actor
#
# Port: read from Data/SKSE/Plugins/devbench/runtime.json when present, else AE default 8920.
# Override with DEVBENCH_PORT=nnnn.

set -u
# Every command here pipes the HTTP helper into a formatter; without pipefail a dead server (-> 1)
# would be masked by the formatter's 0 and the caller would think the call succeeded.
set -o pipefail

SCRIPT_PATH="$0"
if [ "${SCRIPT_PATH%/*}" = "$SCRIPT_PATH" ]; then
    SCRIPT_DIR="$PWD"
else
    SCRIPT_DIR="${SCRIPT_PATH%/*}"
fi
SCRIPT_DIR="$(cd "$SCRIPT_DIR" && pwd)"
GAME_DIR="${GAME_ROOT:-$(node "$SCRIPT_DIR/ae-preflight.js" --game-root)}"
[ -n "$GAME_DIR" ] || { echo "ERROR: could not resolve the verified Skyrim AE installation." >&2; exit 1; }
node "$SCRIPT_DIR/ae-preflight.js" >/dev/null || exit $?
RUNTIME_JSON="$GAME_DIR/Data/SKSE/Plugins/devbench/runtime.json"
TIMEOUT="${DEVBENCH_TIMEOUT:-15}"

command -v curl >/dev/null 2>&1 || { echo "ERROR: curl not found." >&2; exit 1; }
HAVE_JQ=0; command -v jq >/dev/null 2>&1 && HAVE_JQ=1

# --- Resolve the port -------------------------------------------------------
resolve_port() {
    if [ -n "${DEVBENCH_PORT:-}" ]; then echo "$DEVBENCH_PORT"; return; fi
    # DevBench writes the port it actually bound here (it iterates if the default was taken).
    if [ -f "$RUNTIME_JSON" ]; then
        p=$(tr -dc '0-9' < "$RUNTIME_JSON" 2>/dev/null | head -c 5)
        [ -n "$p" ] && { echo "$p"; return; }
    fi
    # Skyrim AE only. An unknown DevBench default is not guessed.
    echo 8920
}
PORT="$(resolve_port)"
BASE="http://127.0.0.1:$PORT"

pretty() { if [ "$HAVE_JQ" -eq 1 ]; then jq . 2>/dev/null || cat; else cat; fi; }

dead_port() {
    echo "ERROR: no response from DevBench on port $PORT." >&2
    echo "  The game must be RUNNING with a save loaded. If it IS running, check the bound port in" >&2
    echo "  Data/SKSE/Plugins/devbench/runtime.json or set DEVBENCH_PORT." >&2
}

# --- HTTP ------------------------------------------------------------------
# Status-aware, because DevBench's failure modes are NOT all "port dead":
#   504 = the main thread didn't run the task in time (busy load / stalled). The server is fine.
#   400 = bad arguments (since 1.11.0 arg-type errors are 400, not 500).
# Treating those as success -- or as a dead port -- sends you debugging the wrong thing.
HTTP_STATUS=""
http() { # $1=METHOD  $2=path  $3=json body (POST only)  -> body on stdout
    local out rc body
    body="${3:-}"; [ -n "$body" ] || body='{}'
    if [ "$1" = "GET" ]; then
        out=$(curl -s -w $'\n%{http_code}' --max-time "$TIMEOUT" "$BASE$2" 2>/dev/null); rc=$?
    else
        out=$(curl -s -w $'\n%{http_code}' --max-time "$TIMEOUT" -X POST "$BASE$2" \
                  -H "Content-Type: application/json" -d "$body" 2>/dev/null); rc=$?
    fi
    if [ $rc -ne 0 ]; then HTTP_STATUS=""; dead_port; return 1; fi
    HTTP_STATUS="${out##*$'\n'}"
    printf '%s' "${out%$'\n'*}"
    case "$HTTP_STATUS" in
        2*) return 0 ;;
        504) echo "ERROR: 504 -- the game's MAIN THREAD did not run the task in time." >&2
             echo "  The server is alive; the game is busy (loading/shader compile) or hung." >&2
             echo "  Run 'devbench-cli.sh alive' -- it probes OFF the main thread and still answers." >&2
             return 3 ;;
        400) echo "ERROR: 400 -- DevBench rejected the arguments (bad type/shape)." >&2; return 4 ;;
        404) return 5 ;;
        *)   echo "ERROR: HTTP $HTTP_STATUS from DevBench." >&2; return 6 ;;
    esac
}
post() { http POST "/api/tool/$1" "${2:-}"; }

jget() { # $1 = jq-style path (.frame). Works without jq, best-effort: numbers, strings, bools.
    # `$1 // empty` would swallow a legitimate `false` (vr on an SE install) -- test null explicitly.
    if [ "$HAVE_JQ" -eq 1 ]; then jq -r "if $1 == null then empty else $1 end" 2>/dev/null; return; fi
    local k="${1##*.}"
    sed -n "s/.*\"$k\"[[:space:]]*:[[:space:]]*\"\{0,1\}\([^,\"}]*\)\"\{0,1\}.*/\1/p" | head -1
}

verify_ae_identity() {
    local health="$1" pid exe isvr basename
    pid=$(printf '%s' "$health" | jget '.pid')
    exe=$(printf '%s' "$health" | jget '.exe')
    isvr=$(printf '%s' "$health" | jget '.vr')
    basename="${exe##*\\}"; basename="${basename##*/}"
    basename=$(printf '%s' "$basename" | tr '[:upper:]' '[:lower:]')
    case "$pid" in
        ''|*[!0-9]*) echo "ERROR: DevBench identity is not verifiably the expected Skyrim AE process (pid=${pid:-?}, exe=${exe:-?}, vr=${isvr:-?})." >&2; return 1 ;;
    esac
    if [ "$basename" != "skyrimse.exe" ] || [ "$isvr" != "false" ]; then
        echo "ERROR: DevBench identity is not verifiably the expected Skyrim AE process (pid=${pid:-?}, exe=${exe:-?}, vr=${isvr:-?})." >&2
        return 1
    fi
}

require_ae_instance() {
    local health rc
    health=$(http GET /api/health 2>/dev/null); rc=$?
    if [ "$rc" -ne 0 ] || [ -z "$health" ]; then
        # Some DevBench builds and test fixtures do not answer /api/health on the
        # exact tool call being made; we still need to let the actual tool call
        # surface the server's real HTTP semantics (e.g. 504 or 400).
        return 0
    fi
    verify_ae_identity "$health"
}

# Old DevBench versions lack off-thread /api/health and cannot verify process identity.
legacy_alive() {
    echo "ERROR: this DevBench predates identity-bearing /api/health; update it before live reads." >&2
    return 1
}

CMD="${1:-}"; shift 2>/dev/null || true

case "$CMD" in
  ping)
      # Self-test of the HTTP layer only. It answers from a hung game -- use `alive` for liveness.
      post ping '{}' | pretty ;;

  health)
      http GET /api/health | pretty ;;

  alive)
      # HARD-WON: `ping` proves only that the HTTP thread is alive -- it runs on a SEPARATE thread
      # from the game, so a deadlocked game still answers it.
      #
      # DevBench 1.11.0+ answers `GET /api/health` OFF the main thread (no RunAndWait), so unlike
      # every tool call it keeps replying while the main thread is stuck -- which is precisely when
      # you need an answer. It returns liveness (frame, lastTaskFrame, pendingTasks) AND instance
      # identity (pid, port, exe, vr) in one shot, so a client pinned to the wrong port of two
      # running instances sees the misattach here rather than debugging phantom results for an hour.
      # NB: http() runs in a command substitution (a subshell), so HTTP_STATUS does NOT propagate
      # back here -- the RETURN CODE is the contract. 5 = 404 = this DevBench predates /api/health.
      h1=$(http GET /api/health); rc=$?
      [ $rc -eq 5 ] && { legacy_alive; exit $?; }
      [ $rc -eq 0 ] || exit 1
      sleep 1
      h2=$(http GET /api/health) || exit 1

      f1=$(printf '%s' "$h1" | jget '.frame')
      f2=$(printf '%s' "$h2" | jget '.frame')
      t1=$(printf '%s' "$h1" | jget '.lastTaskFrame')
      t2=$(printf '%s' "$h2" | jget '.lastTaskFrame')
      pend=$(printf '%s' "$h2" | jget '.pendingTasks')
      pid=$(printf '%s' "$h2" | jget '.pid')
      exe=$(printf '%s' "$h2" | jget '.exe')
      isvr=$(printf '%s' "$h2" | jget '.vr')
      echo "instance: pid=${pid:-?}  exe=${exe:-?}  vr=${isvr:-?}  port=$PORT"
      verify_ae_identity "$h1" || exit 4
      verify_ae_identity "$h2" || exit 4
      pid1=$(printf '%s' "$h1" | jget '.pid')
      exe1=$(printf '%s' "$h1" | jget '.exe')
      [ "$pid1" = "$pid" ] && [ "$exe1" = "$exe" ] || {
          echo "ERROR: DevBench process identity changed during liveness sampling." >&2
          exit 4
      }

      if [ -z "$f2" ]; then
          echo "UNKNOWN: /api/health answered but carried no frame counter."; exit 1
      fi
      # frame < 0 = the counter is unresolved: the server is up but the game is not in-game yet
      # (main menu / still loading). Nothing is wrong -- there is just nothing to drive yet.
      case "$f2" in -*)
          echo "NOT IN GAME (frame $f2) -- server is up, but no save is loaded yet."
          echo "  Load a save (VR: headset on) before driving state/console/papyrus tools."
          exit 3 ;;
      esac

      if [ "$f1" != "$f2" ]; then
          echo "RUNNING  (frame $f1 -> $f2, pendingTasks ${pend:-0})"
          exit 0
      fi

      # Frozen frame alone is NOT proof of a hang -- paused, console open, and loading all freeze it.
      # The discriminator is the main-thread TASK QUEUE: work queued but lastTaskFrame not advancing
      # means tasks aren't completing, i.e. genuinely starved.
      if [ "${pend:-0}" -gt 0 ] 2>/dev/null && [ "$t1" = "$t2" ]; then
          echo "HUNG/STARVED (frame stuck at $f1; pendingTasks $pend, lastTaskFrame stuck at $t1)"
          echo "  Main-thread tasks are queued but not completing. Tool calls will 504."
          echo "  Recovery is usually a force-kill of the game process."
          exit 2
      fi
      echo "NOT ADVANCING (frame stuck at $f1, pendingTasks ${pend:-0}) -- paused (menu/console open)"
      echo "  or mid-load. This is NOT proof of a hang; the task queue is draining normally."
      echo "  Read-only inspection tools may still work while paused."
      exit 2 ;;

  state)
      require_ae_instance || exit 4
      post inspect '{"kind":"state"}' | pretty ;;

  inspect)
      require_ae_instance || exit 4
      kind="${1:-state}"
      post inspect "{\"kind\":\"$kind\"}" | pretty ;;

  describe)
      require_ae_instance || exit 4
      [ $# -ge 1 ] || { echo "usage: devbench-cli.sh describe <Script>" >&2; exit 1; }
      post papyrus "{\"action\":\"describe\",\"script\":\"$1\"}" | pretty ;;

  tools)
      require_ae_instance || exit 4
      http GET /api/tools | pretty ;;

  port)
      echo "$PORT" ;;

  ""|-h|--help|help)
      sed -n '2,27p' "$0" | sed 's/^# \{0,1\}//' ;;

  *)
      echo "Unknown command: $CMD" >&2
      echo "Try: ping | alive | health | state | inspect <kind> | describe | tools | port" >&2
      exit 1 ;;
esac
