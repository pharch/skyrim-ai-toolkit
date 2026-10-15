# Results

Legacy result: source exists; initial configure lacked Visual Studio `rc`/`mt`, and a corrected retry was blocked by platform usage limits. No DLL is claimed.

Local validation pass — 2026-09-23: `python3 -m unittest discover -s
observer/tests -v` passes all 7 offline analyzer tests. This validates fixture
detectors, float-bit preservation, object lineage across load epochs, state
diffs, truncated-tail handling, and report-bundle generation. It does not
validate the Windows SKSE DLL or native lenses.

Escalated native checks — 2026-09-23: direct CMake failed with `cmake: command
not found` (`exit 127`). The PowerShell build script also failed during
`VsDevCmd` initialization before compilation. No native DLL was produced.
