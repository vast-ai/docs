"""Read-only comparison of the authorized four owner-label display changes."""
import base64
import gzip
import hashlib
import json
import re
from pathlib import Path

attempt = Path(__file__).resolve().parent
root = attempt.parents[2]
before = json.loads((attempt / "renderer-owner-display-before.json").read_text())
html = (root / "verification/host-docs-review.html").read_bytes()
envelope = json.loads(re.search(
    rb'<script id="report-data" type="application/json">([\s\S]*?)</script>', html
).group(1))
payload = json.loads(gzip.decompress(base64.b64decode(envelope["data"])))
claims = {claim["id"]: claim for claim in payload["claims"]}
ids = {claim["id"] for claim in before["claims"]}
assert len(ids) == 4
for previous in before["claims"]:
    current = claims[previous["id"]]
    assert current["owner_role"] == "Host Product/Engineering owner", current["id"]
    assert current["text"] == previous["text"], current["id"]
    assert current["status"] == previous["status"] == "UNVALIDATED", current["id"]
other_owners = {key: claim["owner_role"] for key, claim in claims.items() if key not in ids}
canonical = json.dumps(other_owners, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
assert hashlib.sha256(canonical).hexdigest() == before["other_owner_labels_sha256"]
assert payload["counts"]["claim_statuses"] == before["counts"]
assert sorted(row["claimId"] for row in payload["issues"]["sourceFollowUps"]) == before["source_followup_ids"]
model_path = root / "verification/current-host-docs-review.json"
registry_path = root / "verification/current-host-evidence-reuse-review.json"
assert hashlib.sha256(model_path.read_bytes()).hexdigest() == "e376445856232f6a41f1b68ac3e01ee173590390cae8768c4392361bc04cc235"
assert hashlib.sha256(registry_path.read_bytes()).hexdigest() == "0b861b45f54eae3b646480818b147b1936cfed698b750c4b4dc7720d574606e7"
model = json.loads(model_path.read_text())
actual = {claim["id"]: claim for page in model["pages"] for claim in page["claims"]}
for key in ids:
    assert claims[key]["owner_role"] == actual[key]["owner_role"]
result = {
    "result": "PASS",
    "scope": "Four authorized owner-role display corrections only; no UI code change or new runtime evidence.",
    "claim_ids": sorted(ids),
    "owner_role": "Host Product/Engineering owner",
    "other_owner_labels_unchanged": len(other_owners),
    "selected_literals_and_statuses_unchanged": True,
    "counts_unchanged": True,
    "source_followup_ids_unchanged": True,
    "html_sha256": hashlib.sha256(html).hexdigest(),
    "html_bytes": len(html),
    "model_sha256": hashlib.sha256(model_path.read_bytes()).hexdigest(),
    "registry_sha256": hashlib.sha256(registry_path.read_bytes()).hexdigest(),
}
print(json.dumps(result, indent=2))
