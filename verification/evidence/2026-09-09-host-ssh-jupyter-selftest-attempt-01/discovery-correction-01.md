# Discovery harness correction

The three first CLI captures failed before dispatch: Python reported that
vastai has no __main__ module. The harness incorrectly assumed `python -m vastai`
was the packaged entry point. This is a collector defect, not a failed offer
search or a reason to change documentation. The current claim remains unvalidated.

Preserve documented-client-01, one-gpu-client-01 and selftest-host-01. Retest via
the pyproject console entry point `vastai.cli.main:main`, unchanged pinned source
ecf32efa1d8d2f110f7de4118c30698bb7ae2fbd and the same query arguments. Only
read-only queries are permitted; credentials stay in child-process memory.

Fresh Host and client identities differ. The funded-client USD5 prerequisite
passes, while the Host account does not establish a USD15 reserve. Do not label
that a billing rule or assume own-host self-tests are free. A self-test phase
must use an approved account with an adequate reserve and required access;
retain its actual credential role and any deviation from the page's Host-key
instruction explicitly before execution.
