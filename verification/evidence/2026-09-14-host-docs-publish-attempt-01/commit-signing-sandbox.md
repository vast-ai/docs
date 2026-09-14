# Initial signed commit attempt

The normal `git commit` on 14 September 2026 exited 128 before creating a
commit. The filesystem sandbox prevented GPG from creating its lock file and
connecting to the configured keybox daemon. No signing key was read into tool
output. The reviewed index remained staged and HEAD remained 4fa6fbb.

Next action: retry the same normal signed commit with the required local GPG
access. Do not disable signing, change the configured key or bypass hooks.
The resulting Git commit and remote readback establish whether the retry worked;
this initial attempt is a retained environment failure, not a source-test failure.
