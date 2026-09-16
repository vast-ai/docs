#!/usr/bin/env python3
"""Pinned additive reader for bounded Host-review clarification transitions.

The registry is review provenance, never product evidence.  It first validates
the frozen phase-43 predecessor through the existing authority reader, then
applies only hash-bound classification/evidence-method/action corrections.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any, Callable

REGISTRY = "verification/current-host-clarification.json"
REGISTRY_SHA256 = "528460ae02f689bc1e6a3469af6fcb058073197a853611c72ec78a6473b3f66f"
ATTEMPT = "verification/evidence/2026-09-10-host-clarification-sweep-attempt-01"
BASELINE = ATTEMPT + "/before-review.json"
BASELINE_SHA256 = "f1e6086481a372131db5f786c3ab390169bd7620b25a6fa37d033baf5cb779a7"
MARKER = "HOST-REVIEW-CLARIFICATION-SWEEP-01"
CLAIM_FIELDS = {"classification", "required_evidence_types", "owner_role", "rationale", "next_action"}
METHODS = {"ADVICE_REVIEW", "ADVICE_WITH_FACTUAL_INPUTS", "POLICY_SOURCE", "POLICY_ACKNOWLEDGEMENT", "STATIC_CHECK", "TECHNICAL_SOURCE", "MIXED", "SETUP_INSTRUCTION"}
EVIDENCE = {"CANONICAL_IMPLEMENTATION_SOURCE", "RUNTIME_OR_UI_OBSERVATION", "ACCOUNTABLE_OWNER_CONFIRMATION", "AUTHORITATIVE_DOCUMENTATION_CITATION", "REPOSITORY_STATIC_CHECK", "PRODUCT_PUBLICATION_SOURCE"}


def require(value: Any, message: str) -> None:
    if not value:
        raise ValueError("clarification transition: " + message)


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: canonical(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return [canonical(item) for item in value]
    return value


def canonical_hash(value: Any) -> str:
    return digest(json.dumps(canonical(value), separators=(",", ":"), ensure_ascii=False).encode())


def read_json(bytes_value: bytes, name: str) -> dict[str, Any]:
    try:
        value = json.loads(bytes_value)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError(f"clarification transition: invalid JSON {name}: {error}") from error
    require(isinstance(value, dict), f"{name} must be an object")
    return value


def safe(root: Path, ref: str) -> Path:
    require(isinstance(ref, str) and ref and not ref.startswith("/"), "unsafe path")
    candidate = root / ref
    current = root
    for component in Path(ref).parts:
        require(component not in {"", ".", ".."}, "unsafe path")
        current /= component
        require(not current.is_symlink(), "unsafe path")
    path = candidate.resolve()
    require(path.is_relative_to(root.resolve()), "unsafe path")
    return path


def pinned(root: Path, ref: str, expected: str) -> bytes:
    require(isinstance(expected, str) and len(expected) == 64 and all(c in "0123456789abcdef" for c in expected), "invalid pin")
    value = safe(root, ref).read_bytes()
    require(digest(value) == expected, "digest drift: " + ref)
    return value


def exact_keys(value: Any, required: set[str], optional: set[str] = frozenset(), name: str = "record") -> None:
    require(isinstance(value, dict) and set(value) == required | optional, "invalid " + name + " fields")


def phase43(root: Path, predecessor: dict[str, Any]) -> Any:
    spec = importlib.util.spec_from_file_location("clarification_phase43", Path(__file__).with_name("current_host_authority_scan.py"))
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    module.validate_model(predecessor, root)
    return module


def _nonempty_after(after: dict[str, Any]) -> None:
    require(after and set(after) <= CLAIM_FIELDS, "unauthorized claim patch fields")
    for key, value in after.items():
        if key == "required_evidence_types":
            require(isinstance(value, list) and value and len(value) == len(set(value)) and set(value) <= EVIDENCE, "invalid evidence enum")
        else:
            require(isinstance(value, str) and value.strip(), "empty claim patch field " + key)


def _index(model: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    claims, procedures, nodes = {}, {}, {}
    for page in model["pages"]:
        for procedure in page["procedures"]:
            require(procedure["id"] not in procedures, "duplicate predecessor procedure ID")
            procedures[procedure["id"]] = procedure
            for node in procedure["nodes"]:
                require(node["id"] not in nodes, "duplicate predecessor node ID")
                nodes[node["id"]] = node
        for claim in page["claims"]:
            require(claim["id"] not in claims, "duplicate predecessor claim ID")
            claims[claim["id"]] = claim
    return claims, procedures, nodes


def project(root: Path, phase43_validate: Callable[[Path, dict[str, Any]], Any] = phase43) -> dict[str, Any]:
    root = root.resolve()
    registry_bytes = pinned(root, REGISTRY, REGISTRY_SHA256)
    registry = read_json(registry_bytes, REGISTRY)
    exact_keys(registry, {"schema_version", "record_type", "generated_at", "baseline", "claims", "nodes", "procedures"}, name="registry")
    require(registry["schema_version"] == "1.0" and registry["record_type"] == "HOST_REVIEW_CLARIFICATION_TRANSITION", "wrong registry type")
    require(isinstance(registry["generated_at"], str) and registry["generated_at"].strip(), "missing generation time")
    require(registry["baseline"] == {"path": BASELINE, "sha256": BASELINE_SHA256}, "baseline substitution")
    predecessor = read_json(pinned(root, BASELINE, BASELINE_SHA256), BASELINE)
    # This is intentionally before every patch.  Clarification cannot mask an
    # authority/phase-43 integrity failure in its predecessor.
    phase43_validate(root, predecessor)
    claims, procedures, nodes = _index(predecessor)
    result = copy.deepcopy(predecessor)
    projected_claims, projected_procedures, projected_nodes = _index(result)
    seen: set[str] = set()
    for entry in registry["claims"]:
        exact_keys(entry, {"claim_id", "before_sha256", "review_method", "review_rationale", "after"}, name="claim transition")
        cid = entry["claim_id"]
        require(isinstance(cid, str) and cid in claims and cid not in seen, "missing/duplicate claim ID")
        require(entry["before_sha256"] == canonical_hash(claims[cid]), "claim predecessor drift: " + cid)
        require(claims[cid]["status"] not in {"PASS", "NOT_APPLICABLE"}, "PASS/N/A claim method/source remains exact: " + cid)
        require(entry["review_method"] in METHODS and isinstance(entry["review_rationale"], str) and entry["review_rationale"].strip(), "invalid claim review method/rationale")
        _nonempty_after(entry["after"])
        prior = claims[cid]
        if prior["status"] == "FAIL" and "AUTHORITATIVE_DOCUMENTATION_CITATION" in prior["required_evidence_types"]:
            require("required_evidence_types" not in entry["after"] or "AUTHORITATIVE_DOCUMENTATION_CITATION" in entry["after"]["required_evidence_types"], "FAIL citation lane removed: " + cid)
        if prior["status"] == "BLOCKED":
            for field in ("classification", "required_evidence_types", "rationale", "next_action"):
                require(field not in entry["after"] or entry["after"][field] == prior[field], "BLOCKED prerequisite changed: " + cid)
        projected_claims[cid].update(copy.deepcopy(entry["after"]))
        seen.add(cid)
    for collection, original, projected, label in ((registry["nodes"], nodes, projected_nodes, "node"), (registry["procedures"], procedures, projected_procedures, "procedure")):
        seen_ids: set[str] = set()
        for entry in collection:
            exact_keys(entry, {f"{label}_id", "before_sha256", "next_action"}, name=label + " transition")
            identifier = entry[f"{label}_id"]
            require(isinstance(identifier, str) and identifier in original and identifier not in seen_ids, "missing/duplicate " + label + " ID")
            require(entry["before_sha256"] == canonical_hash(original[identifier]), label + " predecessor drift: " + identifier)
            require(isinstance(entry["next_action"], str) and entry["next_action"].strip(), "empty " + label + " next action")
            require(original[identifier].get("status") not in {"PASS", "NOT_APPLICABLE"}, label + " is not unresolved/STALE: " + identifier)
            projected[identifier]["next_action"] = entry["next_action"]
            seen_ids.add(identifier)
    result["generated_at"] = registry["generated_at"]
    result["corrections"].append({"id": MARKER, "scope": "Bounded clarification transition", "history": "Frozen phase-43 predecessor is hash-pinned and validated before patch projection.", "current": f"{len(seen)} exact claim review-method corrections; {len(registry['nodes'])} node and {len(registry['procedures'])} procedure next-action corrections; registry SHA-256 {REGISTRY_SHA256}.", "reason": "Review-method/action provenance only; no status, source, citation, evidence, span, or runtime-proof transition is authorized."})
    return result


def validate_model(model: dict[str, Any], root: Path, phase43_validate: Callable[[Path, dict[str, Any]], Any] = phase43) -> None:
    require(model == project(root, phase43_validate), "whole model differs from clarification projection")


def load_clarification(root: Path, model: dict[str, Any], phase43_validate: Callable[[Path, dict[str, Any]], Any] = phase43) -> dict[str, Any] | None:
    present = safe(root, REGISTRY).is_file()
    marked = any(item.get("id") == MARKER for item in model.get("corrections", []))
    if not present:
        require(not marked, "missing registry for clarified model")
        return None
    validate_model(model, root, phase43_validate)
    return {"registry": read_json(pinned(root, REGISTRY, REGISTRY_SHA256), REGISTRY), "registry_sha256": REGISTRY_SHA256, "baseline": BASELINE, "baseline_sha256": BASELINE_SHA256}
