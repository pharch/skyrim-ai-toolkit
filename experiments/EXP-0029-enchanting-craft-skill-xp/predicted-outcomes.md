# Predicted outcomes

- **H1, input-sensitive credit:** changing item value, soul size, or selected effect count changes the raw Enchanting progress delta under the same workbench and XP modifiers, potentially in repeatable quantized steps.
- **H2, station award and cumulative progress:** one successful craft confirmation produces the same raw-progress delta across matched item/soul/effect inputs; two identical crafts add two progress deltas, and the UI skill level remains unchanged until the stored threshold is crossed.
- **Mixed result:** the craft callback supplies a fixed points value, but a modifier or downstream calculation changes the resulting progress. Preserve the call inputs and raw progress rather than collapsing this into either model.
- **Observer/control failure:** no craft or progress change is interpretable unless the positive craft control changes the readout and the no-craft control does not.
- **Static-only result:** a shared call site narrows code-level models but leaves all runtime numeric claims unknown.
