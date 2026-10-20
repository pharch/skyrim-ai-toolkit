# Predicted outcomes — EXP-0026

- **H1:** an unmodified level-one candidate crosses the rubble and reaches `0200FB21` before stage 10; a read-only observer records the callback and any quest/alias/progression changes while numeric level stays 1. The matched control has no corresponding transition.
- **H2:** ordinary route setup controls the passage or required gate; no player-only crossing appears in the tested candidate. Static records alone cannot falsify H1 because they do not expose collision geometry.
- **H3:** the trigger is physically reached, but VQ01 remains stopped or fails to fill required aliases or produce useful progression. A trigger callback alone is not success.
- **Gate-script finding:** disassembly has only animation and keyword-linked collision toggles, with no `SetStage` or explicit marker-enable call. This supports separation of the generic physical gate action from quest progression, but does not determine the initial child enable state or a collision route.

No runtime outcomes were collected in this investigation.
