from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[3];A=Path(__file__).resolve().parent;AR=str(A.relative_to(R));sha=lambda b:hashlib.sha256(b).hexdigest()
for ext in ['py','mjs']:
 p=R/f'scripts/current_host_evidence_reuse_review.{ext}';s=p.read_text().replace('PENDING_ADJACENT_SCOPE',sha((A/'adjacent-scope.json').read_bytes()))
 if ext=='py':
  s=s.replace("ids={c['id'] for c in frozen_claims}","ids={c['id'] for c in frozen_claims}\n    inventory['source_hashes'].update(expansion['source_hashes'])")
 else:s=s.replace("frozenClaims=[...inventory.claims,...expansion.claims],ids=new Set(frozenClaims.map(c=>c.id));", "frozenClaims=[...inventory.claims,...expansion.claims],ids=new Set(frozenClaims.map(c=>c.id));Object.assign(inventory.source_hashes,expansion.source_hashes);")
 p.write_text(s)
s=(R/'verification/evidence/2026-09-15-host-unvalidated-source-families-attempt-01/integrate.py').read_text()
s=s.replace("for family in ['s1','s2-s3','s4-s5']:","for family in ['a-policy-account','b-hardware-install','c-operations-verification']:")
a=s.index('assert set(decisions)==');z=s.index('changes={}',a)
s=s[:a]+'''assert set(decisions)=={d['id'] for d in inv['claims']} and len(decisions)==309
expansion=read(AR+'/adjacent-scope.json');inv['source_hashes'].update(expansion['source_hashes'])
for d in read(expansion['proposals_ref'])['proposals']:assert d['id'] not in decisions;decisions[d['id']]=d;families[d['id']]='b-hardware-install'
frozen={x['id']:x for x in [*inv['claims'],*expansion['claims']]}
accepted=read(AR+'/root-lane-acceptance.json')
for lane in accepted['lanes']:
 for file,field in [('decisions.json','decisions_sha256'),('sources.json','sources_sha256')]:assert sha((A/lane['lane']/file).read_bytes())==lane[field]
assert len(decisions)==312 and set(decisions)==set(frozen)
assert sha((R/expansion['proposals_ref']).read_bytes())==expansion['proposals_sha256']
''' +s[z:]
s=s.replace("c['status']=='UNVALIDATED'", "c['status']==frozen[cid]['claim']['status']")
s=s.replace("source_index=read(AR+'/s1/sources.json')['sources'];", "source_indexes={f:read(AR+'/'+f+'/sources.json')['sources'] for f in ['a-policy-account','b-hardware-install','c-operations-verification']};")
a=s.index("for f in ['s1/decisions.json'");z=s.index('for cid,d in decisions.items():',a)
s=s[:a]+'''for family in source_indexes:
 for name in ['decisions.json','sources.json']:bind(AR+'/'+family+'/'+name)
for name in ['root-lane-acceptance.json','adjacent-scope.json','b-hardware-install/adjacent-proposals.json','b-hardware-install/sources/cpu-policy-discrepancy.json']:bind(AR+'/'+name)
''' +s[z:]
s=s.replace("meta=source_index[b['source']] if family=='s1' else b", "meta=source_indexes[family][b['source']]")
s=s.replace("'SOURCE-FAMILY-'", "'EVIDENCE-REUSE-'")
s=s.replace("'SCOPED_SOURCE_FAMILY_REVIEW'", "'SCOPED_EVIDENCE_REUSE_REVIEW'")
s=s.replace("'source_family_review'", "'evidence_reuse_review'")
s=s.replace("scope['decisions'][cid]={'fields_sha256'", "scope['decisions'][cid]={'residual_topic':d.get('residual_topic'),'fields_sha256'")
s=s.replace("'decision':d['decision'],'method'", "'decision':d['decision'],'residual_topic':d.get('residual_topic'),'method'")
s=s.replace("'SOURCE_FAMILY'", "'EVIDENCE_REUSE'")
s=s.replace("'HOST_SOURCE_FAMILY_REVIEW'", "'HOST_EVIDENCE_REUSE_REVIEW'")
s=s.replace("'BOUNDED_SOURCE_FAMILY_INTEGRATION_IMPACT'", "'BOUNDED_EVIDENCE_REUSE_INTEGRATION_IMPACT'")
s=s.replace("    assert n['id']=='ERR-T05-B02-S01'\n",'')
s=s.replace("    assert oldcommands and oldcommands==newcommands", "    assert oldcommands==newcommands,('PASS procedure command change requires explicit review',n['id'])")
s=s.replace("assert len(procedures)==43 and len(command_comparisons)==1", "assert not impact['out_of_scope_overlaps'],impact['out_of_scope_overlaps']")
s=s.replace("'all_43_statuses_and_evidence_unchanged':True", "'all_procedure_statuses_and_evidence_unchanged':True,'affected_count':len(procedures)")
a=s.index("amendment=read(AR+'/owner-context-amendment.json')");z=s.index("(A/'integration-scope.json')",a);s=s[:a]+s[z:]
s=s.replace("verification/current-host-source-family-review.json","verification/current-host-evidence-reuse-review.json").replace("scripts/current_host_source_family_review.py","scripts/current_host_evidence_reuse_review.py").replace("scripts/current_host_source_family_review.mjs","scripts/current_host_evidence_reuse_review.mjs")
a=s.index("'limits':'358 frozen occurrences:");z=s.index("}\nrp=",a);s=s[:a]+"'limits':'312 occurrences: 309 previously unvalidated plus two CPU diagnostic FAIL corrections and one adjacent AMD configuration correction. Source-defined instructions, published guidance and bounded historical observations; no new hardware execution, platform-policy resolution or human acceptance. Existing eight owner questions, earlier claims, failures and all prior evidence remain retained.'"+s[z:]
(A/'integrate.py').write_text(s)
print('integration draft prepared')
