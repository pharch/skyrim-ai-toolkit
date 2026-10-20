# Results

EV-0337 maps PlayerCharacter slot +0x378 to FUN_1407371f0 and confirms the flag-zero branch delegates to a generic TLS/nested-field accessor. FUN_1402e55a0 has zero outgoing direct and indirect call sites, but the returned object's class and its dynamic slot +0x150 target remain unknown. The +0x68 and +0x5F0 displacement scans do not identify the context field's owner or a TLS writer. Q64-H1/H2 remain proposed [EV-0337], [EV-0336], [EV-0329].
