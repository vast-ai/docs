/** Reader-facing wording only. Never adjudicates or changes a claim record.
 * Exact text matches keep added, claim-specific limits from being generalized.
 */
import {createHash} from 'node:crypto';
const families = new Map([
  ['This is account context, permission enforcement, console configuration, or a state transition. References to agreement acceptance, invoice data, payout settings, or team ownership are technical subjects here.',
    ['The account setup, settings or permissions described here still need to be checked.', 'Check the relevant Vast account rules and save a record of what the account page or API requires.']],
  ['This is a suggested planning, troubleshooting, or optimization action. It does not promise an outcome, prescribe a contractual price, or create an obligation merely by using finance/responsibility words.',
    ['This is advice. The reasoning and facts behind it still need to be checked; results are not guaranteed.', 'Check the reasoning and technical facts behind this recommendation.']],
  ['This is a topic/destination map or instruction to read a page, not a statement that the destination content is true. Heading or linked-label finance/legal terms cannot create owner authority requirements.',
    ['This points to another page. The link still needs to be checked.', 'Confirm that the link opens the intended page and section. This does not verify the statements on that page.']],
  ['This states a visible console label, control, screenshot caption, or navigation/export action. Its finance/agreement vocabulary does not assert a financial obligation or legal interpretation.',
    ['The screen, label or action described here still needs to be checked in the current console.', 'Check the current console using the relevant account type, and save the result.']],
  ['This describes technical behavior, data meaning, storage/rental state, or an application result. Price, account, contract, or policy vocabulary is incidental to that behavior and does not create a fresh owner-approval requirement.',
    ['The behavior described here still needs support from the Vast code and a relevant test.', 'Check the relevant code or API definition, then save a result from an approved test.']],
  ['The sentence advises a safe/reasonable operating sequence and may describe technical capabilities. Advice is not automatically a platform prohibition or contract promise; test only its actual behavior assertions.',
    ['This is operating advice. Its technical claims still need to be checked.', 'Check the reasoning and technical claims. Keep any claimed requirement separate from the advice.']],
  ['This recommends 2FA, least privilege, secret handling, or key hygiene. It does not assert mandatory platform enforcement or contractual liability. Verify any implied feature separately.',
    ['This is security advice. The guidance and any features it relies on still need to be checked.', 'Check primary security guidance and confirm any Vast security features mentioned here.']],
  ['This states a platform program condition, availability/verification expectation, or program benefit. Existing program requirements and enforcement configuration should be used before seeking a new Product decision.',
    ['The requirement or benefit described here still needs supporting evidence.', 'Check the published program rules and how Vast applies them. Ask Product only about gaps or unclear wording.']],
  ['This occurrence states an actual Host obligation, restriction, or allocation under the rental relationship. Existing governing language can establish it without a new human confirmation; observing a rental does not establish a legal duty.',
    ['This describes a host responsibility or restriction. It still needs support from the applicable agreement.', 'Find and cite the agreement section that supports this statement. Ask the agreement owner only if it is missing or unclear.']],
  ['This asserts actual revenue composition, supported payout service, payout timing/threshold, or financial responsibility. It needs applicable financial authority, but authority may already be published or recorded.',
    ['This describes earnings or payment terms. It still needs an official supporting source.', 'Check and cite the relevant published payment terms. Ask Finance only about gaps or unclear terms.']],
  ['The occurrence asserts accepted-rental terms or their persistence/change, so applicable agreement authority matters. System effects additionally need canonical behavior and representative evidence.',
    ['The rental terms and the system behavior described here still need to be checked.', 'Check the relevant agreement section for the terms. Check the code and an approved test for how the system applies them.']],
  ['This names a declared control, CLI option, unit, or client dispatch capability. Canonical declarations and exact source mappings are appropriate; they do not imply a specific price or backend billing behavior.',
    ['The setting or command option described here still needs a supporting source.', 'Find the setting in the Vast code or API definition and link the exact definition. This does not establish billing behavior.']],
  ['This combines declared options with an asserted backend effect. Owner confirmation is the wrong lane; source and representative behavior remain required.',
    ['Both the option and its stated effect still need to be checked.', 'Check the option definition and the server code that handles it. Save a result from an approved test.']],
  ['This is an actual tax/reporting responsibility or Vast tax-handling assertion. Applicable official tax/provider sources and existing Vast authoritative statements must precede a Finance/Legal escalation.',
    ['The tax or reporting responsibility described here still needs an official supporting source.', 'Check the relevant official tax, payment-provider or Vast source first. Ask Finance or Legal only about gaps or unclear wording.']],
  ['This points to an external official page/action and makes no legal or financial term claim.',
    ['The external link or action still needs to be checked.', 'Confirm that it opens the intended official page or action. This does not verify that page’s statements.']],
  ['This describes implemented verification eligibility, timing, or enforcement. The word policy does not by itself require a new Product owner decision; the current enforcement source/configuration is the first authority.',
    ['The verification rule or timing described here still needs supporting evidence.', 'Check Vast’s verification rules in the code or configuration and compare them with recorded results. Do not promise a timeline without support.']],
  ['This describes high-level product capabilities or revenue categories without a specific term, rate, or account promise.',
    ['This product description still needs an official supporting source.', 'Find an official Vast publication that supports each part of this statement.']],
]);

const missing = new Set([
  'No claim-suitable retained source, runtime observation, or accountable-owner confirmation is bound to this exact current occurrence. Missing evidence alone is UNVALIDATED.',
  'No current claim-suitable source, runtime observation, or accountable-owner decision is bound to this literal occurrence.',
]);

const policyRationale = 'This occurrence states an actual Host obligation, restriction, or allocation under the rental relationship. Existing governing language can establish it without a new human confirmation; observing a rental does not establish a legal duty.';
const policyNext = 'Start with the retained official Hosting Agreement and Terms; identify the exact clause, actor, object, and scope. Narrow or cite the sentence only where the source actually supports it.';
const reviewedPolicyRationale = 'This is a policy instruction, not a runtime test. Match it to the applicable approved rule. An acknowledgement alone does not fill a missing citation.';
const reviewedPolicyNext = 'Check the applicable Terms, Hosting Agreement or approved policy for this exact instruction and scope. Cite a matching clause. Ask the accountable policy owner to confirm or correct only a missing or unclear rule; retain that decision and its citation.';
const sameTypes = (actual, expected) => actual.length === expected.length && actual.every((type, index) => type === expected[index]);
// These are the recorded clarification cohorts. Each uses an exact
// classification, rationale, next action and evidence shape; ID guards apply
// only where the retained acknowledgement wording is claim-specific.
const reviewedFamilies = [
  {
    classification: 'REVIEWED_ADVICE', statuses: ['UNVALIDATED'], types: ['REPOSITORY_STATIC_CHECK'],
    rationale: 'This is advice or an instruction about using the documentation. Review it for clarity, safety and fit. It does not claim that a platform operation succeeded.',
    next: 'Check this advice in its page context and record any wording or safety issue. Review any factual feature, policy rule or promised result separately with the appropriate source.',
    label: 'Advice review', statusLabel: 'Advice review', reviewKind: 'advice-review',
  },
  {
    classification: 'REVIEWED_TECHNICAL_DECLARATION', statuses: ['UNVALIDATED'], types: ['CANONICAL_IMPLEMENTATION_SOURCE'],
    rationale: 'This is a technical description or instruction. Check the exact definition in the relevant code, API schema, configuration or primary tool documentation. A written example is not evidence that an operation ran.',
    next: 'Find the exact definition or instruction in canonical code, an API schema, configuration or primary tool documentation. Compare each option, unit, limit and safety condition with this passage. Use a separate retained result if claiming that the operation ran or succeeded.',
    label: 'Technical declaration review', statusLabel: 'Check technical source', reviewKind: 'technical-declaration-review',
  },
  {
    classification: 'REVIEWED_EXAMPLE_CALCULATION', statuses: ['UNVALIDATED'], types: ['REPOSITORY_STATIC_CHECK'],
    rationale: 'This is a planning example, not an observed earning or bill. Check the arithmetic, units and stated assumptions.',
    next: 'Recalculate the example with its stated inputs and units. Label hypothetical inputs clearly; do not present the result as measured revenue, a bill or a promised return.',
    label: 'Example calculation review', statusLabel: 'Check calculation assumptions', reviewKind: 'example-calculation-review',
  },
  {
    classification: 'REVIEWED_BEHAVIOR_DESCRIPTION', statuses: ['UNVALIDATED'], types: ['CANONICAL_IMPLEMENTATION_SOURCE','RUNTIME_OR_UI_OBSERVATION'],
    rationale: 'This describes a behavior or result. Check the implementation first; use retained execution or UI evidence for any claimed timing, state change or completed outcome. Do not turn this into a general policy-approval request.',
    next: 'Check the implementation and any retained result that covers this exact behavior. For an asserted timing, state change or completed outcome, identify the smallest authorized runtime/UI check and retain its result. Do not rent or mutate merely to establish a declared interface.',
    label: 'Behavior review', statusLabel: 'Check implementation and retained result', reviewKind: 'behavior-review',
  },
  {
    ids: new Set(['MCL-96a7de8300ee0824','MCL-11d3dfb2a39b7a30','MCL-e6019b684fd7cbb3','MCL-a4a99786611bde77','MCL-cd20d467c7457d53','MCL-54decf78374d871f','MCL-102b942b37b8109a','MCL-d9f3e08cb17c901c','MCL-20338cf437fdade2','MCL-92880d84640c3366','MCL-88a0b370ce14c609','MCL-9f4b77d7db2a5ceb','MCL-97ab256f27bab69a','CUR-258e88658b38ad38','MCL-21977b596151a8c1','MCL-906c68dcab1918fd','MCL-94b16e51538e1193','MCL-ae9eade8a82a6c8f','MCL-ddf349fca94c6633','MCL-4c92acd7bb5445f1','MCL-9599579ee6f41207','MCL-ae43a91870f2d84d','MCL-f0af453a8c16714b','MCL-eb4fa2c8374b1359','MCL-07ca2eb2d76b7500','MCL-5e12c7bb993d838a','MCL-3dfdfcfb9fc1b656','MCL-7e0e72f2ec54e028','MCL-01a5ca2ed2a35c42','MCL-0de3ebf3e8464381','MCL-d0dea82ab92274a6','MCL-2c8d7c4ef6e8449d','MCL-e24a2ddbc51d9f97','MCL-85c106837f6a39a8','MCL-c2c48ce89527e0ec','MCL-a443ddfff0691f6f','MCL-f42b42e963581b75','MCL-c346d2d59ffff473','MCL-4b5c1e500979485f','MCL-8d69c2bb075e0c15','MCL-6dfa085c35a11401','MCL-9bcd70097d2893da','MCL-a08770c33cd7d1af','MCL-0c3c37d504b01f38','MCL-912f4fc01153430c','MCL-307f5b9855a598f5','MCL-9ccf623e94dd6414','MCL-3f3cde2e5306852e','MCL-abfacd9d8b4c7585','MCL-249c4808586a7ead','MCL-1a3dedcbfa0bdc7d','MCL-d9da265d026893c3','MCL-0f01c11220cbb5fa','MCL-db31b14ad0a148bd','MCL-6c7dc515e938e540','MCL-095c216ebc2d9949','MCL-96df2a40c896e287','MCL-7d6e7cb6bc2b668f','MCL-ddb9ec73ee76751e','MCL-7b0fcb03188a5ffc','MCL-32d00e380e928e12','MCL-57589fd3e157cb1e','MCL-bdb61764c1323438']),
    classification: 'REVIEWED_ADVICE_WITH_FACTUAL_INPUTS', types: ['REPOSITORY_STATIC_CHECK','CANONICAL_IMPLEMENTATION_SOURCE'],
    rationale: 'This is advice. Review whether it is clear and reasonable, and check any technical facts it relies on. It does not promise a result or require a test rental.',
    next: 'Review the recommendation in this heading, including its assumptions and limits. Use primary technical guidance or the relevant Vast definition for any feature or factual input; do not use this draft as its own proof. Keep advice separate from a claim that an operation succeeded.',
    label: 'Advice review', statusLabel: 'Advice review', reviewKind: 'advice-review',
  },
  {
    ids: new Set(['MCL-08a0259228ce6c01','MCL-9de750468d56faf1','MCL-b319e5b83f8f53ab','MCL-7903a7b953fd13a6','MCL-ffbe126496acafb8','MCL-ac5decb6c41bccd2']),
    classification: 'REVIEWED_ADVICE_WITH_FACTUAL_INPUTS', types: ['REPOSITORY_STATIC_CHECK','CANONICAL_IMPLEMENTATION_SOURCE'],
    rationale: 'This is advice. Review whether it is clear and reasonable, and check any technical facts it relies on. It does not promise a result or require a test rental.',
    next: 'Review the recommendation and its safety limits. Check any named feature or factual input against a primary technical source. This does not prove a device is safe, a machine is eligible, or a support request will succeed.',
    label: 'Advice review', statusLabel: 'Advice review', reviewKind: 'advice-review',
  },
  {
    ids: new Set(['MCL-054a98ae8bf901da','MCL-20ac8bf1404343d1','MCL-11f8abda6c157887','MCL-b9e5bdfb1e78e551','MCL-d0731a0235105443','MCL-e79be1d272044751','MCL-ac95f97ce9cf8be7','MCL-009fe6854feffd7a','MCL-47aa17e2cfb4558a','MCL-ec0258710264c66e']),
    classification: 'REVIEWED_NAVIGATION_INSTRUCTION', types: ['REPOSITORY_STATIC_CHECK'],
    rationale: 'This tells readers where to go or when to use the page. Check the wording and destination, not a rental or platform outcome.',
    next: 'Check the page purpose and any link, heading or label against the current rendered page. A working link does not validate statements on its destination.',
    label: 'Link and wording review', statusLabel: 'Check link and wording', reviewKind: 'navigation-review',
  },
  {
    classification: 'REVIEWED_ADVICE_WITH_FACTUAL_INPUTS', types: ['REPOSITORY_STATIC_CHECK','CANONICAL_IMPLEMENTATION_SOURCE'],
    rationale: 'This is advice. Review whether it is clear and reasonable, and check any technical facts it relies on. It does not promise a result or require a test rental.',
    next: 'Review the recommendation and its safety limits. Check any named feature or factual input against a primary technical source. This does not prove a device is safe, a machine is eligible, or a support request will succeed.',
    label: 'Advice review', statusLabel: 'Advice review', reviewKind: 'advice-review',
  },
  {
    classification: 'REVIEWED_NAVIGATION_INSTRUCTION', types: ['REPOSITORY_STATIC_CHECK'],
    rationale: 'This tells readers where to go or when to use the page. Check the wording and destination, not a rental or platform outcome.',
    next: 'Check the page purpose and any link, heading or label against the current rendered page. A working link does not validate statements on its destination.',
    label: 'Link and wording review', statusLabel: 'Check link and wording', reviewKind: 'navigation-review',
  },
  {
    ids: new Set(['MCL-b61d15c0282ef567','MCL-c59caa4cd52bcc1f','MCL-393941d0e9be9d31','MCL-af1c482a08b09316','MCL-99ca28f707d5966a','MCL-2c3f7082e2c7fdf2','MCL-633317ca7ebecfef','MCL-fe3eccd1cd40b4bd','MCL-03c73e4182b1e7fe']),
    classification: 'REVIEWED_POLICY_RULE', types: ['AUTHORITATIVE_DOCUMENTATION_CITATION'], rationale: reviewedPolicyRationale, next: reviewedPolicyNext,
    label: 'Policy source review', statusLabel: 'Check policy source', reviewKind: 'policy-source-review',
  },
  {
    ids: new Set(['MCL-3b10b5e64ee55003']), classification: 'REVIEWED_POLICY_REFERENCE', types: ['AUTHORITATIVE_DOCUMENTATION_CITATION','REPOSITORY_STATIC_CHECK'],
    rationale: 'This tells hosts to follow the linked policy. Check the applicable approved policy; no new approval or test rental is needed for this instruction.',
    next: 'Check that the link reaches Workload Policy and follow its authoritative policy or agreement source. Do not count two draft pages repeating the instruction as proof.',
    label: 'Policy reference', statusLabel: 'Check policy source', reviewKind: 'policy-reference',
  },
  {
    ids: new Set(['MCL-790d76c6e2bea8fa']), classification: 'REVIEWED_SETUP_INSTRUCTION', types: ['CANONICAL_IMPLEMENTATION_SOURCE','REPOSITORY_STATIC_CHECK'],
    text: '2. **Create a dedicated host account and accept the hosting agreement.** Start from the official [Vast host setup page](https://cloud.vast.ai/host/setup/), then see [Host Account and Agreement](/host/account-hosting-agreement) if the account flow gets stuck. Before using keys or automation, review [Host Account Security](/host/account-security-for-hosts).',
    rationale: 'This is a setup instruction. Check the separate-account and agreement requirements against the official setup rules; no new account or rental is needed to review this wording.',
    next: 'Check the official host setup flow or its canonical code for the separate-account and agreement requirements, and check the linked help pages. A claim that a particular account gained Machines access would need a separate observed result.',
    label: 'Setup review', statusLabel: 'Check setup requirements', reviewKind: 'setup-review',
  },
  {
    ids: new Set(['CUR-d83c946956b9328a','MCL-a3bda9db75c369b4','MCL-83e1933991062890','MCL-368659e99d7579a8','MCL-f2b6a71513a07d91','MCL-5a8901f1b2e4c83e','MCL-1c0c5b93fa68b290','MCL-eb8f13f42bdf73f7','MCL-0df18827bd3203d4','MCL-424d33d6a3638cec','MCL-fb88473a2cbdd618','MCL-ec8fec7a983460fa','MCL-71c4dc412c06d4d0','MCL-3e3923f33a92b548','MCL-85716d9fe2bf9e54','MCL-e287107e6ddc37bd','MCL-fe3d3815536913dc','MCL-072cd83ffa04474f','MCL-84cace0cd47b4af4','MCL-e78ee1438831e63f','MCL-dad1339c420cf9db','MCL-9f1024fef9ec0de1','MCL-d37ccc0c85d792d3','MCL-f426518c26948ea1','MCL-350d25401b2594d2','MCL-e5a99b3d2e81bcae','MCL-9e462bcd0ee70aac','MCL-ff0e592ec9d37394','MCL-fe79b15ff39543a3','MCL-2268c4f831bc7645','MCL-c86e8e5951c1db93','MCL-610efa25a8587e2f','MCL-ca3482eac2556f25','MCL-b5b2716c025774a3','MCL-3896fb44c86e914e']),
    classification: 'ACCOUNT_CONFIGURATION_OR_PERMISSION', types: ['CANONICAL_IMPLEMENTATION_SOURCE','RUNTIME_OR_UI_OBSERVATION'],
    rationale: 'Check this setting, permission or account behavior against the relevant Vast code or API definition. Account-specific effects still need an observed result; mentioning billing or teams does not by itself require policy approval.',
    next: 'Find the exact account, permission or command definition and compare it with this passage. Reuse a suitable retained result for any claimed account effect; if none exists, specify the smallest approved check. Ask the source owner only if the implementation source or meaning is unavailable.',
    label: 'Settings and behavior review', statusLabel: 'Check technical source and retained result', reviewKind: 'settings-review',
  },
];
// Individually reviewed instructions, not a keyword-based policy classifier.
const policyRequests = new Map([
  ['MCL-b61d15c0282ef567', { status: 'FAIL', text: 'Do not run local gaming, mining, display workloads, or other GPU jobs on a rented machine. For policy context, see [Workload Policy](/host/workload-policy).', scope: 'Confirm whether this applies to the whole machine or only the rented resources.', reviewedNextSuffix: ' Confirm whether the rule covers the whole machine or only rented resources.' }],
  ['MCL-c59caa4cd52bcc1f', { status: 'FAIL', text: '| Gaming/workstation use during rentals | Rented machines should be dedicated. |', scope: 'Confirm whether dedication is advice or a requirement, and which resources it covers.', reviewedNextSuffix: ' Preserve “should”; confirm whether dedication is advice or a requirement and which resources it covers.' }],
  ['MCL-af1c482a08b09316', { status: 'FAIL', text: 'While a rental contract is active:\n- Do not run local gaming, mining, benchmarks, display workloads, or background GPU jobs.', scope: 'Confirm whether this applies to the whole machine or only the rented resources.', reviewedNextSuffix: ' Confirm whether the rule covers the whole machine or only rented resources.' }],
  ['MCL-393941d0e9be9d31', { status: 'FAIL', text: 'While a rental contract is active:\n- Do not stop, inspect, modify, or interfere with renter containers because they appear idle.', scope: 'Confirm the instruction for idle rentals. This review does not authorize inspecting or changing renter containers.', reviewedNextSuffix: ' Confirm the idle-rental noninterference scope; do not inspect or change renter containers to test the rule.' }],
  ['MCL-03c73e4182b1e7fe', { status: 'UNVALIDATED', text: '| Rental appears idle | Leave it running. |', suffix: ' Under What To Do on Workload Policy this is a renter noninterference direction; compare the applicable agreement and keep a separate operational rationale. A rental observation alone cannot authorize a restriction.', scope: 'Confirm that the instruction matches the applicable renter noninterference rules.', reviewedNextSuffix: ' Confirm the idle-rental noninterference scope.' }],
  ['MCL-3b10b5e64ee55003', { status: 'UNVALIDATED', text: 'Make sure background work complies with the [Workload Policy](/host/workload-policy).', suffix: ' The advice is to comply with the linked policy. Resolve the actual policy and applicable agreement/terms; no new compliance approval is required to direct readers to the existing rules.', linkOnly: true }],
]);
const productRationale = "Deliberate reviewed correction of an over-demanding runtime-only lane for this exact introductory product description; three independent-of-docs official public pages jointly support its three parts. PASS supports only Vast's published high-level marketplace, Host supply and customer workload capability description. Not runtime observation, individual owner confirmation, a specific rental, machine ownership, health, provisioning or cleanup proof. No Finance, Legal, pricing, security, account or contractual promise is approved. Full HTML bodies are not retained; body hashes are provenance metadata, not replayable page evidence. No human acceptance is inferred.";
// These narrow Terms bindings are deliberately exact: a source-only PASS is
// not a statement about enforcement, acceptance, or any runtime outcome.
const termsRuleCopies = new Map([
  ['MCL-99ca28f707d5966a', {
    rationale: 'PUBLISHED_TERMS_RULE: The retained official Terms introduction supports this bounded link to published prohibited activities only. It does not establish enforcement, runtime checks, monitoring, escalation, account acceptance, or a Host obligation.',
    next: 'Re-review this bounded published Terms citation if the exact occurrence, Terms version, or retained capture changes.',
  }],
  ['MCL-2c3f7082e2c7fdf2', {
    rationale: 'PUBLISHED_TERMS_RULE: The retained official Terms support this exact published rule summary only, including the knowingly limited unlawful or abusive-content wording. It does not establish Host policing, runtime checks, monitoring, escalation, account acceptance, or operational completion.',
    next: 'Re-review this bounded published Terms citation if the exact occurrence, Terms version, or retained capture changes.',
  }],
  ['MCL-c4c4bfc59eb7b49f', {
    rationale: 'PUBLISHED_TERMS_RULE: The retained official Terms support the exact user-facing interference, harmful-material, and spam wording; the retained Hosting Agreement source remains separately cited for its quoted Provider rule. No Host enforcement, runtime behavior, monitoring, escalation, acceptance, or operational completion is inferred.',
    next: 'Re-review these bounded published sources if the exact occurrence, cited Terms/Agreement version, or retained captures change.',
    agreement: true,
  }],
  ['MCL-399798a3c4946b5f', {
    rationale: 'PUBLISHED_TERMS_RULE: The retained official Terms support the exact user-facing third-party-rights clause; the retained Hosting Agreement source remains separately cited for its quoted data-review clause. No Host enforcement, runtime behavior, monitoring, escalation, acceptance, or operational completion is inferred.',
    next: 'Re-review these bounded published sources if the exact occurrence, cited Terms/Agreement version, or retained captures change.',
    agreement: true,
  }],
  ['MCL-633317ca7ebecfef', {
    rationale: 'PUBLISHED_TERMS_RULE: The retained official Terms support the exact user export-control, prohibited-destination/person, restricted-end-use, and authorization wording only. It does not establish Host enforcement, runtime behavior, monitoring, escalation, account acceptance, or operational completion.',
    next: 'Re-review this bounded published Terms citation if the exact occurrence, Terms version, or retained capture changes.',
  }],
  ['MCL-fe3eccd1cd40b4bd', {
    rationale: 'PUBLISHED_TERMS_RULE: The retained official Terms support only the stated cryptocurrency-mining condition for users who purchased service credits with a credit card. It does not establish a blanket rule for every payment method, Host enforcement, runtime behavior, monitoring, escalation, acceptance, or operational completion.',
    next: 'Re-review this bounded published Terms citation if the exact occurrence, Terms version, or retained capture changes.',
  }],
]);

const pricingRevision = 'ecf32efa1d8d2f110f7de4118c30698bb7ae2fbd';
const pricingIntro = 'When editing an offer, distinguish the current rental term from a later extension. The [Vast CLI price-increase guidance](https://github.com/vast-ai/vast-cli/blob/' + pricingRevision + '/vastai/cli/commands/price_increase.py#L123-L145) describes price protection through the current end date and client acceptance of a higher extension rate. Review each change separately:';
const rentalStatementCopies = new Map([
  ['MCL-470bf8ec992a342e', {
    reviewHash: '4d815ed3088b0d4cacdb3c2b2820983a0994f649462d24bb869b74445624a371',
    status: 'FAIL', text: '- Shortening the offer end date affects only future rentals.',
    finding: 'The pricing source does not answer whether shortening an offer changes existing rental end dates. A citation for this statement is still missing.',
    nextStep: 'Find and cite the exact offer or rental rule covering existing rental end dates. Check any claimed system behavior separately.',
  }],
  ['MCL-6e0046c21ac71be4', {
    reviewHash: 'e293d860f7304f0cc6096fbef404832c2569d03ab4ec4d7dc817a2d49fab8a19',
    status: 'FAIL', text: '- The machine must stay available until the latest active rental end date.',
    finding: 'The pricing source does not establish this host obligation. A citation for the required availability period is still missing.',
    nextStep: 'Find and cite the applicable agreement or rule requiring availability through the latest active rental end date.',
    governing: true,
  }],
  ['MCL-8d3286528a924e12', {
    reviewHash: '005410beb5e418281eb1a40edc2eab3f6947479daa68db206795ca5c0837de6e',
    status: 'UNVALIDATED', text: '- Unlisting stops new rentals, but existing contracts continue.',
    finding: 'The pricing source does not show what unlisting does to new or existing rentals. This behavior still needs evidence.',
    nextStep: 'Check the unlisting implementation and any retained test of new and existing rentals. Cite any rental rule this statement relies on.',
  }],
  ['MCL-a4b087a3103c5bdb', {
    reviewHash: '3d31e75d0978774648e808ff5fdeb72f495dde2fc0f44897249161848695c10f',
    status: 'UNVALIDATED', text: '- An offer price change applies to new rentals. Existing renters retain the original rate for their current term; a higher rate for an extension requires their acceptance. See the [Vast CLI price-increase guidance](https://github.com/vast-ai/vast-cli/blob/' + pricingRevision + '/vastai/cli/commands/price_increase.py#L123-L145).',
    finding: 'The CLI guidance describes the pricing rules. The retained sources do not show that the backend or billing applied them to rentals.',
    nextStep: 'Check the implementation and retained rental or billing evidence for new rentals, the current term and an accepted extension.',
    pricing: true,
  }],
]);

// Reader wording for these six unresolved occurrences only. The digest binds
// exact text and recorded review metadata; it does not establish tax practice.
const jurisdictionGapCopies = new Map([
  ['CUR-a991f28f683ba829', {
    reviewHash: '90be0c64672d10e2c8ba31278455c0d128fe39c7b7e4b730fd7701a87984dce4',
    finding: 'The agreement supports independent-contractor status and provider tax responsibility. An official source is still needed for the statements about Vast’s tax-advice services and its ability to verify public tax guidance.',
    nextStep: 'Cite an official Vast statement covering those service limitations.',
  }],
  ['CUR-99fb8d131e321e03', {
    reviewHash: 'e5f4d8c747a3671c0b299dcae6f6ff82cbc16f52b566d7f378c6bb0d77707e77',
    finding: 'Vast’s tax-withholding practice still needs an official supporting source for the relevant jurisdiction and period.',
    nextStep: 'Link the applicable tax rules and an official Vast withholding statement identifying the payer, recipient, jurisdiction and period.',
  }],
  ['CUR-93f089288e67669d', {
    reviewHash: '9412f74ed70dd1657c2652260b4fc6815530ecb3235a3df19356b23354f6b579',
    finding: 'The agreement supports provider tax responsibility. It does not establish which tax documents or advice Vast provides to international hosts. Living outside the United States does not by itself settle US tax obligations.',
    nextStep: 'Cite official Vast document and advice policies, with the applicable jurisdiction and recipient scope.',
  }],
  ['CUR-11f83626486ada1d', {
    reviewHash: 'f734a6c04882ebb1563d53d12c78872048c3e59ec6b753f44eb96d0d1d1903b2',
    finding: 'Sources still need to establish when Vast must collect tax information for Wise payouts and the approved W-9 submission channel.',
    nextStep: 'Cite the applicable reporting rules and Vast’s approved process for collecting the required tax information.',
  }],
  ['CUR-86b30052c0aa0b9c', {
    reviewHash: 'e03fcbcfaf6ff4926ad278fb239cd70892f69d0b78e938634bfc22701088abd5',
    finding: 'Vast’s VAT collection and remittance practice still needs an official supporting source. Being based in California does not determine VAT obligations.',
    nextStep: 'Cite the applicable VAT rules and an official Vast statement with the relevant jurisdiction, service and period.',
  }],
  ['CUR-8eb23dae453fdd8b', {
    reviewHash: 'a005bed30261d354a13cc149c1736aec2997fb21cbb6cc4ec6d06a22540ee5b8',
    finding: 'Whether VAT appears on Vast invoices still needs source and invoice-display evidence. This finding does not determine whether VAT is owed, collected or remitted.',
    nextStep: 'Check current invoice-generation rules and an appropriate retained invoice with personal data removed.',
  }],
]);

// Bounded source/advice findings. The recorded PASS is read, never assigned.
const jurisdictionCheckedCopies = new Map([
  ['CUR-708c718cf735c8b2', {
    reviewHash: 'a64323b44d237800915f36d9790a72294636b2cb716f26a3e2a810e8719d8708',
    label: 'Advice checked', reviewKind: 'advice-review',
    finding: 'Stripe’s guidance supports keeping provider tax details current, within the account and platform’s available options. This review does not establish any host’s tax status or account configuration.',
  }],
  ['CUR-555543e9b2ceddb4', {
    reviewHash: '6b4ac920127c3a692e146597e675642d1d685cfa0fecf44ff8b3f86c33c73704',
    label: 'Advice checked', reviewKind: 'advice-review',
    finding: 'PayPal and IRS guidance support checking the current tax-form rules for the relevant year and location. This review does not decide a host’s form eligibility or income-reporting duties.',
  }],
  ['CUR-2ead4eda972e84b0', {
    reviewHash: 'c4f18f74e9ad3e92e1a2fc9b14939400a5019e4898978fad6e7a6dae2cab63e0',
    label: 'Advice checked', reviewKind: 'advice-review',
    finding: 'IRS guidance supports this advice for US hosts; California guidance applies only when its rules apply to the host. This review does not determine personal tax residency, liability or filing deadlines.',
  }],
  ['MCL-8fe2020c0e7efe26', {
    reviewHash: '267f873748143fe244eef65d29836f83ecae8e6fb02f0076e6963ee40f59ef8f',
    label: 'Advice and rule checked', reviewKind: 'advice-and-rule-review',
    finding: 'The advice to start with host-side evidence and the agreement’s rule against reviewing renter data are supported. This review does not establish report accuracy or a completed investigation.',
  }],
  ['MCL-1536a1bd58d80927', {
    reviewHash: '9bd535276c358039d56aafc7463b1adbb8d50ad9260cbbf4e6d9079c2387d432',
    label: 'Published program source checked', reviewKind: 'published-program-source',
    finding: 'The published program describes higher search placement for certified machines. Actual ranking and reliability were not checked.',
  }],
  ['MCL-c9882f043e407640', {
    reviewHash: '3cce174567917e32552f3f40941f7545e45cd45012dd23286d37c1b6e128ee8d',
    label: 'Published program source checked', reviewKind: 'published-program-source',
    finding: 'The published program describes direct team support for onboarding, troubleshooting and operations. It does not promise a particular chat channel or response time; support delivery was not checked.',
  }],
  ['MCL-c8bf23127171e2b0', {
    reviewHash: '2ed6193fc54971b90b19cf1f32ea20e815bbca27d27c8a4e972b8cb0c1e95b2e',
    label: 'Published program source checked', reviewKind: 'published-program-source',
    finding: 'The published program requires equipment owned by a registered business. This review did not check any applicant’s ownership, eligibility or certification.',
  }],
  ['MCL-3acecd71e6a7b312', {
    reviewHash: '39e4ca95d39d7bd022fe6cfdb32937055517fb6ac5e94baa2e9ce71051213c3a',
    label: 'Published program source checked', reviewKind: 'published-program-source',
    finding: 'The Compliance excerpt describes Secure Cloud datacenter partner audits; the separate Certified Data Center excerpt states registered-business ownership and owner identity verification. These excerpts do not specify which registration documents to submit or show that an applicant completed the checks.',
  }],
]);

export function hostReviewReaderCopy(claim) {
  const rationale = claim.rationale || '';
  const next = claim.next_action ?? claim.nextAction ?? '';
  const types = claim.required_evidence_types ?? claim.requiredEvidenceTypes ?? [];
  const label = claim.status === 'BLOCKED' ? 'What is stopping the check' :
    claim.status === 'UNVALIDATED' ? 'Review pending' : claim.status === 'FAIL' ? 'Correction needed' : 'Finding';
  const payoutInvoiceIds = new Set(['MCL-e2b956d14494e470','MCL-df7b287adb0df683','MCL-5936430d1b2d8de9','MCL-bbd64c772e9b4693','MCL-3d796f5ae7f2020e','MCL-3afd93ae0b6cf8a4']);
  if (payoutInvoiceIds.has(claim.id) && claim.status === 'PASS' &&
      claim.classification === 'PUBLISHED_FINANCIAL_GUIDANCE_DESCRIPTION' &&
      sameTypes(types, ['AUTHORITATIVE_DOCUMENTATION_CITATION']) &&
      rationale === 'Exact attributed published payout guidance supports this wording only. Published guidance checked. This checks what Vast publishes. It does not test invoice generation or payment processing.' &&
      next === 'Recheck this exact published guidance section if its wording or anchor changes.') {
    return {
      label: 'Published guidance checked', statusLabel: 'Published guidance checked', reviewKind: 'published-payout-invoice-guidance',
      finding: 'This passage describes the captured published payout guidance. It does not test invoice generation or payment processing.',
      nextStep: 'Recheck the exact published guidance section if its wording or anchor changes.',
      sourceContextLabel: 'Published guidance checked',
    };
  }
  // This is an exact pending navigation finding, not a calculator adjudication.
  // Any changed wording, method or result must receive a fresh explanation.
  if (claim.id === 'MCL-18f04c2ae7ee95b4' && claim.status === 'UNVALIDATED' &&
      claim.text === '- [Vast hosting earnings calculator](https://vast.ai/hosting/calculator)' &&
      claim.classification === 'REVIEWED_NAVIGATION_INSTRUCTION' &&
      sameTypes(types, ['REPOSITORY_STATIC_CHECK']) &&
      rationale === 'Exact external link/context inspected; no external retrieval was authorized in this repository-only review.' &&
      next === 'Bind an authorized current destination check or a matching retained authoritative source.' &&
      claim.headings?.length === 1 && claim.headings[0] === 'Market Data' &&
      claim.spans?.length === 1 &&
      (claim.spans[0].source_file ?? claim.spans[0].sourceFile) === 'host/earning.mdx' &&
      (claim.spans[0].text_sha256 ?? claim.spans[0].textSha256) === 'de1302d48151ce82ab6e0277d7920877b82f3b568d65b91f5e6137e3f7151245' &&
      (claim.source_refs ?? claim.sourceRefs ?? []).length === 0 &&
      (claim.evidence_refs ?? claim.evidenceRefs ?? []).length === 1 &&
      (claim.evidence_refs ?? claim.evidenceRefs ?? []).some(ref =>
        ref.id === 'EV-HOST-REVIEW-CLEANUP-EDITORIAL-04' &&
        ref.role === 'CURRENT_REPOSITORY_LOCAL_EDITORIAL_INSPECTION' &&
        ref.limit === 'Passage-level editorial/navigation/arithmetic inspection only; no product/runtime proof.' &&
        (ref.artifact_ref ?? ref.artifactRef) === 'verification/evidence/2026-09-11-host-review-cleanup-attempt-01/editorial-local-projection-04.json')) {
    return {
      label: 'Link check pending', statusLabel: 'Check calculator link', reviewKind: 'calculator-link-review',
      finding: 'This entry points readers to the calculator. No saved observation of the destination page is attached to this entry yet.',
      nextStep: 'Open https://vast.ai/hosting/calculator and confirm the intended calculator page loads. Save the final URL, date and time, screenshot, and outcome, then attach that record to this entry. This checks the link only; no paid rental or new owner approval is needed.',
      documentationCheck: {
        finding: 'The saved check confirms the link as written in the document. It does not record a visit to the calculator.',
        scope: 'Link and wording inspection only. It does not establish calculator accuracy or actual earnings.',
      },
      proofGuide: {
        title: 'If reviewing the calculator itself',
        items: [
          {label: 'Calculations', text: 'Identify the formula, units and assumptions in the implementation or published method. Save sample inputs and displayed results, calculate the expected answers independently, and compare them. Code alone is not an observed result.'},
          {label: 'Market history', text: 'If claiming the estimate uses historical market data, identify the actual data source and period, then compare a sample with the calculator inputs. A link to Market Metrics does not prove the calculator uses that data.'},
        ],
        limit: 'These are separate checks, not requirements for closing this link entry. Neither a working link nor correct sample calculations guarantees future earnings.',
      },
    };
  }
  const jurisdictionCopy = jurisdictionGapCopies.get(claim.id) || jurisdictionCheckedCopies.get(claim.id);
  if (jurisdictionCopy && createHash('sha256').update(JSON.stringify([
    claim.text, rationale, next, claim.classification, claim.status, types,
  ])).digest('hex') === jurisdictionCopy.reviewHash) {
    return {
      label: jurisdictionCopy.label || label,
      finding: jurisdictionCopy.finding,
      nextStep: jurisdictionCopy.nextStep || 'Recheck if the wording, page context or supporting source changes.',
      reviewKind: jurisdictionCopy.reviewKind || 'jurisdiction-source-gap',
      ...(jurisdictionCopy.label ? {statusLabel: jurisdictionCopy.label} : {}),
    };
  }
  const split = rentalStatementCopies.get(claim.id);
  // Hashes pin only the existing rationale/action pair, not product truth.
  // A new adjudication must not silently inherit old simplified wording.
  if (split && claim.status === split.status && claim.text === pricingIntro + '\n' + split.text &&
      createHash('sha256').update(JSON.stringify([rationale,next])).digest('hex') === split.reviewHash &&
      claim.spans?.length === 2 &&
      createHash('sha256').update(split.text).digest('hex') === (claim.spans[1].text_sha256 ?? claim.spans[1].textSha256) &&
      claim.classification === (split.governing ? 'GOVERNING_REQUIREMENT' : 'CONTRACT_TERMS_AND_IMPLEMENTED_EFFECT') &&
      sameTypes(types, split.governing ? ['AUTHORITATIVE_DOCUMENTATION_CITATION','CANONICAL_IMPLEMENTATION_SOURCE'] :
        ['CANONICAL_IMPLEMENTATION_SOURCE','RUNTIME_OR_UI_OBSERVATION','AUTHORITATIVE_DOCUMENTATION_CITATION']) &&
      (claim.source_refs ?? claim.sourceRefs ?? []).some(ref => ref.repository === 'vast-ai/vast-cli' &&
        ref.revision === pricingRevision && ref.path === 'vastai/cli/commands/price_increase.py' && ref.locator === '/excerpts/0/text')) {
    return {label, finding: split.finding, nextStep: split.nextStep, reviewKind: 'separate-rental-statement',
      statementText: split.text, statementSpanIndex: 1, relatedClaimId: 'MCL-3d66c8305aa70982',
      sourceContextLabel: split.pricing ? 'Partial support: documented pricing, not observed billing' :
        'Related pricing guidance: not evidence for this statement'};
  }
  const policy = policyRequests.get(claim.id);
  const terms = termsRuleCopies.get(claim.id);
  if (terms && claim.status === 'PASS' && claim.classification === 'PUBLISHED_SOURCE_CLAUSE' &&
      sameTypes(types, ['AUTHORITATIVE_DOCUMENTATION_CITATION']) && rationale === terms.rationale && next === terms.next) {
    return {
      label: 'Finding', reviewKind: 'published-terms-source',
      finding: terms.agreement ? 'The cited Terms and Hosting Agreement support this rule. This does not prove runtime enforcement.' :
        'The cited Terms support this rule. This does not prove runtime enforcement.',
      nextStep: 'Recheck if the wording or cited source changes.',
    };
  }
  const reviewed = reviewedFamilies.find(family =>
    (!family.ids || family.ids.has(claim.id)) && claim.classification === family.classification &&
    (!family.text || claim.text === family.text) &&
    rationale === family.rationale && next === family.next && sameTypes(types, family.types) &&
    (family.statuses || ['UNVALIDATED', 'FAIL']).includes(claim.status));
  if (reviewed) {
    // The five individually reviewed policy examples below deliberately retain
    // the narrower acknowledgement request.  Other policy rules stay in the
    // source-review lane and show their recorded rationale and next action.
    if (!(policy && !policy.linkOnly)) return {
      label: reviewed.label, reviewKind: reviewed.reviewKind, statusLabel: reviewed.statusLabel,
      finding: rationale, nextStep: next,
    };
  }
  if (policy && claim.status === policy.status && claim.text === policy.text &&
      (claim.classification === 'GOVERNING_REQUIREMENT' || claim.classification === 'REVIEWED_POLICY_RULE') && types.length === 1 &&
      types[0] === 'AUTHORITATIVE_DOCUMENTATION_CITATION' &&
      ((rationale === policyRationale + (policy.suffix || '') && next === policyNext) ||
       (rationale === reviewedPolicyRationale && next === reviewedPolicyNext + (policy.reviewedNextSuffix || '')))) {
    if (policy.linkOnly) return {
      label: 'Policy reference', reviewKind: 'policy-reference', statusLabel: 'Check policy source',
      finding: 'This tells hosts to follow the linked policy. It does not need a new approval or a test rental.',
      nextStep: 'Confirm that the linked policy is current, approved and applies to background work. Use its approved source; do not treat two draft pages repeating each other as proof.',
    };
    return {
      label: 'Policy review', reviewKind: 'policy-acknowledgement', statusLabel: 'Needs policy acknowledgement',
      finding: 'Confirm that this instruction matches Vast’s approved policy. No runtime test is needed to establish the rule.',
      nextStep: 'Use the existing approved policy first. If it is missing or unclear, ask the responsible Vast policy owner to confirm or correct this instruction. ' + policy.scope + ' Cite the policy or recorded decision.',
      pendingNote: 'Confirmation and its citation are still pending. This review does not record approval or change the rule.',
    };
  }
  if (claim.id === 'MCL-e12ac9f6be2ce502' && claim.status === 'PASS' &&
      claim.text === 'Vast is a GPU marketplace. Hosts provide machines; renters run workloads on them.' &&
      claim.classification === 'PRODUCT_DESCRIPTION' && rationale === productRationale &&
      types.length === 1 && types[0] === 'PRODUCT_PUBLICATION_SOURCE' &&
      next === 'Re-review this bounded source adjudication if the exact occurrence or retained sources change; no rental or human acceptance is asserted.') {
    return { label: 'Finding', finding: 'Official Vast publications support this basic description. No test rental is needed. This finding covers the published description only.', nextStep: 'Recheck if the wording or supporting sources change.' };
  }
  let finding = rationale;
  let nextStep = next;
  const family = families.get(rationale);
  if (family && ['UNVALIDATED', 'FAIL'].includes(claim.status)) [finding, nextStep] = family;
  if (claim.status === 'FAIL' && types.includes('AUTHORITATIVE_DOCUMENTATION_CITATION') && family) {
    finding += ' The required citation is missing.';
  }
  if (claim.status === 'UNVALIDATED') {
    if (missing.has(rationale)) {
      finding = 'The appropriate review is still pending. No suitable review record is linked to this passage yet.';
      const actions = [];
      if (types.includes('CANONICAL_IMPLEMENTATION_SOURCE')) actions.push('Find the relevant Vast code or API definition.');
      if (types.includes('RUNTIME_OR_UI_OBSERVATION')) actions.push('Run an approved check and save the inputs, result and any cleanup.');
      if (types.includes('AUTHORITATIVE_DOCUMENTATION_CITATION') || types.includes('ACCOUNTABLE_OWNER_CONFIRMATION')) actions.push('Check the relevant published rules or agreement first. Ask the responsible team only about gaps or unclear wording.');
      if (types.includes('PRODUCT_PUBLICATION_SOURCE')) actions.push('Find an official Vast publication supporting this statement.');
      if (types.includes('REPOSITORY_STATIC_CHECK')) actions.push('Check this against the repository and save the result.');
      if (actions.length) nextStep = actions.join(' ');
    }
    // An exact occurrence, not a general assertion about policy or enforcement.
    if (claim.id === 'MCL-790d76c6e2bea8fa' && families.has(rationale) &&
        claim.text === '2. **Create a dedicated host account and accept the hosting agreement.** Start from the official [Vast host setup page](https://cloud.vast.ai/host/setup/), then see [Host Account and Agreement](/host/account-hosting-agreement) if the account flow gets stuck. Before using keys or automation, review [Host Account Security](/host/account-security-for-hosts).') {
      finding = 'The page says you must use a separate host account and accept the agreement. We still need evidence confirming both requirements.';
      nextStep = 'Check Vast’s account setup rules and record what the setup page requires.';
    }
  }
  if (claim.status === 'PASS' && rationale === 'Every local destination in this whole-line navigation occurrence resolves to an exact current repository file and fragment where applicable.') {
    finding = 'All local links in this passage point to existing pages and sections. This does not verify the statements on those pages.';
  }
  if (claim.status === 'NOT_APPLICABLE' && rationale === 'This exact literal is only an editorial scope statement or lead-in; it asserts no product behavior, contractual rule, account state, or completion.') {
    finding = 'This is introductory wording, not a factual claim that needs evidence.';
    nextStep = 'Check it again if the wording adds a factual claim.';
  }
  if (claim.status === 'BLOCKED') {
    finding = rationale.replace(/^UNAVAILABLE_PREREQUISITE [A-Z_]+:\s*/, '');
    nextStep = next.replace(/^Under explicit authorization, provide this prerequisite for [A-Z]+-[a-f\d]+:\s*/, 'Before testing, obtain approval and resolve this gap: ');
  }
  return { label, finding, nextStep };
}
