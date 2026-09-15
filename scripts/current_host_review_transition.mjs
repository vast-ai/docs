/** Select the newest sealed current-Host transition without weakening any
 * predecessor gate.  Terms binding is optional for historical fixtures; a
 * Terms-marked model without its registry fails in its own reader. */
import { loadAuthorityScan } from './current_host_authority_scan.mjs';
import { loadTermsBinding } from './current_host_terms_binding.mjs';
import { loadJurisdiction } from './current_host_jurisdiction.mjs';
import { loadReviewCleanup } from './current_host_review_cleanup.mjs';
import { loadPayoutProviderCorrection } from './current_host_payout_provider_correction.mjs';
import { loadPayoutTermsCorrection } from './current_host_payout_terms_correction.mjs';
import { loadClosureCorrection } from './current_host_closure_correction.mjs';
import { loadPayoutInvoiceCorrection } from './current_host_payout_invoice_correction.mjs';
import { loadSetupMetricsReview } from './current_host_setup_metrics_review.mjs';
import { loadRecoveryEarningsReview } from './current_host_recovery_earnings_review.mjs';
import { loadTeamsConsoleReview } from './current_host_teams_console_review.mjs';
import { loadDiagnosticsSshReview } from './current_host_diagnostics_ssh_review.mjs';
import { loadContinuationReview } from './current_host_continuation_review.mjs';
import { loadEvidenceReuseReview } from './current_host_evidence_reuse_review.mjs';
import { loadSourceFamilyReview } from './current_host_source_family_review.mjs';

export function loadCurrentHostReviewTransition({read, model, exists}) {
  const recoveryEarnings = loadRecoveryEarningsReview({read, model, exists});
  if (recoveryEarnings) return recoveryEarnings;
  const setupMetrics = loadSetupMetricsReview({read, model, exists});
  if (setupMetrics) return setupMetrics;
  const teamsConsole = loadTeamsConsoleReview({read, model, exists});
  if (teamsConsole) return teamsConsole;
  const diagnosticsSsh = loadDiagnosticsSshReview({read, model, exists});
  if (diagnosticsSsh) return diagnosticsSsh;
  const continuation = loadContinuationReview({read, model, exists});
  if (continuation) return continuation;
  const evidenceReuse = loadEvidenceReuseReview({read, model, exists});
  if (evidenceReuse) return evidenceReuse;
  const sourceFamily = loadSourceFamilyReview({read, model, exists});
  if (sourceFamily) return sourceFamily;
  const closure = loadClosureCorrection({read, model, exists});
  if (closure) return closure;
  const payoutInvoice = loadPayoutInvoiceCorrection({read, model, exists});
  if (payoutInvoice) return payoutInvoice;
  const payoutTerms = loadPayoutTermsCorrection({read, model, exists});
  if (payoutTerms) return payoutTerms;
  const payout = loadPayoutProviderCorrection({read, model, exists});
  if (payout) return payout;
  const cleanup = loadReviewCleanup({read, model, exists});
  if (cleanup) return cleanup;
  const jurisdiction = loadJurisdiction({read, model, exists});
  if (jurisdiction) return jurisdiction;
  const terms = loadTermsBinding({read, model, exists});
  return terms || loadAuthorityScan({read, model, exists});
}
