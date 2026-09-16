#!/usr/bin/env python3
"""Independently check frozen claim identity and the proposed evidence bindings."""
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parent
ROOT = ATTEMPT.parents[2]
sha = lambda raw: hashlib.sha256(raw).hexdigest()


def select(raw, pointer):
    if pointer.startswith('/lines/'):
        match = re.fullmatch(r'/lines/(\d+)-(\d+)', pointer)
        assert match, pointer
        start, end = map(int, match.groups())
        lines = raw.decode().splitlines()
        assert 0 < start <= end <= len(lines), pointer
        return '\n'.join(lines[start - 1:end])
    value = json.loads(raw)
    for part in pointer.split('/')[1:]:
        part = part.replace('~1', '/').replace('~0', '~')
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value


def main():
    inventory = json.loads((ATTEMPT / 'inventory.json').read_text())
    assert sha((ATTEMPT / 'inventory.json').read_bytes()) == '4c9abd5c7feecad626ddd458d994f6f243973550802cce2881628e6857ea64ac'
    frozen = {item['id']: item for item in inventory['claims']}
    lanes = sys.argv[1:] or ['a-policy-account', 'b-hardware-install', 'c-operations-verification']
    output = []
    for lane in lanes:
        folder = ATTEMPT / lane
        raw = (folder / 'decisions.json').read_bytes()
        doc = json.loads(raw)
        decisions = doc['decisions']
        sources_raw = (folder / 'sources.json').read_bytes()
        sources = json.loads(sources_raw)['sources']
        expected = {cid for cid, item in frozen.items() if item['lane'] == lane}
        assert len(decisions) == len(expected)
        assert {item['id'] for item in decisions} == expected
        selections = set()
        for decision in decisions:
            cid = decision['id']
            assert decision['literal_sha256'] == frozen[cid]['literal_sha256'], cid
            assert decision['support_rationale'] and decision['method_rationale'] and decision['limitation'] and decision['next_action'], cid
            assert decision['decision'] in {'supported', 'correction', 'residual'}, cid
            if decision['decision'] == 'correction':
                assert decision['proposed_replacement'] != frozen[cid]['claim']['text'], cid
            if decision['decision'] == 'residual':
                assert decision['proposed_status'] in {'UNVALIDATED', 'FAIL', 'BLOCKED'}, cid
            assert decision['source_refs'], cid
            for ref in decision['source_refs']:
                source = sources[ref['source']]
                path = ROOT / source['path']
                assert path.resolve().is_relative_to(ROOT), path
                source_raw = path.read_bytes()
                assert sha(source_raw) == source['sha256'], (cid, source['path'])
                if 'sha256' in ref:
                    assert ref['sha256'] == source['sha256'], cid
                excerpt = ref.get('source_excerpt', ref.get('excerpt'))
                assert select(source_raw, ref['text_pointer']) == excerpt, (cid, ref['source'], ref['text_pointer'])
                selections.add((source['path'], ref['text_pointer']))
        output.append({'lane': lane, 'claims': len(decisions), 'decisions_sha256': sha(raw), 'sources_sha256': sha(sources_raw),
                       'decision_counts': dict(Counter(d['decision'] for d in decisions)),
                       'status_counts': dict(Counter(d['proposed_status'] for d in decisions)),
                       'distinct_exact_source_selections': len(selections)})
    print(json.dumps({'check': 'PASS', 'scope': 'Identity and exact source binding; substantive acceptance is recorded separately.', 'lanes': output}, indent=2))


if __name__ == '__main__':
    main()
