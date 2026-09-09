# Publication addendum — exact evidence bytes

The original pre-stage whitespace checks passed for their then-staged/unstaged scope. After the previously untracked evidence was staged, `git diff --cached --check` reported existing blank-at-EOF/trailing-space formatting in retained artifacts and the exact hash-pinned connection registry. The staged-blob identity comparison passed before this formatting gate stopped the disposable publication harness.

[Actual staged whitespace output](staged-whitespace-02.json) retains the nonzero exit and each diagnostic. Each affected file is byte-identical to the pre-action baseline; none is implementation or customer-page code. This is not converted into a raw whitespace PASS.

The user's existing instruction to preserve historical attempts and the V&V evidence-preservation rule take precedence over cosmetic normalization. Keep these exact bytes; do not alter hashes, rewrite records, suppress global Git checks, bypass hooks, or manufacture retests for product behavior. The revised publication gate verifies the exact same diagnostic set and baseline file identities, while still rejecting any additional formatting finding or file drift.

The additional publication-only records are inventoried separately. No source, customer wording, operational claim, reviewer verdict or historical artifact changes for this disposition. This is an agent decision about harmless retained formatting, not human acceptance of the Host docs or any product risk.
