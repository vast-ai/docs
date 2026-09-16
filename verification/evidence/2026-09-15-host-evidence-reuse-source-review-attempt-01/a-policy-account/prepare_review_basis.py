import json,pathlib,hashlib,subprocess,datetime,re
from decimal import Decimal
A=pathlib.Path(__file__).resolve().parent; R=A.parents[3]
def sh(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def out(name,d):(A/name).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
# Bind observations only to pixels actually inspected; do not assign a capture time/release to old screenshots.
images=[('images/console-notifications-settings.png','The image shows a panel titled "Notification and Webhook Settings", Account/Billing/Instance groups, removable Email chips for some Instance events, and a Save button. It does not show a Host group, a route/address bar, successful save, or actual delivery.'),('images/host-teams-escalation-contact.webp','The image shows an Escalation Contact panel for urgent issues with hosted machines, Escalation Email, Escalation Phone Number and Save. It does not show account context, route/address bar, successful persistence or responder delivery.'),('images/host-teams-invoice-information.webp','The image shows Invoice Information fields and Save. It does not show an account context, route/address bar, invoice generation or data persistence.'),('images/host-teams-create-role.webp','The image shows a Create Role dialog with Machines Read and Write permissions, a global Require 2FA toggle and per-permission 2FA toggles, plus User, Instances, Billing/Earning and Team permission rows. It does not prove enforcement or daemon registration privileges.')]
out('included-image-observations.json',{'record_type':'INSPECTION_OF_INCLUDED_PRODUCT_SCREENSHOTS','inspected_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'capture_version_and_date':'Unknown; no new authenticated product observation','observations':[{'path':f,'sha256':sh(R/f),'observation':t}for f,t in images],'limits':'Existing included product screenshots are reused without modifying or copying image bytes. Visible controls only; no inferred account, backend or delivery outcome.'})
# Separate numeric illustration from claimed policy.
scenarios=[]
for name,rate in [('P10','0.35'),('Median','0.45'),('P90','0.65')]:
 result=Decimal(4)*Decimal(rate)*Decimal(720)*Decimal('0.55')
 scenarios.append({'scenario':name,'gpu_capacity':4,'dollars_per_gpu_hour':rate,'hours':720,'utilization':'0.55','result_dollars':str(result),'interpretation':f'4 available GPUs × ${rate}/GPU-hour × 720 hours × 0.55 occupancy = ${result}. Capacity is not already utilization-adjusted.'})
out('arithmetic-and-context.json',{'record_type':'REVIEWED_EXAMPLE_CALCULATION','method':'Python Decimal dimensional calculation, no marketplace experiment or profitability model validation','scenarios':scenarios,'input_definition':'rentable GPUs is the GPU capacity offered for rental throughout the modeled period, before applying utilization. If capacity changes, use separate time periods or a time-weighted capacity.','gross_components':'Compute, instance storage, bandwidth and separately rented volumes are distinct modeled revenue categories; do not count volume storage again under instance storage. The sum is gross, not profit or a guaranteed bill.'})
# Navigation proof is route/content existence in the frozen reviewed checkout, not product runtime.
paths=['host/supported-hardware.mdx','host/maintenance-windows.mdx','host/removing-recreating-machines.mdx','host/how-to-self-test.mdx','host/common-errors-diagnostics.mdx','host/market-metrics.mdx','host/earning.mdx','host/pricing-your-listing.mdx','guides/reference/keys.mdx','cli/authentication.mdx','cli/reference/reports.mdx','cli/reference/show-members.mdx','cli/reference/invite-member.mdx','cli/reference/remove-member.mdx','host/host-teams.mdx','api-reference/permissions.mdx']
nav=[]
for f in paths:
 p=R/f
 if not p.exists():raise Exception(f)
 lines=p.read_text().splitlines();h=[{'line':i+1,'text':t}for i,t in enumerate(lines)if t.startswith('#')or'id="'in t or t.startswith('title:')or t.startswith('canonical:')or t.startswith('"canonical":')]
 nav.append({'path':f,'sha256':sh(p),'headings_and_anchors':h,'target_exists':True})
out('navigation-review.json',{'record_type':'BOUNDED_REPOSITORY_LINK_CONTEXT_REVIEW','baseline':'61fbb47','targets':nav,'limits':'Checks destination file/section existence and its stated workflow. Does not independently prove any instruction in the destination.'})
# Store exact canonical API excerpts, verified unchanged from approved upstream main.
f='api-reference/openapi/yaml/notifications.yaml';p=R/f;b=p.read_bytes();rev=subprocess.check_output(['git','rev-parse','origin/main'],cwd=R,text=True).strip();assert b==subprocess.check_output(['git','show',f'{rev}:{f}'],cwd=R)
out('notification-api-source.json',{'record_type':'EXACT_APPROVED_API_SPEC_EXCERPTS','repository':'vast-ai/docs','revision':rev,'source_file':f,'source_sha256':sh(p),'source_url':f'https://github.com/vast-ai/docs/blob/{rev}/{f}','excerpts':[{'lines':[s,e],'text':'\n'.join(b.decode().splitlines()[s-1:e])}for s,e in [(9,33),(40,43),(74,104),(251,270),(491,538)]],'limits':'Published OpenAPI type/endpoint declarations; not proof that console host rendering or delivery succeeds.'})
print('Basis files written.')
