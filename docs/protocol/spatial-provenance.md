# Spatial and render provenance

**Provenance:** investigator report supplied 2026-10-08, plus source CSV and image inventory. Grasshopper with Ladybug/Honeybee was used to derive supplied spatial/environmental values. The renders came from Lumion. Renders were sample images; the calculations/extraction conditions were not matched to visual stimuli. Sky, date/time, simulation parameters and input project files are unavailable. Reported illuminance and CCT are supplied room attributes, not verified retinal/headset exposure or controlled manipulations.

Experiment 1's sheet supplies dimensions only. Experiment 2 adds openings and lighting. Experiment 3 adds walkable area and space type. Sleep is recorded only in Experiment 3's biometric sheet. Missing fields are structural and are not zeros. Opening area values are totals: recomputed spreadsheet opening/wall percentages agree within rounding tolerance when areas are used once, without multiplying by count.

Thirty source render files map by filename stem to populated `Room_ID`s. The source inventory and original hashes are in `data/MANIFEST.sha256` and `docs/reports/migration-inventory.json`. Display derivatives are separate and must identify any assumed panorama/eye extraction convention. The original file remains accessible.
