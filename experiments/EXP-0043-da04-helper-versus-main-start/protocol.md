# Protocol

1. Use the strict Python dispatcher and direct TES4 parser against the prepared official five-master scope. Preserve raw wrapper JSON, exact commands, source plugin hashes, and output hashes under ignored .local/alignment/transactions/TX-20261016-0036/.
2. Capture Skyrim.esm QUST DA04, DA04SeptimusSendForPlayerQuest, the DA04 Story Manager SMQN, and Elder Knowledge QUST MQ205 if the editor ID is confirmed. Locate the Ruminations BOOK and its references by a bounded BOOK inventory or exact source-context search; do not guess a FormID.
3. Capture directly referenced DIAL/INFO, alias, stage/fragment, and relevant VMAD-bearing records. Resolve every FormID in the source plugin's TES4 MAST context. A raw reference is not proof that a caller executes or starts the quest.
4. Record QUST conditions, Start Game Enabled and other start flags, stage flags, alias fields, QNAM/quest references, book activation data, and any GetLevel predicates. Decode fields only against TES5Edit `dev-4.1.6` schema or direct raw values with documented offsets. For fragmented QUST VMAD, retain the decoder and raw output so fragment stage/log-entry mapping is reproducible.
5. Keep the UESP revision 3564369 route description and source hash separate from direct game-record observations. Do not infer a native caller from a Papyrus declaration or a missing script body.
6. If the exact native five-master xEdit query runs, record its loaded-file list and keep it separate from direct-parser evidence. If it fails before launch, preserve the exact error and continue static work.
7. To validate level-one behavior, require an unmodified clean save at numeric level 1, an ordinary no-trigger control, a read-only quest/stage observation, preservation of level 1, and repetition. No console, injected script, edited plugin, or forced stage may be called a vanilla reproduction.

## Static result and limits

EV-0301 records the source outcome. The main QUST is configured Start Game Enabled; alias ID 19 binds the named book alias to REFR `00032787` and its alias script sets stage 1 on read. QUST VMAD maps stage 1 to Fragment_18, which sets stage 5. This identifies an ordinary early-start candidate distinct from the >=15 courier helper, but does not establish active-profile winners, book-cell access, a live level-one state, or later stage progression. Native xEdit retried under this transaction but failed before process enumeration with `UtilBindVsockAnyPort`; direct-parser observations remain the usable static lane.
