# Protocol — EXP-0027

1. Run the strict-dispatcher UESP doctor and record local dump identity/hash, page counts and provenance caveats.
2. Retrieve raw revision-cited `Skyrim:Dimhollow Crypt`, `Template:Place Summary`, `Template:Place Summary/Skyrim`, `Skyrim:Encounter Zone Level`, and `Skyrim:Dungeons` pages. Follow only the source links needed to determine what the `level` field denotes; treat wiki content as secondary.
3. Verify the installed official Dawnguard CELL-to-ECZN links with the read-only `xedit_bridge.py file-records` route. Record raw fields and label the route as direct TES4 parsing, not native xEdit or a profile winner. Do not decode ECZN DATA without a mapped schema.
4. Query private Apocrypha only in summary-only mode for a directly relevant dated claim; preserve only aggregate output and any necessary provenance IDs under ignored `.local/`.
5. Keep UESP field meaning, Story Manager level gates, physical rubble access, active-order winners and live traversal as separate claims. Do not infer a level-one route from a location's encounter-zone minimum.
