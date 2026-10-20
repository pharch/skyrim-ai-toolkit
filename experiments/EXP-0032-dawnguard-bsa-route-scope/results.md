# Results

- `domain_doctor.py` completed under the strict dispatcher. It reports the verified Steam runtime 1.6.1170 and missing full active order/live-call readiness, but no archive-reader status or Dawnguard route ([EV-0284]).
- Papyrus CLI help exposes only `disassemble`, `extract`, and `scan-literals`. The `extract` command constructs `data_dir / "Skyrim - Misc.bsa"`. `scan-literals` uses that same archive and optionally enumerates `cc*.bsa` ([EV-0284]).
- The internal extractor takes an archive path but searches raw bytes for PEX markers and a source filename. The CLI does not expose that path argument. The unit test uses a synthetic byte fixture named `Skyrim - Misc.bsa`; it does not validate a real Dawnguard BSA or compressed archive ([EV-0284]).
- The archive-source skill and tool routing describe only the tested Misc-BSA path. Repository inventory revealed no other configured general BSA route ([EV-0284], [EV-0274]).
- `Dawnguard.bsa` was not opened or passed to a tool. Its filename, size, hash, internal contents, and `defaultSetStageTrigSCRIPT` presence remain unknown.

**Outcome:** H1 is falsified for the current documented/tested harness routes; H2 is supported. This blocks only Dawnguard-BSA extraction. It is not evidence that the script or a relevant record is absent.
