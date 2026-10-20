# Physical-trap mitigation with Light/Heavy armor and no known resolver award

This dossier tests whether the physical-trap route can retain the PlayerCharacter cached Light/Heavy armor factor while skipping the known normal resolver AV11/AV12 award branch.

## Static result

GOG AE 1.6.1179.0 code routes BOD2 type 0/1 ARMO entries through the DNAM-based rating visitor and into the PlayerCharacter `+0x274` cache consumed by the hit builder. The trap builder uses the shared AV39/cache mitigation helper and bypasses the resolver containing the known AV11/AV12 award branch. The bounded receiver-handler scan shows no mapped AV11/AV12 award, but cleanup callees and derived reference dispatch remain unresolved.

This is a static vanilla candidate only. It does not establish positive effective protection, a complete zero-award path, Steam 1.6.1170.0 behavior, or level-one reproduction. See EV-0312 and prior evidence EV-0261, EV-0302–EV-0304, and EV-0311.
