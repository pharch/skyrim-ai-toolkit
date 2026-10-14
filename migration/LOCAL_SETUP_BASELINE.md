# Local Setup Baseline

Captured: 2026-10-14 (client local date)

## Destination checkout

- Branch: `glitch-hunting-setup`
- HEAD: `146ef076a5cf91e00fa7a0aed29dde0c8a747aed`
- Worktree was already broadly dirty at session start: 86 modified paths and 6 untracked paths at this capture; staged paths: 0. No reset, checkout, clean, or commit was run. Preserve the pre-existing changes.
- OS/runtime environment: Linux shell on a Windows-mounted workspace. `/etc/os-release`: `PRETTY_NAME="Ubuntu 24.04.4 LTS"; NAME="Ubuntu"; VERSION_ID="24.04"; VERSION="24.04.4 LTS (Noble Numbat)"; VERSION_CODENAME=noble; ID=ubuntu; ID_LIKE=debian; HOME_URL="https://www.ubuntu.com/"; SUPPORT_URL="https://help.ubuntu.com/"; BUG_REPORT_URL="https://bugs.launchpad.net/ubuntu/"; PRIVACY_POLICY_URL="https://www.ubuntu.com/legal/terms-and-policies/privacy-policy"; UBUNTU_CODENAME=noble; LOGO=ubuntu-logo`.
- Available commands verified: Git 2.43.0, Python 3.12.3, Codex CLI 0.162.0-alpha.17.2. `node`, `pytest`, Java, CMake/Ninja, xEdit and Ghidra are absent from PATH. `bzip2`, GCC and G++ are present. Codex CLI starts but reports that it cannot create PATH aliases because the filesystem is read-only.

## External source tree

- The required user-specified `skyrim` research tree is readable, with 242 Markdown/MDX files in the audited text scope.
- Its root `.git` directory is empty (no `HEAD`, `config`, or `index`), so source commit, branch, initial Git status, and submodule state cannot be recovered from this copy. No writes were made there.
- Canonical source manifest SHA-256 (242 relative paths, per-file SHA-256, and byte counts): `4819c59e44aaec195b8f9047730e521eb2ab43b0808ff96bc30e0ee54997bd09`. The temporary startup manifest matches all 242 canonical path/hash/size rows.
- The source `config/local.env` contains concrete candidate paths for two Skyrim executables, xEdit, Ghidra, Java, CommonLibSSE-NG, Address Library and vcpkg. The referenced files/directories exist in the mounted filesystem, but versions, project compatibility and commands have not yet been validated. Values are in ignored `.local/research-paths.toml` only.

## AE/runtime boundary

- Both configured candidate `SkyrimSE.exe` files exist and were SHA-256 hashed; hashes are kept in ignored local config and the redacted tool verification report.
- ProductVersion has **not** been read. `node tools/ae-preflight.js` was not run because Node is unavailable in this shell. xEdit and live game tools have not been invoked.
- No active MO2 profile or complete `plugins.txt` has been verified. No live-game action, save/co-save mutation, plugin edit, or runtime observation was performed.

## Local UESP source candidate

- A pre-existing 186,877,146-byte compressed XML dump is present as an untracked local input; SHA-256: `b3ccaea9d10c653a1bf702d0da5d32c2bc9a5cafdcd374d258f5a063d6074ddb`.
- Header identifies `UESPWiki`, MediaWiki 1.31.16, and a custom `Skyrim` namespace ID 134. Full page/namespace counts, export URL/date provenance, and licensing are pending.
- Direct browser requests to the four official UESP dump/offline pages returned HTTP 403. No official acquisition details have been verified. The dump remains outside Git via an exact ignore rule.

## Evidence files

- Criterion ledger: `LOCAL_SETUP_CHECKLIST.md` (canonical JSON: `local_setup_checklist.json`).
- Detailed path/version checks: `TOOL_PATH_VERIFICATION.md` and `TOOL_COMPATIBILITY_MATRIX.md`.
- Source inventory/import: `OLD_REPO_INVENTORY.md`, `OLD_REPO_SOURCE_MAP.md`, `KNOWLEDGE_IMPORT_AUDIT.md`.
- Exact recovery instruction: `LOCAL_SETUP_RESUME.md`.

## Follow-up results — 2026-10-14

- The local UESP import completed with 475,228 total pages, 17,520 pages in
  custom `Skyrim` namespace 134, 657 empty-text pages, no duplicate pages or
  parse errors, and 475,228 FTS rows. Raw `Skyrim:Karstaag` retrieval,
  namespace search, revision citation, and related links were verified. The
  source URL, license, and completeness remain unknown; see
  `LOCAL_SETUP_REPORT.md` and `TOOL_CAPABILITY_MATRIX.md`.
- All 242 candidate source Markdown/MDX paths have final dispositions. The
  separate source `.git` directory remains empty, so its revision metadata
  cannot be recovered.
