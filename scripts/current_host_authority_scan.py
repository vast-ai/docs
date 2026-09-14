#!/usr/bin/env python3
"""Fail-closed, additive projection from the frozen whole Host scan baseline.

The registry is a reviewed transition instruction, not terminal product evidence.
Previous generators remain the historical validators; this adapter never changes
their phase pins or rewrites their evidence. All filesystem access is read-only.
"""
from __future__ import annotations

from collections import Counter
import copy
import difflib
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from typing import Any, Mapping
from urllib.parse import urlparse

REGISTRY = 'verification/current-host-authority-scan.json'
# Final independent review seals this value. A present but unsealed registry is
# rejected; a checksum stored inside that same registry would not protect it.
REGISTRY_SHA256 = 'a0034595ea679605497106d8a8670bc068559d52441691c4128d7558b50de8c2'
ATTEMPT = 'verification/evidence/2026-09-09-host-authority-scan-attempt-01'
BASELINE = ATTEMPT + '/before-current-host-docs-review.json'
BASELINE_SHA256 = '6dfb73d8d4a4f3f110b1e81adb443db0913dd0ac47a876e0a4519d57bce9ca18'
SNAPSHOT = ATTEMPT + '/source-snapshot-01.json'
SNAPSHOT_SHA256 = 'a090667e08bfc4bcf1a9a85c407965bac686107f4ec6fb75162d5b3a9d6a12d2'
DECISION = 'CURRENT_HOST_AUTHORITY_SCAN_TRANSITION'
RELOCATION = 'CURRENT_HOST_AUTHORITY_SCAN_RELOCATION'
TRANSITION_REASON = ' Exact current source/taxonomy transition is recorded in verification/current-host-authority-scan.json; full previous claim is retained in the frozen scan baseline.'
RELOCATION_REASON = ' Exact unchanged source spans were relocated against the frozen scan source snapshot; no product evidence was added.'
STALE_REASON = ' The previous source span changed in the authority scan; no procedure execution or acceptance transfers.'
LANES = {'CANONICAL_IMPLEMENTATION_SOURCE', 'RUNTIME_OR_UI_OBSERVATION',
         'ACCOUNTABLE_OWNER_CONFIRMATION', 'AUTHORITATIVE_DOCUMENTATION_CITATION',
         'REPOSITORY_STATIC_CHECK', 'PRODUCT_PUBLICATION_SOURCE'}
METHODS = {'TAXONOMY_ONLY', 'EDITORIAL', 'SOURCE_ADJUDICATION',
           'NAVIGATION_RETEST', 'PROVENANCE_DOWNGRADE'}
ARTIFACT_KINDS = {'CONTEXT', 'GOVERNING_SOURCE', 'CANONICAL_SOURCE', 'OBSERVATION', 'STATIC_RETEST'}
SOURCE_LANES = {'CANONICAL_IMPLEMENTATION_SOURCE', 'AUTHORITATIVE_DOCUMENTATION_CITATION', 'PRODUCT_PUBLICATION_SOURCE'}
STATUS = {'UNVALIDATED', 'PASS', 'FAIL', 'BLOCKED', 'NOT_APPLICABLE', 'STALE'}
AFTER_REQUIRED = {'classification', 'status', 'required_evidence_types', 'owner_role', 'rationale', 'next_action'}
AFTER_OPTIONAL = {'text', 'headings', 'spans', 'evidence_refs', 'source_refs'}
VOLUME_DOWNGRADES = {'VOL-C06', 'VOL-C08', 'VOL-C10', 'VOL-C14', 'VOL-C16', 'VOL-C20', 'VOL-C21'}
ADDITIONAL_TAXONOMY_IDS = set('''MCL-dd6ceaa32dd0dc0e MCL-edd5f28e0063df77 MCL-e3c0d6e4e0215c71 MCL-1592c07289fcb2fc CUR-d83c946956b9328a CUR-a0f53a1fa198942f CUR-99fb8d131e321e03 CUR-2ead4eda972e84b0 CUR-b79e1c2e7f6ebf90 MCL-02886603d761ca6c MCL-3b6b597d4d8f4fae MCL-a36d710b5fa47b76 MCL-fabed78e7914587b MCL-97d652cd19c524c1 MCL-94b40aaa6e3660ed MCL-9f1706bb852406b7 MCL-6ca3a2eecf2d8fef MCL-5ab653314f9e68e8 MCL-826a9b5204619d58 MCL-e766e1304f924e4a MCL-8d479c81bf03e837 MCL-5a8901f1b2e4c83e MCL-6f896babd40234bc MCL-5ae1fd277fbd660e MCL-c072275873d06381 MCL-4c9cb86351b449fe MCL-c3ea8c7772c6d5a5 MCL-66f1f7db50c290cf MCL-dbcdd05e71e07521 MCL-80866169a0298a5a MCL-1d8d9f9031c49988 MCL-1f129934b5417646 MCL-fcd20b4aee2e938f MCL-8c06455efca0b382 MCL-6b39ff63388cffbc MCL-bf107c15cc2b058f MCL-d9da265d026893c3 MCL-03c73e4182b1e7fe'''.split())
LINK_RE = re.compile(r'(?<!!)\[[^\]]+\]\(([^)\s]+)(?:\s+[\'\"][^\'\"]*[\'\"])?\)')


def require(condition: Any, message: str) -> None:
    if not condition:
        raise ValueError('Host authority scan: ' + message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def object_digest(value: Any) -> str:
    return digest(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode())


def exact_keys(value: Any, required: set[str], optional: set[str] = frozenset(), name: str = 'record') -> None:
    require(isinstance(value, dict), f'{name} must be an object')
    require(required <= value.keys() and value.keys() <= required | optional, f'{name} has missing/unknown fields')


def safe_path(root: Path, relative: str) -> Path:
    require(isinstance(relative, str) and relative and '\\' not in relative, 'invalid artifact path')
    p = PurePosixPath(relative)
    require(not p.is_absolute() and not any(x in {'', '.', '..'} for x in relative.split('/')), f'unsafe path {relative}')
    base = root.resolve()
    path = base
    for component in p.parts:
        path = path / component
        require(not path.is_symlink(), f'symlink is not an evidence/source target: {relative}')
    require(path.resolve().is_relative_to(base) and path.is_file(), f'missing or escaping path {relative}')
    return path


def pinned_bytes(root: Path, path: str, expected: str) -> bytes:
    require(isinstance(expected, str) and re.fullmatch(r'[0-9a-f]{64}', expected), f'invalid pin for {path}')
    value = safe_path(root, path).read_bytes()
    require(digest(value) == expected, f'hash mismatch for {path}')
    return value


def read_json(data: bytes, name: str) -> dict[str, Any]:
    def pairs(values: list[tuple[str, Any]]) -> dict[str, Any]:
        result = {}
        for key, value in values:
            require(key not in result, f'duplicate JSON key {key} in {name}')
            result[key] = value
        return result
    value = json.loads(data, object_pairs_hook=pairs)
    require(isinstance(value, dict), f'{name} must contain a JSON object')
    return value


def span_text(lines: list[str], span: dict[str, Any]) -> str:
    exact_keys(span, {'source_file', 'start', 'end', 'text_sha256'}, name='span')
    start, end = span['start'], span['end']
    require(type(start) is int and type(end) is int and 1 <= start <= end <= len(lines), 'invalid source span')
    text = '\n'.join(lines[start - 1:end])
    require(digest(text.encode()) == span['text_sha256'], f'source span hash mismatch {span["source_file"]}:{start}')
    return text


def equality_map(before: list[str], after: list[str]) -> dict[int, int]:
    return {a + offset + 1: b + offset + 1
            for a, b, size in difflib.SequenceMatcher(a=before, b=after, autojunk=False).get_matching_blocks()
            for offset in range(size)}


def relocate_span(span: dict[str, Any], sources: dict[str, Any]) -> dict[str, Any] | None:
    require(span['source_file'] in sources, 'span source absent from frozen inventory')
    source = sources[span['source_file']]
    span_text(source['before_lines'], span)
    if not source['changed']:
        return copy.deepcopy(span)
    mapped = [source['map'].get(i) for i in range(span['start'], span['end'] + 1)]
    if None in mapped or mapped != list(range(mapped[0], mapped[-1] + 1)):
        return None
    result = {**span, 'start': mapped[0], 'end': mapped[-1]}
    span_text(source['after_lines'], result)
    return result


def changed_history(value: dict[str, Any], decision: str, reason: str) -> dict[str, Any]:
    prior = copy.deepcopy(value.get('history', {}))
    prior['carry_decision'] = decision
    if 'reason' in prior:
        prior['reason'] = str(prior['reason']) + reason
    return prior


def validate_artifacts(root: Path, entries: list[dict[str, Any]]) -> dict[str, Any]:
    require(isinstance(entries, list), 'artifacts must be an array')
    artifacts: dict[str, Any] = {}
    paths = set()
    for item in entries:
        exact_keys(item, {'id', 'path', 'sha256', 'kind'}, {'origin'}, 'artifact')
        require(isinstance(item['id'], str) and item['id'] and item['id'] not in artifacts, 'duplicate/invalid artifact ID')
        require(item['path'] not in paths and item['kind'] in ARTIFACT_KINDS, 'duplicate artifact path or invalid kind')
        data = pinned_bytes(root, item['path'], item['sha256'])
        artifacts[item['id']] = {**item, '_bytes': data}
        paths.add(item['path'])
    return artifacts


def pointer_text(data: bytes, pointer: str | None) -> str:
    if pointer is None:
        return data.decode('utf-8')
    require(isinstance(pointer, str) and re.fullmatch(r'/(?:sections|excerpts)/[0-9]+/text|/source_text', pointer), 'pointer must select a retained source text field, not metadata')
    value: Any = read_json(data, 'terminal source')
    capture = value
    parent = None
    for part in pointer[1:].split('/'):
        key = part.replace('~1', '/').replace('~0', '~')
        parent = value
        if isinstance(value, list):
            require(key.isdecimal() and int(key) < len(value), 'source pointer outside list')
            value = value[int(key)]
        else:
            require(isinstance(value, dict) and key in value, 'source pointer missing')
            value = value[key]
    require(isinstance(value, str) and value.strip(), 'terminal source pointer must select actual retained text')
    if pointer == '/source_text':
        require(capture.get('source_text_sha256') == digest(value.encode()), 'retained source_text hash missing or mismatched')
    elif isinstance(parent,dict) and 'text_sha256' in parent:
        require(parent['text_sha256'] == digest(value.encode()), 'retained section/excerpt text hash mismatch')
    return value


def terminal_allowed(artifact: dict[str, Any]) -> None:
    path = artifact['path']
    require(not path.startswith(('graphify-out/', '.orchestra/')) and
            '/sources-before/' not in path and 'before-current-' not in path and
            not path.startswith('verification/current-') and
            path not in {REGISTRY, BASELINE, SNAPSHOT, 'verification/host-docs-test-sets.json',
                         'verification/host-docs-test-results.json', 'verification/host-docs-command-scores.json'},
            f'derived model/graph/registry/snapshot cannot be terminal proof: {path}')
    require(artifact['kind'] != 'CONTEXT', 'registry/context-only proof cannot promote a claim')


def verify_basis(entry: dict[str, Any], claim: dict[str, Any], page: dict[str, Any], artifacts: dict[str, Any], root: Path) -> None:
    require(isinstance(entry['basis'], list), 'basis must be an array')
    satisfied: set[str] = set()
    used = set()
    evidence_paths = {e['artifact_ref'] for e in claim['evidence_refs']}
    for basis in entry['basis']:
        exact_keys(basis, {'artifact_id', 'lane', 'support_rationale'}, {'text_pointer', 'excerpt'}, 'basis')
        require(basis['artifact_id'] in artifacts and basis['lane'] in LANES and basis['support_rationale'].strip(), 'invalid basis identity/lane/rationale')
        identity = (basis['artifact_id'], basis['lane'], basis.get('text_pointer'))
        require(identity not in used, 'duplicate proof binding')
        used.add(identity)
        artifact = artifacts[basis['artifact_id']]
        terminal_allowed(artifact)
        require(artifact['path'] in evidence_paths, 'terminal proof missing from claim evidence refs')
        if basis['lane'] == 'REPOSITORY_STATIC_CHECK':
            require(artifact['kind'] == 'STATIC_RETEST' and entry['method'] == 'NAVIGATION_RETEST', 'invalid navigation proof method')
            proof = read_json(artifact['_bytes'], artifact['path'])
            checks = proof.get('checks', [proof])
            require(isinstance(checks, list), 'navigation checks must be an array')
            matches = [c for c in checks if c.get('claim_id') == claim['id']]
            require(len(matches) == 1, 'missing/duplicate exact navigation retest')
            check = matches[0]
            require(check.get('text_sha256') == digest(claim['text'].encode()) and
                    check.get('source_sha256') == page['source_sha256'] and check.get('result') == 'PASS',
                    'navigation retest target/result mismatch')
            links = LINK_RE.findall(claim['text'])
            require(links and all(x.startswith(('/', '#')) for x in links), 'navigation PASS is bounded to local destinations')
            # Resolve independently, not merely by trusting a static report.
            import importlib.util
            spec = importlib.util.spec_from_file_location('scan_nav', root / 'scripts/build_current_host_vv_overlay.py')
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            mod.REPO = root
            require(all(mod.resolve_local_href(page['source_file'], x) for x in links), 'navigation destination does not resolve')
        else:
            require(basis['lane'] in SOURCE_LANES, 'new runtime or owner PASS is outside this transition')
            expected_kind = 'CANONICAL_SOURCE' if basis['lane'] == 'CANONICAL_IMPLEMENTATION_SOURCE' else 'GOVERNING_SOURCE'
            require(artifact['kind'] == expected_kind, 'source kind does not support evidence lane')
            require(isinstance(basis.get('excerpt'), str) and basis['excerpt'].strip(), 'source proof needs retained exact excerpt')
            require(basis['excerpt'] in pointer_text(artifact['_bytes'], basis.get('text_pointer')), 'source excerpt absent from retained origin')
            origin = artifact.get('origin')
            require(isinstance(origin, dict), 'source origin missing')
            if expected_kind == 'GOVERNING_SOURCE':
                exact_keys(origin, {'url'}, name='governing source origin')
                url = urlparse(origin['url'])
                require(url.scheme == 'https' and url.hostname and not url.username and not url.password, 'invalid governing-source URL')
                capture = read_json(artifact['_bytes'], artifact['path'])
                require(capture.get('url') == origin['url'], 'capture origin does not match source')
                require(basis.get('text_pointer') is not None, 'publication proof must select actual captured source text')
                if basis.get('text_pointer') == '/source_text':
                    raw = next((a for a in artifacts.values() if a['path']==capture.get('raw_artifact_ref')),None)
                    require(raw is not None and raw['path'] != artifact['path'] and raw['sha256']==capture.get('raw_artifact_sha256'), 'extracted publication needs separately pinned raw body')
                    terminal_allowed({**raw,'kind':'GOVERNING_SOURCE'})
                    require(isinstance(capture.get('extraction_method'),str) and capture['extraction_method'].strip(), 'source extraction method missing')
                require(any(ref.get('path') == origin['url'] for ref in claim['source_refs']), 'governing source missing from claim sources')
            else:
                exact_keys(origin, {'repository', 'revision', 'path'}, name='canonical source origin')
                require(origin['repository'] not in {'vast-ai/docs', 'docs'} and re.fullmatch(r'[0-9a-f]{40}', origin['revision']), 'canonical product source must be independent and revision-pinned')
                if artifact['path'].endswith('.json'):
                    capture=read_json(artifact['_bytes'],artifact['path'])
                    require(basis.get('text_pointer') is not None and all(capture.get(key)==origin[key] for key in ('repository','revision','path')), 'canonical capture origin or source-text selection mismatch')
                require(any(all(ref.get(key) == origin[key] for key in ('repository', 'revision', 'path')) for ref in claim['source_refs']), 'canonical origin missing from claim sources')
        satisfied.add(basis['lane'])
    if claim['status'] == 'PASS':
        require(entry['method'] in {'SOURCE_ADJUDICATION', 'NAVIGATION_RETEST'}, 'taxonomy/metadata changes cannot promote PASS')
        require(set(claim['required_evidence_types']) and set(claim['required_evidence_types']) <= satisfied, 'PASS has unsatisfied evidence lanes')


def validate_evidence_refs(claim: dict[str, Any], artifacts: dict[str, Any]) -> None:
    by_path = {a['path']: a for a in artifacts.values()}
    require(isinstance(claim.get('evidence_refs'), list) and isinstance(claim.get('source_refs'), list), 'claim source/evidence refs must be arrays')
    for evidence in claim['evidence_refs']:
        require(isinstance(evidence, dict) and isinstance(evidence.get('artifact_ref'), str), 'missing artifact_ref; no model fallback is permitted')
        require(evidence['artifact_ref'] in by_path, 'evidence artifact is missing an independent registry pin: ' + evidence['artifact_ref'])
        require(evidence['artifact_ref'] != REGISTRY and 'current-host-docs-review.json' not in evidence['artifact_ref'], 'current model/scan registry cannot be claim evidence')


def load_inputs(root: Path, frozen_source_overrides: Mapping[str, bytes] | None = None) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    registry = read_json(pinned_bytes(root, REGISTRY, REGISTRY_SHA256), REGISTRY)
    exact_keys(registry, {'schema_version','record_type','generated_at','baseline','source_snapshot','artifacts','source_transitions','transitions'}, name='registry')
    require(registry['schema_version'] == '1.0' and registry['record_type'] == 'HOST_AUTHORITY_SCAN_TRANSITION', 'wrong registry type/version')
    require(registry['baseline'] == {'path':BASELINE,'sha256':BASELINE_SHA256}, 'baseline pin may not be redefined')
    require(registry['source_snapshot'] == {'path':SNAPSHOT,'sha256':SNAPSHOT_SHA256}, 'source snapshot pin may not be redefined')
    baseline = read_json(pinned_bytes(root, BASELINE, BASELINE_SHA256), BASELINE)
    snapshot = read_json(pinned_bytes(root, SNAPSHOT, SNAPSHOT_SHA256), SNAPSHOT)
    artifacts = validate_artifacts(root, registry['artifacts'])
    require(len(baseline['pages']) == 44 and len(baseline['support_layers']) == 33 and sum(len(p['claims']) for p in baseline['pages']) == 2013, 'frozen inventory size mismatch')
    manifest = {m['path']:m['sha256'] for m in baseline['source']['source_manifest']}
    sources = {}
    changes = {}
    require(isinstance(registry['source_transitions'], list), 'source transitions must be an array')
    for item in registry['source_transitions']:
        exact_keys(item, {'path','before_sha256','after_sha256'}, name='source transition')
        require(item['path'] not in changes and item['path'] in manifest, 'duplicate/out-of-scope source transition')
        changes[item['path']] = item
    overrides = dict(frozen_source_overrides or {})
    for item in snapshot['records']:
        exact_keys(item, {'path','sha256','snapshot'}, name='source snapshot item')
        path = item['path']
        require(path not in sources and manifest.get(path) == item['sha256'], 'snapshot inventory/hash mismatch')
        require(item['snapshot'] == ATTEMPT + '/sources-before/' + path, 'snapshot path mismatch')
        before = pinned_bytes(root, item['snapshot'], item['sha256'])
        after = overrides.pop(path) if path in overrides else safe_path(root, path).read_bytes()
        # An override is deliberately restricted to the exact registered
        # authority output.  A later, hash-bound transition may validate its
        # predecessor against that output, but cannot substitute arbitrary
        # source bytes or bypass an authority source transition.
        if frozen_source_overrides is not None and path in frozen_source_overrides:
            expected_override = changes.get(path, {}).get('after_sha256', item['sha256'])
            require(digest(after) == expected_override, 'frozen source override differs from registered authority output ' + path)
        changed = before != after
        if changed:
            require(changes.get(path) == {'path':path,'before_sha256':item['sha256'],'after_sha256':digest(after)}, 'unregistered/tampered current source change ' + path)
        else:
            require(path not in changes, 'redundant source transition ' + path)
        before_lines, after_lines = before.decode().splitlines(), after.decode().splitlines()
        sources[path] = {'before_lines':before_lines,'after_lines':after_lines,'changed':changed,'sha256':digest(after),'map':equality_map(before_lines,after_lines)}
    require(not overrides and set(sources) == set(manifest) and len(sources) == 144, 'incomplete frozen source population')
    # A changed navigation configuration must not silently add/drop Host pages
    # while the producer retains the old denominator.
    docs=read_json(safe_path(root,'docs.json').read_bytes(),'docs.json')
    host_tabs=[tab for tab in docs.get('navigation',{}).get('tabs',[]) if tab.get('tab')=='Host']
    require(len(host_tabs)==1,'expected one current Host navigation tab')
    def routes(value: Any) -> list[str]:
        if isinstance(value,str):
            return ['/'+value.lstrip('/')] if value.startswith('host/') else []
        if isinstance(value,list):
            return [r for child in value for r in routes(child)]
        if isinstance(value,dict):
            return [r for key,child in value.items() if key in {'groups','pages'} for r in routes(child)]
        return []
    primary=[route for route in routes(host_tabs[0]) if not route.startswith(('/host/cli/','/host/sdk/'))]
    require(len(primary)==44 and set(primary)=={p['route'] for p in baseline['pages']},'current Host routes differ from complete frozen inventory')
    return registry, baseline, artifacts, sources


def project(root: Path, frozen_source_overrides: Mapping[str, bytes] | None = None) -> dict[str, Any]:
    """Validate frozen inputs/terminals and derive a complete deterministic model."""
    root = root.resolve()
    registry, baseline, artifacts, sources = load_inputs(root, frozen_source_overrides)
    result = copy.deepcopy(baseline)
    before_claims = {c['id']:c for p in baseline['pages'] for c in p['claims']}
    require(len(before_claims) == 2013, 'duplicate baseline claim ID')
    entries = {}
    require(isinstance(registry['transitions'], list), 'transitions must be an array')
    for entry in registry['transitions']:
        exact_keys(entry, {'claim_id','before_claim_sha256','method','after','basis','review_rationale'}, name='claim transition')
        cid = entry['claim_id']
        require(cid in before_claims and cid not in entries, 'duplicate/unknown claim transition')
        require(entry['before_claim_sha256'] == object_digest(before_claims[cid]), 'previous claim hash mismatch ' + cid)
        require(entry['method'] in METHODS and isinstance(entry['review_rationale'],str) and entry['review_rationale'].strip(), 'invalid transition method/review rationale')
        exact_keys(entry['after'], AFTER_REQUIRED, AFTER_OPTIONAL, 'after claim fields')
        entries[cid] = entry
    require(VOLUME_DOWNGRADES <= entries.keys(), 'seven known Volume scope overclaims must be corrected explicitly')
    owners = {cid for cid, claim in before_claims.items() if 'ACCOUNTABLE_OWNER_CONFIRMATION' in claim['required_evidence_types']}
    require(len(owners)==331 and owners | ADDITIONAL_TAXONOMY_IDS <= entries.keys(), 'all331 owner claims and38 adjacent taxonomy discoveries need explicit dispositions')
    for page in result['pages']:
        source = sources[page['source_file']]
        page_changed = source['changed'] or any(sources[d['source_file']]['changed'] for d in page['dependencies'])
        page['source_sha256'] = source['sha256']
        if page_changed:
            page['coverage_state'] = 'CHANGED'
        for dep in page['dependencies']:
            dep['source_sha256'] = sources[dep['source_file']]['sha256']
        for claim in page['claims']:
            old = before_claims[claim['id']]
            entry = entries.get(claim['id'])
            relocation = [relocate_span(s, sources) for s in old['spans']]
            if entry:
                claim.update(copy.deepcopy(entry['after']))
                require(all(isinstance(claim[key],str) and claim[key].strip() for key in ('classification','owner_role','rationale','next_action','text')), 'empty/malformed transition text fields')
                if 'spans' not in entry['after']:
                    require(None not in relocation, 'edited occurrence needs explicit after spans ' + claim['id'])
                    claim['spans'] = relocation
                require(claim['status'] in STATUS and isinstance(claim['required_evidence_types'],list) and
                        len(set(claim['required_evidence_types'])) == len(claim['required_evidence_types']) and
                        set(claim['required_evidence_types']) <= LANES, 'invalid status/evidence lanes ' + claim['id'])
                if entry['method'] == 'EDITORIAL':
                    require(claim['status'] == 'NOT_APPLICABLE' and not claim['required_evidence_types'] and not entry['basis'], 'editorial transition must be bounded N/A')
                elif entry['method'] in {'TAXONOMY_ONLY','PROVENANCE_DOWNGRADE'}:
                    require(claim['status'] not in {'PASS','NOT_APPLICABLE'}, 'taxonomy/provenance alone cannot clear a claim')
                if claim['id'] in VOLUME_DOWNGRADES:
                    require(entry['method']=='PROVENANCE_DOWNGRADE' and claim['status']=='UNVALIDATED' and
                            'CANONICAL_IMPLEMENTATION_SOURCE' in claim['required_evidence_types'] and
                            claim['evidence_refs'] and all('PARTIAL' in e.get('role','') for e in claim['evidence_refs']), 'Volume downgrade must retain narrow proof as PARTIAL')
                    require(all(any({k:v for k,v in previous.items() if k not in {'role','limit'}} ==
                                    {k:v for k,v in current.items() if k not in {'role','limit'}}
                                    for current in claim['evidence_refs'])
                                for previous in old['evidence_refs']),
                            'Volume downgrade cannot replace or discard the retained narrow proof identity')
                claim['history'] = changed_history(old, DECISION, TRANSITION_REASON)
                claim['coverage_state'] = page['coverage_state']
            else:
                require(None not in relocation, 'unregistered source occurrence change ' + claim['id'])
                claim['spans'] = relocation
                if page_changed or relocation != old['spans']:
                    claim['coverage_state'] = 'CHANGED'
                    claim['history'] = changed_history(old, RELOCATION, RELOCATION_REASON)
            require(isinstance(claim['spans'],list) and claim['spans'], 'claim has no current source occurrence')
            raw_parts = []
            for span in claim['spans']:
                require(span['source_file'] in sources, 'unregistered source in claim span')
                raw_parts.append(span_text(sources[span['source_file']]['after_lines'],span))
            if entry and claim['text'] != old['text']:
                require('spans' in entry['after'] and claim['text'] == '\n'.join(raw_parts), 'changed literal must exactly equal its current source span(s)')
            elif entry and 'spans' in entry['after']:
                old_parts = [span_text(sources[s['source_file']]['before_lines'],s) for s in old['spans']]
                require(raw_parts == old_parts, 'unchanged literal cannot be rebound to different source text')
            validate_evidence_refs(claim,artifacts)
            if entry:
                verify_basis(entry,claim,page,artifacts,root)
        if page_changed:
            for procedure in page['procedures']:
                for node in [procedure,*procedure['nodes']]:
                    old_spans=node.get('spans',[])
                    relocated=[relocate_span(s,sources) for s in old_spans]
                    if None in relocated:
                        node['spans']=[]
                        node['status']='STALE'
                        node['coverage_state']='CHANGED'
                        node['limits']=[*node.get('limits',[]),STALE_REASON.strip()]
                        node['history']=changed_history(node,'CURRENT_HOST_AUTHORITY_SCAN_SOURCE_CHANGED',STALE_REASON)
                    else:
                        node['spans']=relocated
                        node['coverage_state']='CHANGED'
                        node['history']=changed_history(node,RELOCATION,RELOCATION_REASON)
    for support in result['support_layers']:
        for key in ('source_file','fragment_file','central_reference_file'):
            require(not sources[support[key]]['changed'], 'support-layer edits need their own explicit transition')
        validate_evidence_refs({'evidence_refs':support['evidence_refs'],'source_refs':[]},artifacts)
    for item in result['source']['source_manifest']:
        item['sha256']=sources[item['path']]['sha256']
    claims=[c for p in result['pages'] for c in p['claims']]
    require(len(claims)==2013 and {c['id'] for c in claims} == set(before_claims), 'full inventory preservation failed')
    covered: dict[str,set[int]]={path:set() for path in sources}
    for claim in claims:
        for span in claim['spans']:
            covered[span['source_file']].update(range(span['start'],span['end']+1))
    for path,source in sources.items():
        if not source['changed']:
            continue
        for kind,_a,_b,start,end in difflib.SequenceMatcher(a=source['before_lines'],b=source['after_lines'],autojunk=False).get_opcodes():
            if kind in {'insert','replace'}:
                require(all(not source['after_lines'][line].strip() or line+1 in covered[path] for line in range(start,end)),
                        'new nonblank source lines are outside the reconciled claim inventory: '+path)
    dangerous=next(c for c in claims if c['id']=='MCL-17c8031cb2c7e34a')
    require(dangerous['status']!='PASS' or 'why terms lock' not in dangerous['text'], 'unsupported contract lock semantics remain passing navigation')
    result['counts']['claim_statuses']=dict(sorted(Counter(c['status'] for c in claims).items()))
    result['counts']['page_coverage_states']=dict(sorted(Counter(p['coverage_state'] for p in result['pages']).items()))
    result['generated_at']=registry['generated_at']
    result['history']['authority_scan']={'registry':REGISTRY,'registry_sha256':REGISTRY_SHA256,'baseline':registry['baseline'],'source_snapshot':registry['source_snapshot'],'limit':'Integrity and transition provenance only; not terminal product proof.'}
    result['corrections'].append({'id':'HOST-AUTHORITY-SOURCE-FIRST-SCAN-01','scope':'44 primary Host pages; all2013 claim IDs retained','history':'Frozen full before model and all144 source snapshots remain immutable.','current':f'{len(entries)} exact reviewed transitions; no taxonomy-only PASS.','reason':'Existing independent source authority precedes any genuine decision escalation; narrow retained proof does not validate broader claims.'})
    return result


def validate_model(model: dict[str, Any], root: Path, frozen_source_overrides: Mapping[str, bytes] | None = None) -> None:
    require(model == project(root, frozen_source_overrides), 'current model differs from the complete independently derived transition projection')


def classify_occurrence(root: Path, source_file: str, text: str) -> tuple[str, list[str], bool]:
    """Shared current classification; only exact reviewed source-bound records.

    Unknown or ambiguous text fails closed instead of inheriting a heading's
    policy words. Historical extraction remains available in the old adapter.
    """
    model = project(root)
    matches=[c for p in model['pages'] for c in p['claims'] if c['text']==text and any(s['source_file']==source_file for s in c['spans'])]
    require(matches, 'current classification has no exact reviewed occurrence')
    values={(c['classification'],tuple(c['required_evidence_types'])) for c in matches}
    require(len(values)==1, 'same literal has differing contextual classifications; select exact claim ID')
    classification,lanes=next(iter(values))
    return classification,list(lanes),'AUTHORITATIVE_DOCUMENTATION_CITATION' in lanes
