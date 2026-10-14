> Historical validation report from a different checkout/toolchain. Its PASS results are not current evidence; see `LOCAL_SETUP_REPORT.md` and `LOCAL_SETUP_CHECKLIST.md`.

# Final validation report

## Environment
- Branch: `glitch-hunting-setup`
- Commit: `8b1c0f48d3c134b35e3d125aa3f9e7f6657bffa7`
- OS: Linux x86_64 (Codespaces host)
- Toolchain: Node.js v20.20.2, npm 10.8.2, Python 3.11.15, pytest 9.0.2
- Windows AE runtime: not available here; no live runtime verification is claimed

## Commands executed
```sh
cd /workspaces/skyrim-ai-toolkit
python -m pytest -q
npm test -- --test-reporter=spec
python scripts/validate_research.py
python scripts/validate_overlay.py
python scripts/setup_research.py check
```

## Results
- `python -m pytest -q`: PASS (94 passed)
- `npm test -- --test-reporter=spec`: PASS (23 tests, 0 failed)
- `python scripts/validate_research.py`: PASS (research schema/frontier state valid)
- `python scripts/validate_overlay.py`: PASS after creating the missing required docs and finalizing the checklist
- `python scripts/setup_research.py check`: PASS when run after completion

## Repository status
- Cloud/repo readiness: PASS
- Windows AE runtime verification: BLOCKED_ENV; follow [docs/WINDOWS_AE_VERIFICATION.md](../docs/WINDOWS_AE_VERIFICATION.md)

## Important boundary
This report proves the repository logic, schema, docs, and offline test behavior. It does not prove a live Windows Skyrim AE install or gameplay result, which remains a separate Windows-only validation step.
