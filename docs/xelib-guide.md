# xEditLib/xelib for Skyrim AE research

xEditLib exposes xEdit record inspection through a Delphi-compiled Windows
DLL. It is not available to Linux CI. Skyrim AE uses xEdit `GM_SSE` (enum 4)
for plugin data, but that mode does not detect AE; use
`node tools/ae-preflight.js` first.

## Prerequisites

1. Windows, Node.js 20+, an operator-installed xEditLib package, and the
   required xEdit registry mapping to the intended AE installation.
2. Local `config/local.env` values: `SKYRIM_EDITION=AE`, `GAME_ROOT`, and an
   absolute `PLUGINS_TXT`. For MO2, choose the active profile's virtualized
   plugin list. Never use a hand-selected plugin subset for an absence or
   winner claim.
3. Run the executable and load-order preflight, then preserve its output,
   executable SHA-256, and profile path/hash with the experiment.

## Read-only usage

```sh
bash tools/skyrim-winner.sh winner 0x0003418E
bash tools/skyrim-winner.sh chain 0x0003418E
bash tools/skyrim-winner.sh conflicts Example.esp
```

The winner helper loads the complete active order and asks xEdit for the
winning override. The shell wrapper's exit status is authoritative: 0 denotes
a complete result, 2 a reported error, 3 no valid result marker. Inspect logs
for the `RESULT:` line and loaded plugin count. Never convert a loader error or
empty tree into a negative record finding.

## FFI caveats retained from upstream

- Delphi strings are UTF-16LE, not UTF-8.
- `WordBool` is 16-bit. `InitXEdit()` and `CloseXEdit()` are void.
- String results use a length output then a separate string retrieval call.
- Use file-based Node scripts for xelib, not `node -e`.
- Terminate the game path with a separator before initializing the native
  library; call order can otherwise change whether the DLL reports an error.
- Release every record/element handle after use.

Do not call `SaveFile` or deserialize altered Spriggit output. Registry creation and xEditLib installation
are operator-managed Windows setup, not automated by this repository.
