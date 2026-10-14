# Retired non-Python tool entrypoints

This directory preserves the former Node, shell, and Java tool launchers as
historical source only. Skills, CI, and current setup documentation must not
invoke these files. The active research tools are Python entrypoints in
`tools/` and `scripts/`.

The retired xEditLib bridge depended on Node and an unbundled native binding;
its winner-record path was not verified in this environment. ReSaver and
archive wrappers depended on Java/.NET shell launchers. DevBench's live bridge
was not run. Their presence here is not evidence of a working or safe current
integration. Any replacement must have a Python entrypoint and passing tests
before it is routed from a skill.
