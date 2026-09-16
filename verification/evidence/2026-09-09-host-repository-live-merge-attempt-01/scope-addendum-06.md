# Python cache publication guard — addendum 06

PUB-03: The new Python regression execution produces __pycache__ directories.
An actual git check-ignore returned exit1 for a script cache path, meaning it
remains accidentally stageable. Add only the standard __pycache__/ directory
rule and a regression for a nested cache file. Keep source, verification
artifacts and the user's pre-existing tracked files unchanged; no deletion or
untracking is part of this fix.
