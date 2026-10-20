# EXP-0061 — Five-master GetLevel CTDA census

## Question

Do any official Skyrim AE record signatures outside the previously screened SMQN and DIAL/INFO families contain GetLevel CTDA conditions that gate quest, encounter, or access progression?

This is a source census, not a profile-winner or runtime test. Its purpose is to find source-backed candidates and identify where static record coverage is incomplete.

## Scope and method

The capture script scans every record and subrecord in the five official masters using the existing read-only `tools.plugin_reader.read_plugin` implementation. It checks the installed Steam executable identity against EV-0109, hashes the executable and each master, counts records by signature and all CTDA records, retains every well-formed function-index-80 condition, and records CTDA length anomalies. The existing EXP-0052 decoder is used for 32-byte CTDA fields.

Raw machine-local output stays under ignored `.local/alignment/transactions/`. The tracked result reports master names and hashes, not machine paths. A complete condition census requires every master to finish parsing and no CTDA length anomalies; a parser-complete capture with anomalous CTDA lengths remains incomplete for the negative claim.

## Evidence boundary

The five prepared official files are not an active-profile winner. EV-0260 records that the complete selected order and live observer prerequisites are unavailable. A source condition alone does not establish that a vanilla level-one player can reach the transition or that it is effective in the installed load order.
