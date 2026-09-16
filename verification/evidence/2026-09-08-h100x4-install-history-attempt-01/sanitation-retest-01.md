# Source metadata sanitation correction and retest

Date: 2026-09-08. Method: local byte retention, one-field masking, JSON equality and path checks. No remote operation.

The initial `source-inspection-01.json` metadata included an absolute workstation-user checkout path. This was a publication-sanitation defect, not a product or installation failure. The entire original 4,322-byte record is preserved in the restricted intake directory, mode 0600, SHA-256 `5b9e13a3e1c324ee363f57b3adc15a47444a273e27479d2fcfa7928c93e6f746`.

The public copy masks only `local_tui_source.path` with `<RESTRICTED_LOCAL_CHECKOUT>/host-installer-wizard`. Its SHA-256 is now `e01d79c9793119b9d7a117b74d75d007b1eeb5b4021c2b95bf1784603a73e2f2`. Comparing parsed objects after that one replacement returned true; checking for `/Users/` in the public copy returned false. Result: PASS for this exact sanitation correction. All original source interpretations, limitations and source digests are unchanged; the later semantic corrections remain in source inspection 02.

This is a linked correction/retest with original bytes retained, not erasure of the first attempt. It does not establish absence of every possible sensitive item in unrelated historical repository files.
