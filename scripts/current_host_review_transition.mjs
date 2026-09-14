/** Select the newest sealed current-Host transition without weakening any
 * predecessor gate.  Terms binding is optional for historical fixtures; a
 * Terms-marked model without its registry fails in its own reader. */
import { loadAuthorityScan } from './current_host_authority_scan.mjs';
import { loadTermsBinding } from './current_host_terms_binding.mjs';
import { loadJurisdiction } from './current_host_jurisdiction.mjs';
import { loadReviewCleanup } from './current_host_review_cleanup.mjs';
import { loadPayoutProviderCorrection } from './current_host_payout_provider_correction.mjs';
import { loadPayoutTermsCorrection } from './current_host_payout_terms_correction.mjs';
import { loadPayoutInvoiceCorrection } from './current_host_payout_invoice_correction.mjs';

export function loadCurrentHostReviewTransition({read, model, exists}) {
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
