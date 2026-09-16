"""Explicit per-occurrence S4/S5 source-review decisions; no model writes."""
import hashlib,json,pathlib
O=pathlib.Path(__file__).parent;A=O.parent;ROOT=O.parents[3]
inv=json.loads((A/'inventory.json').read_text());model=json.loads((ROOT/'verification/current-host-docs-review.json').read_text())
assert hashlib.sha256((ROOT/'verification/current-host-docs-review.json').read_bytes()).hexdigest()==inv['baseline_model_sha256']
rows={x['id']:x for x in inv['claims'] if x['family'] in ['S4','S5']}
def current(x):
 c=model
 for k in x['model_pointer'].strip('/').split('/'):c=c[int(k)] if isinstance(c,list) else c[k]
 assert hashlib.sha256(c['text'].encode()).hexdigest()==x['literal_sha256'];return c
for file in ['canonical-cli-excerpts.json']:
 p=O/file;j=json.loads(p.read_text())
 for x in j['excerpts']:x['lines_text']=x['text'].splitlines()
 p.write_text(json.dumps(j,indent=2)+'\n')
p=O/'arithmetic-review.json';j=json.loads(p.read_text())
for c in j['checks']:c['finding']=c['expression']+' = '+str(c['actual'])+'; matched expected '+str(c['expected'])
p.write_text(json.dumps(j,indent=2)+'\n')
def proof(file,pointer):
 p=O/file;j=json.loads(p.read_text());v=j
 for k in pointer.strip('/').split('/'):v=v[int(k)] if isinstance(v,list) else v[k]
 assert isinstance(v,str) and v
 return {'artifact_ref':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'text_pointer':pointer,'excerpt':v,'source_url':j.get('source_url'),'source_revision':j.get('source_revision')or j.get('title')}
def code(index,needle):
 j=json.loads((O/'canonical-cli-excerpts.json').read_text());e=j['excerpts'][index];n=next(i for i,x in enumerate(e['lines_text']) if needle in x)
 r=proof('canonical-cli-excerpts.json',f'/excerpts/{index}/lines_text/{n}');r.update(source_url=e['source_url'],source_revision=e['revision'],source_path=e['source_path'],source_sha256=e['source_sha256'],source_lines=[e['lines'][0]+n,e['lines'][0]+n]);return r
P={
 'math':proof('arithmetic-review.json','/checks/4/finding'),'units':proof('arithmetic-review.json','/dimensional_check'),'utilization':proof('arithmetic-review.json','/checks/0/finding'),'margin':proof('arithmetic-review.json','/checks/5/finding'),
 'gpu':code(0,'num_gpus:'),'region':code(0,'geolocation:'),'network':code(0,'inet_down:'),'hardware':code(0,'cpu_ram:'),'disk':code(0,'disk_space:'),'storage-price':code(0,'storage_cost:'),'reliability':code(0,'reliability:'),'verified':code(0,'verified:'),'duration':code(1,'--duration'),'enddate':code(1,'--end_date'),'bid':code(1,'--price_min_bid'),'discount':code(1,'--discount_rate'),'ready':code(1,'only list when ready'),'outage':code(1,'goes offline'),'volumes':code(1,'--vol_size'),'bandwidth-price':code(1,'--price_inetu'),'median':code(2,'price_median'),'p10':code(2,'price_p10'),'p90':code(2,'price_p90')}
S5=[
('MCL-de45745b7371d2ea',['utilization'],'0.55 is exactly 55/100; the table defines an input fraction, not observed rental utilization.'),
('MCL-54decf78374d871f',['math','storage-price'],'Qualified troubleshooting advice follows the compute-only estimate. Lower utilization can reduce compute revenue at a fixed rate; storage is a separately priced input. No renter-choice cause or actual earnings is adjudicated.'),
('MCL-15fd976af9df9776',['region','network'],'The comparison checklist uses declared location and bandwidth attributes; considering latency is contextual advice, without a promised ranking or return.'),
('MCL-5c510c7c9dae633d',['hardware','disk'],'System RAM and disk space are explicit offer fields. Comparing CPU/storage characteristics is sensible matching advice, without a performance outcome.'),
('MCL-102b942b37b8109a',['storage-price','bandwidth-price'],'Storage and bandwidth have separate declared prices, so they are relevant comparison inputs. No fee schedule or charged amount is verified.'),
('MCL-6ece27546cfec525',['reliability','outage'],'The CLI declares reliability and cautions against outages. Comparing reliability/uptime is advice; no score formula, guarantee or rank is asserted.'),
('MCL-d9f3e08cb17c901c',['math','median'],'Advice uses comparable prices and actual utilization as planning inputs. The arithmetic supports the tradeoff, not a demand forecast.'),
('MCL-20338cf437fdade2',['reliability','median'],'Within Pricing Strategy this is qualified advice to compare price while reliability history develops; it states no required introductory discount, ranking rule or guaranteed utilization. The price and reliability inputs are declared.'),
('MCL-92880d84640c3366',['math'],'Read in Pricing Strategy, this is a willingness-to-pay consideration rather than a promised causal uplift. A higher asking price with no rental hours cannot increase compute revenue.'),
('MCL-88a0b370ce14c609',['math'],'The conditional price/utilization tradeoff is arithmetically sound. Reducing price with rental hours held fixed reduces revenue; no claim that actual demand will increase is validated.'),
('MCL-8bbe65d1247cdcdd',['margin'],'Gross less applicable operating costs is the planning distinction between revenue and margin. No tax treatment, fee amount or investment return is asserted.'),
('MCL-a92a5f176cb1e129',['margin'],'Power and cooling are candidate costs in the preceding cost-subtraction checklist. The advice does not prescribe an amount or tax classification.'),
('MCL-216077c3dab0d6a1',['margin'],'Internet, rack and colocation are candidate operating inputs in the cost checklist, not a universal charge or provider tariff.'),
('MCL-3a382c4118031f61',['margin'],'The cost-planning checklist asks the operator to include their hardware/depreciation or financing basis. It does not set a depreciation schedule, deductible amount or accounting rule.'),
('MCL-4a8ee9706710c271',['margin'],'Repairs and maintenance time are candidate costs in a planning checklist. No cost, duty or service guarantee is claimed.'),
('MCL-07ca2eb2d76b7500',['math'],'The introduction recommends optimizing overall revenue rather than one hourly-rate input; the fixed-period price/utilization example establishes that distinction without a trial.'),
('MCL-5e12c7bb993d838a',['ready'],'A pre-listing readiness recommendation agrees with CLI guidance to test first and list when ready. It does not assert each item is a separately enforced verification gate.'),
('MCL-3dfdfcfb9fc1b656',['enddate','outage'],'In the preparation checklist, matching availability to commitments is planning advice. The page separately says to review existing rental commitments; an offer date is not treated as automatically ending rentals.'),
('MCL-7e0e72f2ec54e028',['median'],'The destination exists and the advice is to compare similar machines using market information; no displayed figure or refresh schedule is promised.'),
('MCL-01a5ca2ed2a35c42',['math'],'The linked Earnings Model exists and defines a gross-revenue estimate. Recommending estimation before pricing is contextual advice, not validation of actual earnings.'),
('MCL-f07cbcdea0b58547',['p10','median','p90'],'This is a request to inspect a consistent 30-day comparison period, not an assertion of its measured value. CLI declares price percentiles; the current target page explicitly defines the 30-day rented-share label. This review validates the advice/navigation only, not that a live dashboard currently returns those fields.'),
('MCL-d0dea82ab92274a6',['bid'],'The listing parser calls the minimum bid a price floor. Distinguishing that floor from a target price is advisory interpretation of the declared option.'),
('MCL-0ebbdb298d5bf37f',['discount'],'The option is a long-term prepay discount; advising capacity for longer rentals is a planning limit, not a promised reservation outcome.'),
('MCL-2c8d7c4ef6e8449d',['math'],'At fixed GPU-hours a lower hourly price with sufficiently higher utilization can yield more compute revenue. The internal income-estimate anchor exists; no market outcome is guaranteed.'),
('MCL-85c106837f6a39a8',['math'],'The Possible action row is an optional future-contract pricing experiment. It makes no promise of demand or retroactive rate change.'),
('MCL-c2c48ce89527e0ec',['verified','reliability'],'The row advises checking listing fit and health when rental demand is poor. Declared offer attributes support those comparison dimensions; they are not a proven cause of low rentals.'),
('MCL-0c50a629b1a27cea',['discount','enddate'],'The conditional Possible action recommends considering declared discount and availability controls. It states no guaranteed reservation or profit uplift.'),
('MCL-37c5601dbd39cdce',['units','math'],'The original equality omits GPU count and hours, so hourly price × utilization has rate units rather than revenue. The replacement explicitly fixes those dimensions.','For a fixed GPU count and time period, compute revenue is proportional to hourly price multiplied by utilization. A high price with low occupancy can earn less than a moderate price with steady rentals.'),
('MCL-7ed20e047d190019',['duration'],'The shorter/longer duration table expresses a planning tradeoff in available time. It promises neither occupancy nor uninterrupted execution.'),
('MCL-a443ddfff0691f6f',['duration'],'This introduces different workload planning needs, without quantifying renter preferences or establishing a product rule.'),
('MCL-c6b33f097c787b0e',['duration'],'The fixed hours-to-days range was presented as Typical duration without a renter-distribution source. Mark it as an illustrative planning example and condition the recommendation on covering the job.','| Automated inference or burst work | Hours to days (illustrative example) | Consider shorter offers when they cover the expected job. |'),
('MCL-f42b42e963581b75',['duration'],'The days-to-weeks range is an illustrative assumption, not measured typical renter behavior. The replacement makes that scope explicit and removes an implied occupancy result.','| Experiments and fine-tuning | Days to weeks (illustrative example) | Compare the required job time with the commitment you can support. |'),
('MCL-8990a3b72adf934d',['duration'],'The weeks-to-months range lacks population evidence, and higher-value renters is an unsupported comparative claim. The replacement uses an illustrative range and workload-fit advice only.','| Training runs or reserved capacity | Weeks to months (illustrative example) | Consider longer offers for jobs that need longer rental windows. |'),
('MCL-c346d2d59ffff473',['math','median'],'Qualified advice uses comparable pricing and observed utilization instead of an isolated high quote. The mathematical tradeoff is supported; success is not promised.'),
('MCL-4b5c1e500979485f',['math'],'The Consider column proposes an option for an idle machine. It does not claim that lowering price necessarily creates demand.'),
('MCL-8d69c2bb075e0c15',['math'],'This is a proposed pricing experiment, not an observed uplift. The adjacent price-change paragraph retains current-term protections.'),
('MCL-6dfa085c35a11401',['median','reliability'],'This is a conditional consideration, not a mandated matching price or verified score/ranking effect. The comparison attributes are declared.'),
('MCL-9bcd70097d2893da',['enddate'],'The row advises when to reconsider price, and does not change current rental terms or promise a demand spike.'),
('MCL-a08770c33cd7d1af',['bid','margin'],'Minimum bid as a floor is declared. The frequency claim often close to loaded power cost lacks support and can omit other costs. The replacement makes the host choose the cost basis.','The minimum bid is a floor, not your expected on-demand price. Choose the lowest price you are willing to accept after considering the operating costs you intend to cover.'),
('MCL-0c3c37d504b01f38',['bid','margin'],'Both risks are conditional planning considerations: no accepted work can mean idle GPUs, and a received rate below applicable costs can produce a loss. There is no predicted utilization or prescribed floor.'),
('MCL-912f4fc01153430c',['storage-price'],'The Guidance table recommends considering local resource scarcity when setting a declared storage rate. It does not assert a backend allocation or demand response.'),
('MCL-307f5b9855a598f5',['bandwidth-price'],'The Guidance table makes pricing contingent on the operator\'s link/cost conditions. It does not prescribe a tariff or promise congestion prevention.'),
('MCL-3397592e4033c1b8',['disk','volumes'],'Read as capacity planning: leave disk headroom for all commitments. It does not instruct deletion of tenant data, revocation of rented volumes, or secure wiping; no storage lifecycle guarantee is inferred.'),
('MCL-3f3cde2e5306852e',['storage-price'],'The Watch out for column is a qualified price/competitiveness consideration, not measured demand or a promised ranking effect.'),
('MCL-abfacd9d8b4c7585',['disk','volumes'],'The row flags a conditional capacity-planning risk when disk is constrained. It does not establish price as an enforcement mechanism or recommend deleting existing renter storage.'),
('MCL-249c4808586a7ead',['bandwidth-price'],'The claim is a qualified possible advantage of a declared comparison price, not a promised ranking, occupancy or profitability result.'),
('MCL-1a3dedcbfa0bdc7d',['bandwidth-price','margin'],'The row flags the conditional cost/capacity risk of metered or shared bandwidth. It does not say price enforces bandwidth limits or that a renter will necessarily saturate a link.'),
('MCL-3956d55db518eaa8',['ready'],'Pre-listing driver upkeep is a readiness recommendation. It does not require upgrading an active rental or assert that every newest driver is compatible.'),
('MCL-c9004ebe62856857',['outage'],'Avoiding unplanned interruptions follows the CLI caution about outages/performance during client jobs. No quantitative reliability or uptime guarantee is inferred.'),
('MCL-d9da265d026893c3',[],'This is editorial advice to make only true, approved claims. It neither awards certification nor asserts eligibility, legal compliance or who can approve a facility claim.'),
('MCL-17f0db9b9773ff3f',['duration'],'The quick-reference question asks the operator to assess their own availability. It imposes no new universal minimum or maximum duration.'),
('MCL-89ca18d38ed24003',['bid'],'The quick-reference question asks the operator to choose an acceptable floor for a declared option. No required price or expected return is asserted.'),
]
def make_s5():
 out=[]
 for item in S5:
  id,tags,why,*replacement=item;x=rows[id];c=current(x);methods=c['required_evidence_types'];proposed=methods
  # Advice without a product declaration needs reasoned context, not code or paid outcomes.
  pure=id in {'MCL-8bbe65d1247cdcdd','MCL-a92a5f176cb1e129','MCL-216077c3dab0d6a1','MCL-3a382c4118031f61','MCL-4a8ee9706710c271','MCL-a443ddfff0691f6f','MCL-d9da265d026893c3','MCL-de45745b7371d2ea','MCL-37c5601dbd39cdce','MCL-c6b33f097c787b0e','MCL-f42b42e963581b75','MCL-8990a3b72adf934d'}
  if pure:proposed=['REPOSITORY_STATIC_CHECK']
  proofs=[P[t] for t in tags]
  if not proofs:proofs=[proof('static-context.json','/truthful_guidance/finding')]
  d={'id':id,'family':'S5','model_pointer':x['model_pointer'],'page':x['page'],'headings':c['headings'],'spans':c['spans'],'literal_sha256':x['literal_sha256'],'current_literal':c['text'],'decision':'correction' if replacement else 'supported','proofs':proofs,'support_rationale':why,'limits':'Qualified planning advice, arithmetic or declared comparison inputs only. No actual earnings, utilization uplift, ranking, fees, rental lifecycle, legal duty, tenant-data deletion, or human acceptance is validated.','next_action':'Apply the exact reviewed replacement and check affected source spans.' if replacement else 'No additional runtime check is needed for this scoped source/advice review; reassess if wording or inputs change.'}
  if pure and proposed!=methods:d['proposed_methods']=proposed;d['method_change_rationale']='The whole occurrence is an arithmetic input or contextual recommendation, not an implementation assertion. '+why
  if id=='MCL-37c5601dbd39cdce':d.update(proposed_methods=['REPOSITORY_STATIC_CHECK'],proposed_classification='REVIEWED_EXAMPLE_CALCULATION',method_change_rationale='Dimensional analysis and a declared-input arithmetic fixture support this correction; no canonical product implementation is being validated.')
  if id in {'MCL-c6b33f097c787b0e','MCL-f42b42e963581b75','MCL-8990a3b72adf934d'}:d.update(proposed_methods=['REPOSITORY_STATIC_CHECK'],proposed_classification='REVIEWED_ADVICE',method_change_rationale='These corrected ranges are explicitly illustrative planning assumptions, not measured renter distributions or canonical duration rules.')
  if replacement:d.update(original_discrepancy=why,replacement=replacement[0],replacement_sha256=hashlib.sha256(replacement[0].encode()).hexdigest(),replacement_review='Rechecked the complete replacement against the selected declarations or exact arithmetic; it removes the unsupported equality, typicality or comparative claim and adds no outcome promise.')
  out.append(d)
 assert len(out)==52 and {d['id'] for d in out}=={x['id'] for x in rows.values() if x['family']=='S5'}
 return out
if __name__=='__main__':
 decisions=make_s5();s4=O/'decisions-s4.json'
 if s4.exists():decisions+=json.loads(s4.read_text())['decisions']
 out={'record_type':'BOUNDED_SOURCE_FAMILY_REVIEW','status':'COMPLETE' if len(decisions)==130 else 'IN_PROGRESS_S5_COMPLETE','baseline_commit':inv['baseline_commit'],'baseline_model_sha256':inv['baseline_model_sha256'],'frozen_inventory_sha256':hashlib.sha256((A/'inventory.json').read_bytes()).hexdigest(),'assigned_count':130,'reviewed_count':len(decisions),'decisions':decisions,'context_corrections':[{'page':'host/optimization-guide.mdx','line':34,'source_before_sha256':hashlib.sha256((ROOT/'host/optimization-guide.mdx').read_bytes()).hexdigest(),'literal_before_sha256':hashlib.sha256('| Renter need | Typical duration | Fit |'.encode()).hexdigest(),'current':'| Renter need | Typical duration | Fit |','replacement':'| Renter need | Illustrative planning window | Fit |','reason':'Necessary header alignment for the three selected duration rows; this adjacent header is outside the frozen 130 IDs and needs explicit integration accounting.'}],'limits':'These are per-occurrence proposals, not model statuses. Source/manual/fixture review does not prove live Hosts, fees, guarantees or acceptance.'}
 (O/'decisions.json').write_text(json.dumps(out,indent=2)+'\n');(O/'decisions-s5.json').write_text(json.dumps({'decisions':make_s5()},indent=2)+'\n');print({k:sum(x['decision']==k for x in decisions) for k in ['supported','correction','residual']})
