# Results

## Direct observations

- The official CLOC node and QUST select `DLC2CultistAmbush`; the separate
  SCPT branch selects `DLC2WE09`. The CLOC parent/node/QUST and loose stage
  sources screened in Q81 expose no `GetLevel` predicate [EV-0654]–[EV-0664].
- `DLC2WE09` has a bounded `GetLevel >=25 OR Solstheim` group after its earlier
  chance/stage conditions under the identity-checked GOG condition evaluator
  [EV-0657], [EV-0665]–[EV-0669].
- UESP revision 3586604 describes the pair sent after The Way of the Voice
  separately from level-25 random encounters; the Dragonborn quest page names
  separate givers for the pair and world encounters [EV-0679].
- The two CLOC alias NPCs link through `DLC2LvlCultist*` records to root LVLN
  records. The root lists carry thresholds from level 1 through 46 and
  `LVLF=0x03`; their level-1 nested entries point to the Cultist and Summoner
  NPC sets [EV-0677].
- The four alias/template NPC records have ACBS actor flags `0x00000000`, so
  PCLevelMult and UsesTemplate bits are clear; they nevertheless store TPLT
  links and nonzero template-use masks. The leaf cultist NPCs encode actor
  level 12 and link to a separate template [EV-0677].
- The GOG 1.6.1179.0 TESNPC secondary vtable slot 4 maps to the
  `CopyFromTemplateForms` override. Its body reads the base-template pointer,
  checks per-field template-use bits, and branches on ACBS bit `0x100`; a
  helper can set that bit and initialize template-chain state [EV-0678].
  CommonLib/TES5Edit labels and layouts identify the relevant fields [EV-0680].

## Assessment

H1 is falsified for the bounded official record and loose PSC path; H2 is
supported for that scope. No explicit level gate was found before the CLOC
QUST in those sources. The level-25 condition is on the distinct world QUST.
The alias-to-LVLN chain makes level-dependent actor selection a supported
serialized candidate, but H3 and H4 remain unresolved for actual runtime use:
the aliases' UsesTemplate bits are clear, and neither the GOG method nor the
record walk shows which base FormIDs the installed Steam CLOC aliases receive.

This is not a level-one bypass because the CLOC path itself has no demonstrated
pre-start level gate. It is also not a Steam runtime reproduction. There is no
causal edge from this event/template line to the OBJ-2 armor mitigation or
armor-XP mechanism; the exact positive-protection/raw-AVSK Steam test remains
EV-0260.

## Next action

Close Q83 as a bounded static source investigation, retain H3/H4 as a separate
runtime discriminator under EV-0260, then let the validated frontier selector
begin the highest-information-gain independent P0 item. Continue with the
selected line rather than treating this local result as bounty completion.

## Durable scope note

The direct parser evidence EV-0677 is from the configured Steam AE Data tree
associated with verified executable identity EV-0109, but the parser did not
load a complete active plugin order or resolve profile winners. The GOG code
capture EV-0678 is separately tied to 1.6.1179.0 and is not transferred to
Steam. EV-0679 is secondary UESP grounding; EV-0680 labels record fields and
class layout only. None of these evidence classes establishes a natural
level-one CLOC start or actual alias actor FormIDs.
