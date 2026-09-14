#!/usr/bin/env python3
"""Fail-closed editorial cleanup projection above the jurisdiction baseline.

This layer records only claim-specific, repository-local editorial checks.  It
does not execute Host operations or convert a source classification alone into
product evidence.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path
from typing import Any

REGISTRY = 'verification/current-host-review-cleanup.json'
# Set to the frozen registry digest when the independently reviewed proposal is
# sealed.  An empty value is permitted only while no cleanup registry exists.
REGISTRY_SHA256 = 'ae2c8781c9d0d806818649052ad9bace4e8e6e9cf0b08e61f1d797049c20906c'
ATTEMPT = 'verification/evidence/2026-09-11-host-review-cleanup-attempt-01'
BASELINE = ATTEMPT + '/before-current-host-docs-review.json'
BASELINE_SHA256 = 'f18e61882f50a2785f2fe863aba88ecf3d79af8a45bdcbf1596e6e64c6b7059d'
MARKER = 'HOST-REVIEW-CLEANUP-01'
DECISION = 'CURRENT_HOST_REVIEW_CLEANUP'
STATIC = 'REPOSITORY_STATIC_CHECK'
EDITORIAL = {'EDITORIAL_SCOPE_OR_LEAD_IN', 'EDITORIAL_NAVIGATION_PREAMBLE'}
STATIC_CLASSES = {'REVIEWED_ADVICE', 'REVIEWED_NAVIGATION_INSTRUCTION', 'REVIEWED_EXAMPLE_CALCULATION'}
METHODS = {'MARKUP_OR_PREAMBLE_INSPECTION', 'CONTEXTUAL_INSPECTION', 'LOCAL_NAVIGATION_CHECK', 'ARITHMETIC_CHECK', 'MIXED_REPOSITORY_LOCAL_EDITORIAL_CHECKS'}
AFTER = {'classification', 'status', 'required_evidence_types', 'owner_role', 'rationale', 'next_action', 'evidence_refs', 'source_refs'}


def require(ok: Any, message: str) -> None:
    if not ok:
        raise ValueError('cleanup: ' + message)


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def objhash(value: Any) -> str:
    return digest(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode())


def module(name: str):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(name + '.py'))
    result = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(result)
    return result


def safe(root: Path, ref: str) -> Path:
    require(isinstance(ref, str) and ref and not ref.startswith('/') and '\\' not in ref and all(p not in {'', '.', '..'} for p in ref.split('/')), 'unsafe path')
    path = root.resolve()
    for part in ref.split('/'):
        path /= part
        require(not path.is_symlink(), 'unsafe symlink')
    require(path.is_file() and path.resolve().is_relative_to(root.resolve()), 'missing path ' + ref)
    return path


def pinned(root: Path, ref: str, wanted: str) -> bytes:
    value = safe(root, ref).read_bytes()
    require(digest(value) == wanted, 'digest drift ' + ref)
    return value


def decode(value: bytes) -> dict[str, Any]:
    result = json.loads(value)
    require(isinstance(result, dict), 'JSON object required')
    return result


def keys(value: Any, expected: set[str]) -> None:
    require(isinstance(value, dict) and set(value) == expected, 'missing/unknown fields')


def predecessor(root: Path, baseline: dict[str, Any]) -> None:
    jurisdiction = module('current_host_jurisdiction')
    jurisdiction.validate_model(baseline, root)


def correction(count: int) -> dict[str, str]:
    return {
        'id': MARKER,
        'scope': f'{count} exact editorial/navigation/calculation cleanup transitions',
        'history': 'The sealed jurisdiction predecessor is hash-pinned. Original claim text, spans, statuses, sources and evidence remain available.',
        'current': f'{count} individually observed repository-local editorial checks; no Host, API, SSH, credentialed, paid or mutating operation was run.',
        'reason': 'A completed navigation, arithmetic or contextual editorial inspection is limited to the documented passage. It does not establish product behavior, a runtime result, policy enforcement or human acceptance.',
    }


def project(root: Path) -> dict[str, Any]:
    root = root.resolve()
    require(REGISTRY_SHA256, 'cleanup registry digest not sealed')
    registry_bytes = pinned(root, REGISTRY, REGISTRY_SHA256)
    registry_sha256 = REGISTRY_SHA256
    registry = decode(registry_bytes)
    keys(registry, {'schema_version', 'record_type', 'generated_at', 'baseline', 'artifacts', 'transitions', 'result_ref'})
    require(registry['schema_version'] == '1.0' and registry['record_type'] == 'HOST_REVIEW_CLEANUP_TRANSITION', 'wrong registry type')
    require(registry['baseline'] == {'path': BASELINE, 'sha256': BASELINE_SHA256}, 'baseline substitution')
    require(isinstance(registry['result_ref'], str) and registry['result_ref'].startswith(ATTEMPT + '/') and safe(root, registry['result_ref']).is_file(), 'invalid result reference')
    baseline = decode(pinned(root, BASELINE, BASELINE_SHA256))
    predecessor(root, baseline)

    artifacts: dict[str, tuple[dict[str, Any], dict[str, Any]]] = {}
    for artifact in registry['artifacts']:
        keys(artifact, {'id', 'path', 'sha256', 'method'})
        aid = artifact['id']
        require(isinstance(aid, str) and aid and aid not in artifacts and artifact['method'] in METHODS, 'invalid artifact')
        require(isinstance(artifact['path'], str) and artifact['path'].startswith(ATTEMPT + '/'), 'artifact outside cleanup attempt')
        capture = decode(pinned(root, artifact['path'], artifact['sha256']))
        keys(capture, {'schema_version', 'record_type', 'generated_at', 'baseline', 'method', 'limits', 'source_candidate', 'support_artifacts', 'observations'})
        require(capture['schema_version'] == '1.0' and capture['record_type'] == 'HOST_REVIEW_CLEANUP_LOCAL_CHECKS', 'wrong cleanup capture')
        require(capture['baseline'] == registry['baseline'] and capture['method'] == artifact['method'], 'capture baseline/method drift')
        require(isinstance(capture['limits'], str) and capture['limits'].strip(), 'capture limits required')
        require(isinstance(capture['observations'], list), 'capture observations required')
        keys(capture['source_candidate'], {'path', 'sha256'})
        candidate = decode(pinned(root, capture['source_candidate']['path'], capture['source_candidate']['sha256']))
        require(candidate.get('record_type') == 'HOST_EDITORIAL_INSPECTION_CANDIDATES' and candidate.get('baseline') == registry['baseline'] and isinstance(candidate.get('records'), list), 'raw independent candidate drift')
        require(isinstance(capture['support_artifacts'], list), 'support artifacts required')
        for support in capture['support_artifacts']:
            keys(support, {'path', 'sha256'})
            pinned(root, support['path'], support['sha256'])
        artifacts[aid] = (artifact, capture, {item.get('claim_id'): item for item in candidate['records']})

    before = {claim['id']: claim for page in baseline['pages'] for claim in page['claims']}
    result = copy.deepcopy(baseline)
    after = {claim['id']: claim for page in result['pages'] for claim in page['claims']}
    seen: set[str] = set()
    allowed_statuses = {'PASS', 'NOT_APPLICABLE'}
    for entry in registry['transitions']:
        keys(entry, {'claim_id', 'before_sha256', 'artifact_id', 'observation_id', 'after', 'review_rationale', 'limits'})
        cid = entry['claim_id']
        require(cid in before and cid not in seen and entry['before_sha256'] == objhash(before[cid]), 'claim identity/predecessor drift')
        seen.add(cid)
        prior, claim = before[cid], after[cid]
        require(prior['status'] == 'UNVALIDATED', 'only known selected UNVALIDATED claims may transition')
        keys(entry['after'], AFTER)
        claim.update(copy.deepcopy(entry['after']))
        require(claim['status'] in allowed_statuses | {'UNVALIDATED'}, 'only PASS, NOT_APPLICABLE or scoped UNVALIDATED cleanup status')
        require(claim['text'] == prior['text'] and claim['headings'] == prior['headings'] and claim['spans'] == prior['spans'], 'source literal/span mutation')
        require(all(ref in claim['evidence_refs'] for ref in prior['evidence_refs']) and all(ref in claim['source_refs'] for ref in prior['source_refs']), 'prior evidence/source dropped')
        require(entry['artifact_id'] in artifacts, 'missing cleanup artifact')
        artifact, capture, candidates = artifacts[entry['artifact_id']]
        observation = next((item for item in capture['observations'] if item.get('id') == entry['observation_id']), None)
        keys(observation, {'id', 'claim_id', 'before_sha256', 'text', 'text_sha256', 'source_file', 'source_sha256', 'spans', 'method', 'result', 'finding', 'limits', 'context', 'expected', 'observed', 'links', 'arithmetic', 'candidate_record'})
        require(prior['spans'] and all(span['source_file'] == prior['spans'][0]['source_file'] for span in prior['spans']), 'cleanup spans must be in one exact source file')
        source_file = prior['spans'][0]['source_file']
        require(observation['claim_id'] == cid and observation['before_sha256'] == entry['before_sha256'] and observation['text'] == prior['text'] and observation['text_sha256'] == digest(prior['text'].encode()), 'observation claim identity drift')
        require(observation['source_file'] == source_file and observation['spans'] == prior['spans'] and observation['source_sha256'] == digest(safe(root, source_file).read_bytes()), 'observation source/span drift')
        require(observation['method'] in METHODS and artifact['method'] == 'MIXED_REPOSITORY_LOCAL_EDITORIAL_CHECKS' and observation['finding'] == entry['review_rationale'] and observation['limits'] == entry['limits'], 'observation rationale/limits drift')
        require(observation['candidate_record'] == candidates.get(cid), 'raw candidate record substitution')
        current_source = safe(root, source_file).read_text()
        require(isinstance(observation['context'], str) and observation['context'] in current_source and isinstance(observation['expected'], str) and observation['expected'].strip() and isinstance(observation['observed'], str) and observation['observed'].strip(), 'raw contextual expected/observed evidence missing')
        require(isinstance(observation['links'], list), 'navigation evidence must be a list')
        require(isinstance(entry['review_rationale'], str) and entry['review_rationale'].strip() and isinstance(entry['limits'], str) and entry['limits'].strip(), 'rationale/limits required')
        if claim['status'] == 'NOT_APPLICABLE':
            require(claim['classification'] in EDITORIAL and claim['required_evidence_types'] == [] and observation['method'] == 'MARKUP_OR_PREAMBLE_INSPECTION' and observation['result'] == 'NOT_APPLICABLE' and observation['arithmetic'] is None, 'invalid editorial non-claim closure')
        else:
            require(claim['classification'] in STATIC_CLASSES and claim['required_evidence_types'] == [STATIC] and observation['method'] in {'CONTEXTUAL_INSPECTION', 'LOCAL_NAVIGATION_CHECK', 'ARITHMETIC_CHECK'} and observation['result'] == ('PASS' if claim['status'] == 'PASS' else 'UNVALIDATED'), 'invalid bounded static closure')
            require(any(ref.get('artifact_ref') == artifact['path'] for ref in claim['evidence_refs']), 'selected static evidence missing')
            if observation['method'] == 'LOCAL_NAVIGATION_CHECK':
                require(observation['links'] and observation['arithmetic'] is None and all(isinstance(item, dict) and set(item) == {'href', 'destination', 'result'} and item['result'] == 'PASS' for item in observation['links']), 'exact local navigation observation required')
            elif observation['method'] == 'ARITHMETIC_CHECK':
                require(not observation['links'] and isinstance(observation['arithmetic'], dict) and set(observation['arithmetic']) == {'inputs', 'formula', 'expected', 'observed'} and observation['arithmetic']['expected'] == observation['arithmetic']['observed'], 'exact arithmetic observation required')
            else:
                require(not observation['links'] and observation['arithmetic'] is None, 'contextual inspection must not pose as link/arithmetic proof')
            if claim['status'] == 'UNVALIDATED':
                require(observation['method'] == 'CONTEXTUAL_INSPECTION' and claim['rationale'] != prior['rationale'] and claim['next_action'] != prior['next_action'], 'unvalidated cleanup needs exact current rationale and next action')
        claim['history'] = {**prior['history'], 'carry_decision': DECISION, 'reason': prior['history'].get('reason', '') + ' Exact repository-local cleanup observation; no product/runtime or human-acceptance result is inferred.'}
        claim['coverage_state'] = 'CHANGED'
    require(seen, 'empty cleanup registry is not an additive transition')
    require(len(before) - sum(before[cid] == after[cid] for cid in before) == len(seen), 'unrelated claim drift')
    result['counts']['claim_statuses'] = dict(sorted(Counter(item['status'] for item in after.values()).items()))
    result['generated_at'] = registry['generated_at']
    result['corrections'].append(correction(len(seen)))
    return result


def validate_model(model: dict[str, Any], root: Path) -> None:
    require(model == project(root), 'whole model differs from cleanup projection')


def load_cleanup(root: Path, model: dict[str, Any]) -> dict[str, Any] | None:
    present = (root / REGISTRY).is_file()
    marked = any(item.get('id') == MARKER for item in model.get('corrections', []))
    if not present:
        require(not marked, 'cleanup-marked model has no registry')
        return None
    validate_model(model, root)
    registry = decode(pinned(root, REGISTRY, REGISTRY_SHA256))
    return {'registry': registry, 'registry_sha256': REGISTRY_SHA256}
