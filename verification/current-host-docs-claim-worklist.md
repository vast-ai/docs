# Current Host Docs claim worklist

Current-source claims requiring proof or correction. Historical evidence is carried only where exact source identity is recorded.

Current dispositions: 2008 occurrences (1797 PASS, 95 editorial NOT_APPLICABLE, 116 requiring review or evidence). Most dispositions are automated or exact historical carry-forward; this package records no invented manual completion.

## [Hosting Overview](http://127.0.0.1:4000/host/hosting-overview)

### [Start Here](http://127.0.0.1:4000/host/hosting-overview#start-here) — `MCL-b7862fc23da77b56`

**Status:** UNVALIDATED

**Literal source text:** Create a dedicated host account from the [Vast host setup page](https://cloud.vast.ai/host/setup/). That flow links to the hosting agreement and starts host onboarding, including access to the Machines area after the agreement is accepted.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Documentation technical-source reviewer

**Next:** Inspect canonical account/team/auth/invoice/payout configuration and applicable retained console or API observation for the exact transition. Existing general docs are navigation to sources, not terminal proof.

### [Offers And Rental Contracts](http://127.0.0.1:4000/host/hosting-overview#offers-and-rental-contracts) — `MCL-3b63eef0c333379b`

**Status:** UNVALIDATED

**Literal source text:** An offer is the listing renters can accept. Key offer settings include:

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Documentation technical-source reviewer

**Next:** Locate the exact canonical implementation/schema/configuration for this behavior and reuse applicable retained source/execution/UI evidence. Client dispatch or documentation alone cannot prove backend effects.

### [The Rental Contract](http://127.0.0.1:4000/host/hosting-overview#the-rental-contract) — `MCL-956cf053a5801e8d`

**Status:** UNVALIDATED

**Literal source text:** Each rental contract is independent. A multi-GPU machine can have several active contracts with different renters, prices, and end dates.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Documentation technical-source reviewer

**Next:** Locate the exact canonical implementation/schema/configuration for this behavior and reuse applicable retained source/execution/UI evidence. Client dispatch or documentation alone cannot prove backend effects.

### [Offer End Date](http://127.0.0.1:4000/host/hosting-overview#offer-end-date) — `MCL-0246358c365900db`

**Status:** UNVALIDATED

**Literal source text:** Set an offer end date before listing. If you leave it open indefinitely, you may create a longer commitment than intended.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Documentation technical-source reviewer

**Next:** Record the engineering rationale, inspect relevant canonical technical behavior, and reuse applicable retained observations. Split guidance from any actual obligation or effect when their methods differ.

### [Volume Offers](http://127.0.0.1:4000/host/hosting-overview#volume-offers) — `MCL-31d29b7bc5df0ef5`

**Status:** UNVALIDATED

**Literal source text:** Volume offers rent storage space separately from GPU offers. Rented volume space comes from the same disk pool used by GPU rentals, so it reduces storage available for GPU offers only when actually rented or occupied. See [Volume Offers](/host/volume-offers) for the host/renter lifecycle, identifiers, shared-capacity planning, limits, and the complete command map.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host Product and Documentation content owner; Authorized Host/API operator

**Next:** The Host Product and Documentation content owner supplies the exact repository, revision, path, and symbol/operation locator; bind it to MCL-31d29b7bc5df0ef5 and retain the focused source check. An authorized Host/API operator runs only an approved representative check for MCL-31d29b7bc5df0ef5 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Introduction](http://127.0.0.1:4000/host/hosting-overview) — `CUR-d83c946956b9328a`

**Status:** UNVALIDATED

**Literal source text:** For community help, connect your host account to Discord and use the [host-only channels](https://discord.gg/hSuEbSQ4X8).

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Documentation technical-source reviewer

**Next:** Find the exact account, permission or command definition and compare it with this passage. Reuse a suitable retained result for any claimed account effect; if none exists, specify the smallest approved check. Ask the source owner only if the implementation source or meaning is unavailable.

## [Supported Hardware](http://127.0.0.1:4000/host/supported-hardware)

### [Introduction](http://127.0.0.1:4000/host/supported-hardware) — `MCL-dbbeba126a396851`

**Status:** UNVALIDATED

**Literal source text:** Meeting minimum requirements makes a machine eligible. It does not guarantee verification, search placement, rentals, or earnings.

**Required proof:** Authoritative Documentation Citation, Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Documentation authoritative-source reviewer

**Next:** Inspect the current official datacenter application/program publication or verification requirements as applicable, then applicable configuration/enforcement and retained UI. Do not use a generic marketing page to prove a specific threshold.

### [Quick Check](http://127.0.0.1:4000/host/supported-hardware#quick-check) — `MCL-dd01d426b53b2e5f`

**Status:** UNVALIDATED

**Literal source text:** - Supported NVIDIA GPUs, or the AMD families listed below.

**Required proof:** Published Vendor Documentation, Repository Static Check

**Existing proof / limit:** [EVIDENCE-REUSE-MCL-dd01d426b53b2e5f-1](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/a-policy-account/setup-browser-response.json) — Exact retained selector; source/runtime boundary is stated in the passage review.; [EVIDENCE-REUSE-MCL-dd01d426b53b2e5f-2](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/requirement-con-1516.json) — Exact retained selector; source/runtime boundary is stated in the passage review.

**Responsible role:** Documentation technical-source reviewer; implementation source owner only for an unavailable or unclear definition

**Next:** Obtain the current supported AMD/ROCm host families and their listing/verification limits from the setup/product owner, then reconcile the quick check and AMD table together.

### [Quick Check](http://127.0.0.1:4000/host/supported-hardware#quick-check) — `MCL-22c6970e6e4f9904`

**Status:** UNVALIDATED

**Literal source text:** - More than 7 GiB VRAM per GPU.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-22c6970e6e4f9904 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Quick Check](http://127.0.0.1:4000/host/supported-hardware#quick-check) — `MCL-5413b0eb68620dc3`

**Status:** UNVALIDATED

**Literal source text:** - AVX-capable CPU.

**Required proof:** Published Vendor Documentation, Repository Static Check

**Existing proof / limit:** [EVIDENCE-REUSE-MCL-5413b0eb68620dc3-1](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/a-policy-account/setup-browser-response.json) — Exact retained selector; source/runtime boundary is stated in the passage review.

**Responsible role:** Documentation technical-source reviewer; implementation source owner only for an unavailable or unclear definition

**Next:** Confirm which CPU feature checks apply separately to x86_64 and ARM64 hosts and reconcile the AVX and architecture rows.

### [Quick Check](http://127.0.0.1:4000/host/supported-hardware#quick-check) — `MCL-d8c581b080df635b`

**Status:** UNVALIDATED

**Literal source text:** - At least one physical CPU core per visible/listed GPU. Hyperthreads do not count.

**Required proof:** Authoritative Documentation Citation, Accountable Owner Confirmation

**Existing proof / limit:** [EVIDENCE-REUSE-MCL-d8c581b080df635b-1](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/owner-source-1518.json) — Exact retained selector; source/runtime boundary is stated in the passage review.; [EVIDENCE-REUSE-MCL-d8c581b080df635b-2](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/a-policy-account/setup-browser-response.json) — Exact retained selector; source/runtime boundary is stated in the passage review.; [EVIDENCE-REUSE-MCL-d8c581b080df635b-3](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/b-hardware-install/sources/cpu-policy-discrepancy.json) — Exact retained selector; source/runtime boundary is stated in the passage review.

**Responsible role:** Host Product/Engineering owner

**Next:** Ask the Host Product/Engineering owner to confirm the current physical-CPU-core requirement per GPU and whether listing, verification and image diagnostics intentionally differ; reconcile the current Setup two-core statement with the dated one-core answer. Keep CLI offer-counter and image physical-counter definitions separate. Then review the entire literal before changing its wording or status.

### [Quick Check](http://127.0.0.1:4000/host/supported-hardware#quick-check) — `MCL-014cf72e3bc1fddf`

**Status:** UNVALIDATED

**Literal source text:** - Enough system RAM for the GPU tier.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-014cf72e3bc1fddf and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Quick Check](http://127.0.0.1:4000/host/supported-hardware#quick-check) — `MCL-d8e81695f7b8ac5d`

**Status:** UNVALIDATED

**Literal source text:** - Fast SSD/NVMe storage, with at least 128 GB per GPU as a listing baseline.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-d8e81695f7b8ac5d and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Quick Check](http://127.0.0.1:4000/host/supported-hardware#quick-check) — `MCL-a917eb0bbbae4890`

**Status:** UNVALIDATED

**Literal source text:** - Public inbound networking with direct TCP and UDP port forwarding.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-a917eb0bbbae4890 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [GPU Support](http://127.0.0.1:4000/host/supported-hardware#gpu-support) — `MCL-ec6ce17ba9330504`

**Status:** UNVALIDATED

**Literal source text:** | NVIDIA | 10-series or newer. Newer datacenter, workstation, and recent consumer GPUs are more attractive to renters. |

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-ec6ce17ba9330504 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [GPU Support](http://127.0.0.1:4000/host/supported-hardware#gpu-support) — `MCL-6842b63298275c23`

**Status:** UNVALIDATED

**Literal source text:** | AMD | MI25 or newer Radeon Instinct, Radeon VII, Radeon Pro VII, Radeon RX 7900 GRE/XT/XTX, and Radeon Pro W7900/W7800. Other 6000-series or newer Radeon RX/Pro W GPUs may work, but may not appear in standard ROCm filters. |

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-6842b63298275c23 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Minimum Listing Baseline](http://127.0.0.1:4000/host/supported-hardware#minimum-listing-baseline) — `MCL-70cdd39ea57d36f0`

**Status:** UNVALIDATED

**Literal source text:** | Machine use | Dedicated host machine while rented. |

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-70cdd39ea57d36f0 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Minimum Listing Baseline](http://127.0.0.1:4000/host/supported-hardware#minimum-listing-baseline) — `MCL-c569a7d52ef2d67c`

**Status:** UNVALIDATED

**Literal source text:** | CPU | AVX-capable, with at least one physical core per listed GPU. |

**Required proof:** Authoritative Documentation Citation, Accountable Owner Confirmation

**Existing proof / limit:** [EVIDENCE-REUSE-MCL-c569a7d52ef2d67c-1](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/owner-source-1518.json) — Exact retained selector; source/runtime boundary is stated in the passage review.; [EVIDENCE-REUSE-MCL-c569a7d52ef2d67c-2](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/a-policy-account/setup-browser-response.json) — Exact retained selector; source/runtime boundary is stated in the passage review.; [EVIDENCE-REUSE-MCL-c569a7d52ef2d67c-3](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/b-hardware-install/sources/cpu-policy-discrepancy.json) — Exact retained selector; source/runtime boundary is stated in the passage review.

**Responsible role:** Host Product/Engineering owner

**Next:** Ask the Host Product/Engineering owner to confirm the current physical-CPU-core requirement per GPU and whether listing, verification and image diagnostics intentionally differ; reconcile the current Setup two-core statement with the dated one-core answer. Keep CLI offer-counter and image physical-counter definitions separate. Then review the entire literal before changing its wording or status.

### [Minimum Listing Baseline](http://127.0.0.1:4000/host/supported-hardware#minimum-listing-baseline) — `MCL-2cee95fda0495911`

**Status:** UNVALIDATED

**Literal source text:** | System RAM | At least 4 GB per GPU as a listing baseline; high-VRAM GPUs may need more. |

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-2cee95fda0495911 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Minimum Listing Baseline](http://127.0.0.1:4000/host/supported-hardware#minimum-listing-baseline) — `MCL-d09b4f5036615d3a`

**Status:** UNVALIDATED

**Literal source text:** | Storage | Fast SSD/NVMe, at least 128 GB per GPU. |

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-d09b4f5036615d3a and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Minimum Listing Baseline](http://127.0.0.1:4000/host/supported-hardware#minimum-listing-baseline) — `MCL-cea060612b933be3`

**Status:** UNVALIDATED

**Literal source text:** | Network | Reliable public inbound connectivity for the configured port range. |

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-cea060612b933be3 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Balance Matters](http://127.0.0.1:4000/host/supported-hardware#balance-matters) — `MCL-33e45499d30e77f5`

**Status:** UNVALIDATED

**Literal source text:** A strong GPU can still be a poor host if the rest of the machine is weak. Match CPU, RAM, PCIe, storage, cooling, power, and network capacity to the GPU tier.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-33e45499d30e77f5 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Balance Matters](http://127.0.0.1:4000/host/supported-hardware#balance-matters) — `MCL-82c7f3f9ab52b1e8`

**Status:** UNVALIDATED

**Literal source text:** Avoid reducing GPU count, RAM, disk, or other capacity after the machine is created; reductions can trigger deverification.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-82c7f3f9ab52b1e8 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Storage And Network](http://127.0.0.1:4000/host/supported-hardware#storage-and-network) — `MCL-ff39602a6bb66e32`

**Status:** UNVALIDATED

**Literal source text:** Docker storage should be fast, predictable, and mounted before Docker starts. Vast uses XFS project quotas for per-container storage limits. See [Storage Setup](/host/storage-setup).

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-ff39602a6bb66e32 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Storage And Network](http://127.0.0.1:4000/host/supported-hardware#storage-and-network) — `MCL-3ae1ef3a04b05d55`

**Status:** UNVALIDATED

**Literal source text:** Hosts also need public inbound connectivity. CGNAT, double NAT without a real public forwarding path, blocked ports, IPv6-only service, LAN-only port forwarding, packet loss, or unstable upload can prevent listing, self-test, or rentals. See [Network & Ports](/host/network-ports).

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-3ae1ef3a04b05d55 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Unsupported Or Discouraged Setups](http://127.0.0.1:4000/host/supported-hardware#unsupported-or-discouraged-setups) — `MCL-e80976b585f7867e`

**Status:** UNVALIDATED

**Literal source text:** | Mixed GPU models | Complicates offers, verification, and renter expectations. |

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-e80976b585f7867e and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Unsupported Or Discouraged Setups](http://127.0.0.1:4000/host/supported-hardware#unsupported-or-discouraged-setups) — `MCL-50d830db2c44850b`

**Status:** UNVALIDATED

**Literal source text:** | No public inbound networking | Connectivity checks and renter access can fail. |

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-50d830db2c44850b and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

## [Earnings & Pricing Model](http://127.0.0.1:4000/host/earning)

### [Introduction](http://127.0.0.1:4000/host/earning) — `MCL-5b6bc28b279709b4`

**Status:** UNVALIDATED

**Literal source text:** Earnings are not guaranteed. Demand, supply, reliability, search filters, location, and renter requirements all affect utilization.

**Required proof:** Authoritative Documentation Citation, Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Documentation authoritative-source reviewer

**Next:** Inspect the current official datacenter application/program publication or verification requirements as applicable, then applicable configuration/enforcement and retained UI. Do not use a generic marketing page to prove a specific threshold.

### [Compute-Only Monthly Model](http://127.0.0.1:4000/host/earning#compute-only-monthly-model) — `MCL-3b5573f171e1df39`

**Status:** UNVALIDATED

**Literal source text:** | `hourly GPU price` | Expected host-side dollars per GPU-hour. Use comparable listings. |

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-3b5573f171e1df39 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [30-Day Range](http://127.0.0.1:4000/host/earning#30-day-range) — `MCL-1cff5f750ca7b8b2`

**Status:** UNVALIDATED

**Literal source text:** Use P90 only when your machine has a real advantage: strong reliability, better network, fast storage, better location, datacenter status, or scarce GPU supply. Then add realistic storage, bandwidth, and volume assumptions separately.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-1cff5f750ca7b8b2 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [30-Day Range](http://127.0.0.1:4000/host/earning#30-day-range) — `MCL-a35107ea06772e33`

**Status:** UNVALIDATED

**Literal source text:** For a fast market-dashboard estimate, use the **GPU Overview** tab in [Host Market](https://cloud.vast.ai/host/market/): multiply `$/HR MED` by `% Rented (30D Avg)`, then multiply by `720` hours and your GPU count. See [GPU Market Metrics: GPU Overview Income Estimate](/host/market-metrics#gpu-overview-income-estimate).

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-a35107ea06772e33 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Compute-Only Example](http://127.0.0.1:4000/host/earning#compute-only-example) — `MCL-f1e6d4aaab85f9d6`

**Status:** UNVALIDATED

**Literal source text:** A 4-GPU host at 55% utilization:

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-f1e6d4aaab85f9d6 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [What To Compare](http://127.0.0.1:4000/host/earning#what-to-compare) — `MCL-f2c28cfd1aa6c89a`

**Status:** UNVALIDATED

**Literal source text:** - GPU model and count.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-f2c28cfd1aa6c89a and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

## [Tax Guide for Hosts](http://127.0.0.1:4000/host/guide-to-taxes)

### [Introduction](http://127.0.0.1:4000/host/guide-to-taxes) — `CUR-99fb8d131e321e03`

**Status:** UNVALIDATED

**Literal source text:** **Important:** Vast.ai does not automatically withhold taxes.

**Required proof:** Authoritative Documentation Citation

**Existing proof / limit:** [EVIDENCE-REUSE-CUR-99fb8d131e321e03-1](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/a-policy-account/published-current.json) — Exact retained selector; source/runtime boundary is stated in the passage review.; [EVIDENCE-REUSE-CUR-99fb8d131e321e03-2](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/a-policy-account/existing-owner-question-excerpts.json) — Exact retained selector; source/runtime boundary is stated in the passage review.

**Responsible role:** Documentation authoritative-source reviewer

**Next:** Ask Vast Finance/Tax to confirm current withholding practice and its jurisdiction/account exceptions in an approved source, or approve the pending tax-guide scope/removal decision.

### [By Payout Method](http://127.0.0.1:4000/host/guide-to-taxes#by-payout-method) — `CUR-11f83626486ada1d`

**Status:** FAIL

**Literal source text:** **Wise** If you are a **US-based host** receiving payouts via Wise, Vast.ai is required to collect your tax information directly. Please contact support for guidance on how to safely send your W9 to Vast.ai.

**Required proof:** Authoritative Documentation Citation

**Existing proof / limit:** No retained proof

**Responsible role:** Documentation authoritative-source reviewer

**Next:** Inspect applicable tax authority/provider guidance and existing official Vast reporting/withholding statement for the exact jurisdiction, period, and actor; retain those applicability limits.

### [Does Vast.ai handle VAT?](http://127.0.0.1:4000/host/guide-to-taxes#does-vast-ai-handle-vat) — `CUR-86b30052c0aa0b9c`

**Status:** FAIL

**Literal source text:** Vast.ai is based in California and does not currently collect or remit VAT.

**Required proof:** Authoritative Documentation Citation

**Existing proof / limit:** No retained proof

**Responsible role:** Documentation authoritative-source reviewer

**Next:** Inspect applicable tax authority/provider guidance and existing official Vast reporting/withholding statement for the exact jurisdiction, period, and actor; retain those applicability limits.

### [Is VAT shown on invoices?](http://127.0.0.1:4000/host/guide-to-taxes#is-vat-shown-on-invoices) — `CUR-8eb23dae453fdd8b`

**Status:** UNVALIDATED

**Literal source text:** VAT is not currently specified on Vast.ai invoices.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Documentation technical-source reviewer

**Next:** Locate the exact canonical implementation/schema/configuration for this behavior and reuse applicable retained source/execution/UI evidence. Client dispatch or documentation alone cannot prove backend effects.

## [Hardware Prep](http://127.0.0.1:4000/host/hardware-prep)

### [What should be ready before I run the host installer?](http://127.0.0.1:4000/host/hardware-prep#what-should-be-ready-before-i-run-the-host-installer) — `MCL-14fafb4770a2b16f`

**Status:** UNVALIDATED

**Literal source text:** Before installing, make sure the host has supported same-type GPUs, native Ubuntu/Linux, an AVX-capable CPU, at least one physical CPU core per listed GPU, adequate RAM, fast SSD/NVMe storage, working compatible GPU drivers, stable public networking, and enough direct ports forwarded for both TCP and UDP.

**Required proof:** Canonical Implementation Source, Authoritative Documentation Citation, Accountable Owner Confirmation

**Existing proof / limit:** [EVIDENCE-REUSE-MCL-14fafb4770a2b16f-1](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/owner-source-1518.json) — Exact retained selector; source/runtime boundary is stated in the passage review.; [EVIDENCE-REUSE-MCL-14fafb4770a2b16f-2](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/a-policy-account/setup-browser-response.json) — Exact retained selector; source/runtime boundary is stated in the passage review.; [EVIDENCE-REUSE-MCL-14fafb4770a2b16f-3](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/b-hardware-install/sources/cpu-policy-discrepancy.json) — Exact retained selector; source/runtime boundary is stated in the passage review.

**Responsible role:** Host Product/Engineering owner

**Next:** Ask the Host Product/Engineering owner to confirm the current physical-CPU-core requirement per GPU and whether listing, verification and image diagnostics intentionally differ; reconcile the current Setup two-core statement with the dated one-core answer. Keep CLI offer-counter and image physical-counter definitions separate. Then review the entire literal before changing its wording or status.

### [What should be ready before I run the host installer?](http://127.0.0.1:4000/host/hardware-prep#what-should-be-ready-before-i-run-the-host-installer) — `MCL-71aa2b81147538fb`

**Status:** UNVALIDATED

**Literal source text:** For CPU capacity, use the physical-core rule: the host should have at least one visible physical CPU core per visible GPU. Hyperthreads and logical CPUs do not count as physical cores.

**Required proof:** Authoritative Documentation Citation, Accountable Owner Confirmation

**Existing proof / limit:** [EVIDENCE-REUSE-MCL-71aa2b81147538fb-1](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/owner-source-1518.json) — Exact retained selector; source/runtime boundary is stated in the passage review.; [EVIDENCE-REUSE-MCL-71aa2b81147538fb-2](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/a-policy-account/setup-browser-response.json) — Exact retained selector; source/runtime boundary is stated in the passage review.; [EVIDENCE-REUSE-MCL-71aa2b81147538fb-3](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/b-hardware-install/sources/cpu-policy-discrepancy.json) — Exact retained selector; source/runtime boundary is stated in the passage review.

**Responsible role:** Host Product/Engineering owner

**Next:** Ask the Host Product/Engineering owner to confirm the current physical-CPU-core requirement per GPU and whether listing, verification and image diagnostics intentionally differ; reconcile the current Setup two-core statement with the dated one-core answer. Keep CLI offer-counter and image physical-counter definitions separate. Then review the entire literal before changing its wording or status.

## [Headless Hosting Guide](http://127.0.0.1:4000/host/headless-install)

### [Step 8: Configure GRUB Only When Needed](http://127.0.0.1:4000/host/headless-install#step-8-configure-grub-only-when-needed) — `MCL-673370399b8669d9`

**Status:** BLOCKED

**Literal source text:** ```bash sudo update-grub ```

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** [EV-HOST-COMMAND-OCCURRENCE-RECONCILIATION-01](evidence/2026-09-03-host-repository-rebase-01/result.md) — Static or partial evidence does not establish the prohibited or unavailable runtime behavior.

**Responsible role:** Authorized Host/API operator

**Next:** Under explicit authorization, provide this prerequisite for CLM-2872a25df6add3a5: Explicit operator authorization and a controlled disposable or idle Host are unavailable for changing the bootloader configuration. Then retain the exact observation and cleanup.

## [How to Self-Test](http://127.0.0.1:4000/host/how-to-self-test)

### [Before You Run It](http://127.0.0.1:4000/host/how-to-self-test#before-you-run-it) — `MCL-9ad33b25fd88c5cb`

**Status:** FAIL

**Literal source text:** ```bash vastai set api-key <API_KEY> ```

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** [EV-CLI-SET-API-KEY-PERMISSIONS-01](evidence/2026-09-02-cli-set-api-key-permissions-attempt-01/result.md) — The retained adverse command result concerns a security/output property not asserted by the literal fenced syntax alone; the exact documentation claim remains UNVALIDATED rather than being falsely contradicted.; [EVIDENCE-REUSE-MCL-9ad33b25fd88c5cb-1](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/b-hardware-install/sources/auth.py) — Exact retained selector; source/runtime boundary is stated in the passage review.

**Responsible role:** Self-Test and Verification source owner; Authorized Host/API operator

**Next:** Provide a secure key-storage path or verify a corrected CLI release; retain the existing isolated0644 failure and test a restrictive new-file/existing-file workflow before promoting this credential instruction.

### [Run The Test](http://127.0.0.1:4000/host/how-to-self-test#run-the-test) — `MCL-eeaf6da83da9eca7`

**Status:** BLOCKED

**Literal source text:** ```bash vastai self-test machine <machine_id> \   --support-bundle-dir /path/to/output ```

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** [CONNECTION-MCL-eeaf6da83da9eca7-01](current-host-connection-adjudications.json) — Exact normal support-bundle preflight only. No diagnostic rental, image execution, remote logs, runtime workload, verification, kernel result, or final billing outcome occurred.; [SELFTEST_PREFLIGHT](evidence/2026-09-09-host-ssh-jupyter-selftest-attempt-01/selftest-normal-preflight-01.json) — Exact normal support-bundle preflight only. No diagnostic rental, image execution, remote logs, runtime workload, verification, kernel result, or final billing outcome occurred.; [CANONICAL_CLI](evidence/2026-09-09-host-ssh-jupyter-selftest-attempt-01/canonical-cli-source-01.json) — Exact normal support-bundle preflight only. No diagnostic rental, image execution, remote logs, runtime workload, verification, kernel result, or final billing outcome occurred.

**Responsible role:** Self-Test and Verification source owner; Authorized Host/API operator

**Next:** Resolve the measured reliability and upload prerequisites, then use a new approved idle rental to rerun the normal support-bundle command. Do not call raw exit 0 or this preflight outcome a self-test runtime PASS.

## [Optimize Your Earnings](http://127.0.0.1:4000/host/optimization-guide)

### [Introduction](http://127.0.0.1:4000/host/optimization-guide) — `MCL-ad97857bfa72cad9`

**Status:** UNVALIDATED

**Literal source text:** Use this page after your machine is ready to list. Hardware matters, but listing settings decide who can find and rent it.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-ad97857bfa72cad9 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Core Rule](http://127.0.0.1:4000/host/optimization-guide#core-rule) — `MCL-77a49245c082175e`

**Status:** UNVALIDATED

**Literal source text:** Before changing settings, compare similar machines by GPU model, GPU count, verification state, region, reliability, storage, bandwidth, and listing duration.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-77a49245c082175e and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Core Rule](http://127.0.0.1:4000/host/optimization-guide#core-rule) — `MCL-62e3175c4db97642`

**Status:** UNVALIDATED

**Literal source text:** Renters commonly filter by verification state, rental duration, and disk space. If your listing does not pass those filters, price alone will not make it visible to the renters you want.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Documentation technical-source reviewer

**Next:** Locate the exact canonical implementation/schema/configuration for this behavior and reuse applicable retained source/execution/UI evidence. Client dispatch or documentation alone cannot prove backend effects.

### [Duration](http://127.0.0.1:4000/host/optimization-guide#duration) — `MCL-45898b6578e27858`

**Status:** UNVALIDATED

**Literal source text:** | Less commitment | Stronger availability promise |

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation, Authoritative Documentation Citation

**Existing proof / limit:** No retained proof

**Responsible role:** Documentation authoritative-source reviewer

**Next:** Inspect the retained agreement Offer/Rental Contract/Operation and Maintenance clauses and any current published terms; bind only supported clauses. Inspect the corresponding offer/update/unlist/extension implementation and retained execution for actual system effects.

### [Min GPU](http://127.0.0.1:4000/host/optimization-guide#min-gpu) — `MCL-f166af02a80b03bc`

**Status:** UNVALIDATED

**Literal source text:** `min_gpu` controls the smallest GPU slice renters can choose.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-f166af02a80b03bc and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Min GPU](http://127.0.0.1:4000/host/optimization-guide#min-gpu) — `MCL-74657cb19f5c28f4`

**Status:** UNVALIDATED

**Literal source text:** | More renters can use the machine | Better fit for full-node workloads |

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-74657cb19f5c28f4 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Min GPU](http://127.0.0.1:4000/host/optimization-guide#min-gpu) — `MCL-1bd94e9310cacf0d`

**Status:** UNVALIDATED

**Literal source text:** | Higher fragmentation risk | Lower fragmentation |

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-1bd94e9310cacf0d and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Min GPU](http://127.0.0.1:4000/host/optimization-guide#min-gpu) — `MCL-9094b9aa0c52e505`

**Status:** UNVALIDATED

**Literal source text:** | Can improve occupancy | Can miss small-job demand |

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-9094b9aa0c52e505 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Min GPU](http://127.0.0.1:4000/host/optimization-guide#min-gpu) — `MCL-309bc988193e16b5`

**Status:** UNVALIDATED

**Literal source text:** For an 8-GPU machine, a `min_gpu` of `2` creates 2x, 4x, and 8x listing options. A `min_gpu` of `8` creates only a full-node option.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Product and Finance owner; Authorized Host/API operator

**Next:** The Product and Finance owner supplies the exact repository, revision, path, and symbol/operation locator; bind it to MCL-309bc988193e16b5 and retain the focused source check. An authorized Host/API operator runs only an approved representative check for MCL-309bc988193e16b5 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Min GPU](http://127.0.0.1:4000/host/optimization-guide#min-gpu) — `MCL-2346f746d6a41615`

**Status:** UNVALIDATED

**Literal source text:** For fleets, mix `min_gpu` values across machines instead of setting every host the same way.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-2346f746d6a41615 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Min GPU](http://127.0.0.1:4000/host/optimization-guide#min-gpu) — `MCL-4b7ceacf92e47a2f`

**Status:** UNVALIDATED

**Literal source text:** | A | `1` | 1x, 2x, 4x, 8x |

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-4b7ceacf92e47a2f and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Min GPU](http://127.0.0.1:4000/host/optimization-guide#min-gpu) — `MCL-5ff3652dff3c6570`

**Status:** UNVALIDATED

**Literal source text:** | B | `2` | 2x, 4x, 8x |

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-5ff3652dff3c6570 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Min GPU](http://127.0.0.1:4000/host/optimization-guide#min-gpu) — `MCL-94975fee1bc2b136`

**Status:** UNVALIDATED

**Literal source text:** | C | `4` | 4x, 8x |

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-94975fee1bc2b136 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Min GPU](http://127.0.0.1:4000/host/optimization-guide#min-gpu) — `MCL-b0ae349a48ac8704`

**Status:** UNVALIDATED

**Literal source text:** | D | `8` | 8x only |

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-b0ae349a48ac8704 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Min GPU](http://127.0.0.1:4000/host/optimization-guide#min-gpu) — `MCL-b9a2234d232976cd`

**Status:** UNVALIDATED

**Literal source text:** Avoid setting every machine to `1` if it creates fragmentation you cannot fill. Avoid setting every machine to full-node only unless you know there is enough demand for that exact GPU class and configuration.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-b9a2234d232976cd and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Keep The Listing Competitive](http://127.0.0.1:4000/host/optimization-guide#keep-the-listing-competitive) — `MCL-f09d755d9fc2c3a4`

**Status:** UNVALIDATED

**Literal source text:** - Run self-test after setup and major changes.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-f09d755d9fc2c3a4 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

## [Verification Stages](http://127.0.0.1:4000/host/verification-stages)

### [CPU](http://127.0.0.1:4000/host/verification-stages#cpu) — `CUR-1da68c391b45b80a`

**Status:** UNVALIDATED

**Literal source text:** | Instruction set | AVX |

**Required proof:** Authoritative Documentation Citation, Accountable Owner Confirmation

**Existing proof / limit:** [EVIDENCE-REUSE-CUR-1da68c391b45b80a-1](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/c-operations-verification/sources/upstream-verification.mdx) — Exact retained selector; source/runtime boundary is stated in the passage review.; [EVIDENCE-REUSE-CUR-1da68c391b45b80a-2](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/requirement-con-1516.json) — Exact retained selector; source/runtime boundary is stated in the passage review.; [EVIDENCE-REUSE-CUR-1da68c391b45b80a-3](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/c-operations-verification/sources/context_verification-stages.mdx) — Exact retained selector; source/runtime boundary is stated in the passage review.; [EVIDENCE-REUSE-CUR-1da68c391b45b80a-4](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/c-operations-verification/sources/setup-requirement-excerpts.json) — Exact retained selector; source/runtime boundary is stated in the passage review.; [VERIFICATION-STORAGE-CUR-1da68c391b45b80a-1](evidence/2026-09-15-host-continuation-verification-selftest-attempt-01/source-pages/verification-stages.mdx) — No Host, account, installation, network, image publication, rental, self-test or paid operation was performed. The pinned CLI and image revisions are distinct; their code does not prove the deployed image or platform verification algorithm. Prior evidence and procedure status remain unchanged.; [VERIFICATION-STORAGE-CUR-1da68c391b45b80a-2](evidence/2026-09-15-host-continuation-verification-selftest-attempt-01/primary/source-excerpts.json) — No Host, account, installation, network, image publication, rental, self-test or paid operation was performed. The pinned CLI and image revisions are distinct; their code does not prove the deployed image or platform verification algorithm. Prior evidence and procedure status remain unchanged.; [VERIFICATION-STORAGE-CUR-1da68c391b45b80a-3](evidence/2026-09-15-host-continuation-verification-selftest-attempt-01/primary/published-verification-stages.md) — No Host, account, installation, network, image publication, rental, self-test or paid operation was performed. The pinned CLI and image revisions are distinct; their code does not prove the deployed image or platform verification algorithm. Prior evidence and procedure status remain unchanged.

**Responsible role:** Host Product/Engineering owner

**Next:** Ask the Host Product/Engineering owner to state the instruction-set requirement separately for x 86_64 and ARM64, and update the public Setup/table consistently. Do not infer a platform exception from a successful ARM64 image build or remove the rule using a host test alone.

## [First 24 Hours After Install](http://127.0.0.1:4000/host/first-24-hours)

### [Test Like A Client](http://127.0.0.1:4000/host/first-24-hours#test-like-a-client) — `MCL-1ebb3e6e2b370757`

**Status:** BLOCKED

**Literal source text:** - Jupyter opens.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** [CONNECTION-MCL-1ebb3e6e2b370757-01](current-host-connection-adjudications.json) — Exact browser session only. Scoped Python TLS is not browser trust; no Jupyter UI render, kernel execution, independent WAN proof, or product failure is established.; [JUPYTER_HTTP](evidence/2026-09-09-host-ssh-jupyter-selftest-attempt-01/jupyter-browser-open-01.json) — Exact browser session only. Scoped Python TLS is not browser trust; no Jupyter UI render, kernel execution, independent WAN proof, or product failure is established.; [JUPYTER_HTTPS](evidence/2026-09-09-host-ssh-jupyter-selftest-attempt-01/jupyter-browser-open-02.json) — Exact browser session only. Scoped Python TLS is not browser trust; no Jupyter UI render, kernel execution, independent WAN proof, or product failure is established.; [JUPYTER_CERTIFICATE](evidence/2026-09-09-host-ssh-jupyter-selftest-attempt-01/jupyter-certificate-snapshot-01.json) — Exact browser session only. Scoped Python TLS is not browser trust; no Jupyter UI render, kernel execution, independent WAN proof, or product failure is established.; [JUPYTER_SCOPED_TLS](evidence/2026-09-09-host-ssh-jupyter-selftest-attempt-01/jupyter-scoped-tls-01.json) — Exact browser session only. Scoped Python TLS is not browser trust; no Jupyter UI render, kernel execution, independent WAN proof, or product failure is established.

**Responsible role:** Authorized client/browser/network operator

**Next:** With explicit approval, establish trust for the official Vast CA only in the bounded browser context, then repeat authenticated browser navigation and UI rendering. Do not classify this environmental trust prerequisite as a product failure.

## [Reliability & Uptime](http://127.0.0.1:4000/host/reliability-uptime)

### [Why does reliability drop after rentals, reboots, or disconnects?](http://127.0.0.1:4000/host/reliability-uptime#why-does-reliability-drop-after-rentals-reboots-or-disconnects) — `MCL-22723a8aa7a0b7ca`

**Status:** UNVALIDATED

**Literal source text:** Reliability can drop when the platform observes instability, failed starts, disconnections, downtime, network failures, driver or GPU failures, thermal or power events, or active rental disruption. Short rentals can expose startup and runtime failures quickly. Reboots or disconnects during active commitments can hurt reliability.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-22723a8aa7a0b7ca and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Why does reliability drop after rentals, reboots, or disconnects?](http://127.0.0.1:4000/host/reliability-uptime#why-does-reliability-drop-after-rentals-reboots-or-disconnects) — `MCL-d5249da7f6f88a3e`

**Status:** UNVALIDATED

**Literal source text:** If you must take the machine offline, minimize the offline time. The score also takes the machine's average earnings into account: machines with lower earnings are penalized less for offline time.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Documentation technical-source reviewer

**Next:** Locate the exact canonical implementation/schema/configuration for this behavior and reuse applicable retained source/execution/UI evidence. Client dispatch or documentation alone cannot prove backend effects.

### [How quickly does reliability recover?](http://127.0.0.1:4000/host/reliability-uptime#how-quickly-does-reliability-recover) — `MCL-e03dd5c5f68b4bcf`

**Status:** UNVALIDATED

**Literal source text:** Reliability recovery depends on sustained stable operation and the machine's recent incident history. Some error messages can clear after the underlying issue is resolved, but reliability score recovery should not be treated as an instant reset. Keep the machine stable and error-free, then monitor the score over time.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host installer and operations engineering owner; Authorized Host/API operator

**Next:** The Host installer and operations engineering owner supplies the exact repository, revision, path, and symbol/operation locator; bind it to MCL-e03dd5c5f68b4bcf and retain the focused source check. An authorized Host/API operator runs only an approved representative check for MCL-e03dd5c5f68b4bcf and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [What should I do when reliability is at or below 0.9?](http://127.0.0.1:4000/host/reliability-uptime#what-should-i-do-when-reliability-is-at-or-below-0-9) — `MCL-33898e3231bb3364`

**Status:** UNVALIDATED

**Literal source text:** Reliability greater than 0.9 is a self-test and verification gate. If the machine is at or below the threshold, the normal self-test can fail before renting the temporary instance and the machine will not enter the verification pool. Keep the machine stable, resolve recent hardware, network, driver, daemon, thermal, power, or rental-disruption issues, then retry once the score recovers.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host installer and operations engineering owner; Authorized Host/API operator

**Next:** The Host installer and operations engineering owner supplies the exact repository, revision, path, and symbol/operation locator; bind it to MCL-33898e3231bb3364 and retain the focused source check. An authorized Host/API operator runs only an approved representative check for MCL-33898e3231bb3364 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [What should I do when reliability is at or below 0.9?](http://127.0.0.1:4000/host/reliability-uptime#what-should-i-do-when-reliability-is-at-or-below-0-9) — `MCL-1fdf3f5df77ef7d8`

**Status:** UNVALIDATED

**Literal source text:** Do not use `--ignore-requirements` as a verification shortcut. It is only useful for advanced runtime validation, and the machine still needs enough direct ports for the runtime test to work.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-1fdf3f5df77ef7d8 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Preventing score drops](http://127.0.0.1:4000/host/reliability-uptime#preventing-score-drops) — `MCL-5fe6dd91d4b0a5c2`

**Status:** UNVALIDATED

**Literal source text:** - Keep thermals, power delivery, and network stability healthy under sustained load.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-5fe6dd91d4b0a5c2 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

## [Maintenance Windows](http://127.0.0.1:4000/host/maintenance-windows)

### [Before Maintenance](http://127.0.0.1:4000/host/maintenance-windows#before-maintenance) — `MCL-7fbdf0de1f80b419`

**Status:** UNVALIDATED

**Literal source text:** Check the machine before you change its listing state:

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-7fbdf0de1f80b419 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Schedule An Unplanned Window](http://127.0.0.1:4000/host/maintenance-windows#schedule-an-unplanned-window) — `MCL-68587b2f7067d91a`

**Status:** UNVALIDATED

**Literal source text:** <Frame caption="Machine maintenance form with start time, duration, and reason fields.">

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-68587b2f7067d91a and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Schedule An Unplanned Window](http://127.0.0.1:4000/host/maintenance-windows#schedule-an-unplanned-window) — `MCL-00431aaac5977008`

**Status:** UNVALIDATED

**Literal source text:** If you must take the machine down unexpectedly, schedule a maintenance window so clients are notified and can save their work. The start date is Unix epoch seconds in UTC, and the duration is in hours.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-00431aaac5977008 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Schedule An Unplanned Window](http://127.0.0.1:4000/host/maintenance-windows#schedule-an-unplanned-window) — `MCL-e77d46d33f06a175`

**Status:** UNVALIDATED

**Literal source text:** <Frame caption="Maintenance reason options available in the machine maintenance form.">

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-e77d46d33f06a175 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Check Or Cancel Maintenance](http://127.0.0.1:4000/host/maintenance-windows#check-or-cancel-maintenance) — `MCL-6141b9411a225436`

**Status:** UNVALIDATED

**Literal source text:** Cancel scheduled maintenance for a machine:

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-6141b9411a225436 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Should I disable automatic updates?](http://127.0.0.1:4000/host/maintenance-windows#should-i-disable-automatic-updates) — `MCL-e2e25df310050c8c`

**Status:** UNVALIDATED

**Literal source text:** Avoid unattended kernel or GPU driver changes during active rentals. Driver and kernel updates can break running jobs or leave the host in a driver/library mismatch state until rebooted. Plan updates during maintenance windows, then verify `nvidia-smi`, Docker GPU access, and self-test behavior before accepting new rentals.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-e2e25df310050c8c and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

## [Disable SSH Password Login](http://127.0.0.1:4000/host/disable-ssh-password-login)

### [Introduction](http://127.0.0.1:4000/host/disable-ssh-password-login) — `CUR-3ded5aa3299dacd9`

**Status:** UNVALIDATED

**Literal source text:** Turn off SSH password login to protect your machine. A machine with it enabled will not pass verification.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Documentation technical-source reviewer

**Next:** Inspect verification scheduler/gate/configuration and exact self-test versus backend checks. Reuse compatible observations and keep any unsupported timeline/guarantee statement unresolved.

### [1. Check the current setting](http://127.0.0.1:4000/host/disable-ssh-password-login#1-check-the-current-setting) — `CUR-56b269be0ac552e6`

**Status:** UNVALIDATED

**Literal source text:** A fresh Ubuntu install says `yes`. Ubuntu ships the setting commented out, and sshd enables password login when the setting is absent.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host implementation source owner

**Next:** Bind an exact canonical source, authorized runtime observation, or accountable-owner decision before changing status.

### [2. Add your key and confirm it works](http://127.0.0.1:4000/host/disable-ssh-password-login#2-add-your-key-and-confirm-it-works) — `CUR-70d86d46ce67494a`

**Status:** UNVALIDATED

**Literal source text:** From your own computer. Replace `youruser` with your login name on the machine and `1.2.3.4` with its IP address, here and in every command below.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host implementation source owner

**Next:** Bind an exact canonical source, authorized runtime observation, or accountable-owner decision before changing status.

### [2. Add your key and confirm it works](http://127.0.0.1:4000/host/disable-ssh-password-login#2-add-your-key-and-confirm-it-works) — `CUR-0384df43f8e6b914`

**Status:** UNVALIDATED

**Literal source text:** Now open a second terminal, leaving the first one connected, and log in using only your key. This proves the key is what is getting you in.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Documentation technical-source reviewer; authorized operator for a required observed result

**Next:** Check the implementation and any retained result that covers this exact behavior. For an asserted timing, state change or completed outcome, identify the smallest authorized runtime/UI check and retain its result. Do not rent or mutate merely to establish a declared interface.

### [2. Add your key and confirm it works](http://127.0.0.1:4000/host/disable-ssh-password-login#2-add-your-key-and-confirm-it-works) — `CUR-fff81b607ab85103`

**Status:** UNVALIDATED

**Literal source text:** You should get a shell prompt with no password asked.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Documentation technical-source reviewer; authorized operator for a required observed result

**Next:** Check the implementation and any retained result that covers this exact behavior. For an asserted timing, state change or completed outcome, identify the smallest authorized runtime/UI check and retain its result. Do not rent or mutate merely to establish a declared interface.

### [3. Turn off password login](http://127.0.0.1:4000/host/disable-ssh-password-login#3-turn-off-password-login) — `CUR-8644fba884bb187b`

**Status:** UNVALIDATED

**Literal source text:** Do not run this until step 2 worked. If your key is not accepted yet, this locks you out.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host implementation source owner

**Next:** Bind an exact canonical source, authorized runtime observation, or accountable-owner decision before changing status.

### [3. Turn off password login](http://127.0.0.1:4000/host/disable-ssh-password-login#3-turn-off-password-login) — `CUR-fc13bfb88987a85b`

**Status:** UNVALIDATED

**Literal source text:** First save a copy of the config you have now. `cp -n` never overwrites, so it is safe to run this more than once.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host implementation source owner

**Next:** Bind an exact canonical source, authorized runtime observation, or accountable-owner decision before changing status.

### [If you are locked out](http://127.0.0.1:4000/host/disable-ssh-password-login#if-you-are-locked-out) — `CUR-16ea1e3b642162dd`

**Status:** UNVALIDATED

**Literal source text:** You need access that does not go through SSH. Use the machine's IPMI, iDRAC, iLO, or other BMC console, or plug a monitor and keyboard into it. Then put back every copy you saved in step 3, and restart:

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host implementation source owner

**Next:** Bind an exact canonical source, authorized runtime observation, or accountable-owner decision before changing status.

### [If you are locked out](http://127.0.0.1:4000/host/disable-ssh-password-login#if-you-are-locked-out) — `CUR-b235ee5806d25707`

**Status:** UNVALIDATED

**Literal source text:** Log in with your password, fix your key, and start again at step 2. Password login has to go back off before the machine will verify.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host implementation source owner

**Next:** Bind an exact canonical source, authorized runtime observation, or accountable-owner decision before changing status.

## [Removing or Recreating Machines](http://127.0.0.1:4000/host/removing-recreating-machines)

### [What changes when I swap GPUs or other hardware?](http://127.0.0.1:4000/host/removing-recreating-machines#what-changes-when-i-swap-gpus-or-other-hardware) — `MCL-02397010364a9a76`

**Status:** UNVALIDATED

**Literal source text:** Hardware changes can affect verification, search visibility, offers, and client expectations. Reducing GPU count, RAM, disk, or advertised capacity can trigger deverification or contract problems. Adding or replacing GPUs may require the host daemon or backend to refresh machine specs, and you may need to rerun self-test. The same-GPU-type guideline still applies; see [Supported Hardware](/host/supported-hardware).

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Documentation technical-source reviewer

**Next:** Record the engineering rationale, inspect relevant canonical technical behavior, and reuse applicable retained observations. Split guidance from any actual obligation or effect when their methods differ.

### [Uninstalling the host software](http://127.0.0.1:4000/host/removing-recreating-machines#uninstalling-the-host-software) — `MCL-fe93aa337bb543bf`

**Status:** UNVALIDATED

**Literal source text:** To uninstall, use the Vast uninstall script located at [https://s3.amazonaws.com/vast.ai/uninstall](https://s3.amazonaws.com/vast.ai/uninstall). Make sure active rental contracts have ended and the machine is unlisted first.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Documentation technical-source reviewer

**Next:** Record the engineering rationale, inspect relevant canonical technical behavior, and reuse applicable retained observations. Split guidance from any actual obligation or effect when their methods differ.

### [What should I do with a ghost machine?](http://127.0.0.1:4000/host/removing-recreating-machines#what-should-i-do-with-a-ghost-machine) — `MCL-df3998d5872da302`

**Status:** UNVALIDATED

**Literal source text:** First inspect whether the machine has active contracts, stored instances or volumes, visible offers, or backend state preventing deletion. Use the normal unlist/delete/cleanup path only when safe. If a stale backend record remains after normal cleanup, collect the account context, screenshots or CLI output, and relevant logs, then contact Vast support.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Documentation technical-source reviewer

**Next:** Record the engineering rationale, inspect relevant canonical technical behavior, and reuse applicable retained observations. Split guidance from any actual obligation or effect when their methods differ.

## [Fleet Operations](http://127.0.0.1:4000/host/fleet-operations)

### [Introduction](http://127.0.0.1:4000/host/fleet-operations) — `MCL-e962f57e828074a7`

**Status:** UNVALIDATED

**Literal source text:** If multiple people manage the fleet, run the machines under the intended team context and assign machine permissions deliberately. See [Host Teams](/host/host-teams).

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-e962f57e828074a7 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Bulk Listing And Pricing](http://127.0.0.1:4000/host/fleet-operations#bulk-listing-and-pricing) — `MCL-a2da03ac5606f76d`

**Status:** UNVALIDATED

**Literal source text:** Apply listing changes to selected machines:

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Documentation technical-source reviewer

**Next:** Record the engineering rationale, inspect relevant canonical technical behavior, and reuse applicable retained observations. Split guidance from any actual obligation or effect when their methods differ.

### [Maintenance Windows](http://127.0.0.1:4000/host/fleet-operations#maintenance-windows) — `MCL-7118c859b1c62f5d`

**Status:** UNVALIDATED

**Literal source text:** `--sdate` is Unix epoch seconds UTC. Categories are `power`, `internet`, `disk`, `gpu`, `software`, or `other`. See [Maintenance Windows](/host/maintenance-windows).

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-7118c859b1c62f5d and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Default Jobs](http://127.0.0.1:4000/host/fleet-operations#default-jobs) — `MCL-f16d11e0b0e9e16a`

**Status:** UNVALIDATED

**Literal source text:** Run your own container when a machine is idle:

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-f16d11e0b0e9e16a and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Defragment GPUs](http://127.0.0.1:4000/host/fleet-operations#defragment-gpus) — `MCL-c0ec17dd86d47c87`

**Status:** UNVALIDATED

**Literal source text:** On multi-GPU machines, defragmentation can free larger GPU groups. Select and review the intended machine IDs first; do not expand `vastai show machines` inside this state-changing command.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host installer and operations engineering owner; Authorized Host/API operator

**Next:** The Host installer and operations engineering owner supplies the exact repository, revision, path, and symbol/operation locator; bind it to MCL-c0ec17dd86d47c87 and retain the focused source check. An authorized Host/API operator runs only an approved representative check for MCL-c0ec17dd86d47c87 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Monitor](http://127.0.0.1:4000/host/fleet-operations#monitor) — `MCL-c3e830af14448060`

**Status:** UNVALIDATED

**Literal source text:** 3. Inspect individual machines with [vastai show machine](/cli/reference/show-machine).

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host installer and operations engineering owner; Authorized Host/API operator

**Next:** The Host installer and operations engineering owner supplies the exact repository, revision, path, and symbol/operation locator; bind it to MCL-c3e830af14448060 and retain the focused source check. An authorized Host/API operator runs only an approved representative check for MCL-c3e830af14448060 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Cleanup And Decommissioning](http://127.0.0.1:4000/host/fleet-operations#cleanup-and-decommissioning) — `MCL-5035a12250932203`

**Status:** UNVALIDATED

**Literal source text:** To decommission, unlist first, honor remaining rental end dates, then delete. See [Remove or Recreate](/host/removing-recreating-machines).

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-5035a12250932203 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

## [Host Teams](http://127.0.0.1:4000/host/host-teams)

### [Earnings And Payouts](http://127.0.0.1:4000/host/host-teams#earnings-and-payouts) — `MCL-f426518c26948ea1`

**Status:** UNVALIDATED

**Literal source text:** Rental earnings from team-owned machines accrue to the team account, not to the individual operator who installed or managed the machine.

**Required proof:** Published Vendor Documentation, Canonical Implementation Source, Static Context Review, Accountable Owner Confirmation

**Existing proof / limit:** [TEAMS-CONSOLE-MCL-f426518c26948ea1-1](evidence/2026-09-15-host-continuation-88-attempt-01/c-teams-source/guides-excerpts.json) — No account balances, rental settlement or payout destination were observed. Do not infer a Host-specific financial allocation rule solely from separate team accounts.; [TEAMS-CONSOLE-MCL-f426518c26948ea1-2](evidence/2026-09-15-host-continuation-teams-account-attempt-01/source-excerpts.json) — No account balances, rental settlement or payout destination were observed. Do not infer a Host-specific financial allocation rule solely from separate team accounts.; [TEAMS-CONSOLE-MCL-f426518c26948ea1-3](evidence/2026-09-15-host-continuation-teams-account-attempt-01/context-review.json) — No account balances, rental settlement or payout destination were observed. Do not infer a Host-specific financial allocation rule solely from separate team accounts.; [RECOVERY-EARNINGS-MCL-f426518c26948ea1-1](evidence/2026-09-15-host-continuation-earnings-ui-attempt-01/source-excerpts-03.json) — No payout, export, account mutation or settlement was performed. Frontend source supports displayed controls and declared calculations only; no backend financial/account ownership or team-permission guarantee is inferred. Existing procedure status and historical attempts remain unchanged.

**Responsible role:** Host finance or Teams product owner

**Next:** Confirm whether rental earnings for team-owned machines accrue only to the team account rather than an individual installer/operator.

### [Earnings And Payouts](http://127.0.0.1:4000/host/host-teams#earnings-and-payouts) — `MCL-350d25401b2594d2`

**Status:** UNVALIDATED

**Literal source text:** Earnings and payout visibility is role-gated:

**Required proof:** Published Vendor Documentation, Static Context Review, Accountable Owner Confirmation

**Existing proof / limit:** [TEAMS-CONSOLE-MCL-350d25401b2594d2-1](evidence/2026-09-15-host-continuation-88-attempt-01/c-teams-source/guides-excerpts.json) — Published billing_read coverage for earnings/invoices does not establish the separate payout-history surface or role mapping.; [TEAMS-CONSOLE-MCL-350d25401b2594d2-2](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/a-policy-account/published-current.json) — Published billing_read coverage for earnings/invoices does not establish the separate payout-history surface or role mapping.; [TEAMS-CONSOLE-MCL-350d25401b2594d2-4](evidence/2026-09-15-host-continuation-teams-account-attempt-01/context-review.json) — Published billing_read coverage for earnings/invoices does not establish the separate payout-history surface or role mapping.; [RECOVERY-EARNINGS-MCL-350d25401b2594d2-1](evidence/2026-09-15-host-continuation-earnings-ui-attempt-01/source-excerpts-03.json) — No payout, export, account mutation or settlement was performed. Frontend source supports displayed controls and declared calculations only; no backend financial/account ownership or team-permission guarantee is inferred. Existing procedure status and historical attempts remain unchanged.

**Responsible role:** Teams permissions product owner

**Next:** Provide the current permission/role matrix for team Earnings and Payout visibility, including custom roles.

### [Earnings And Payouts](http://127.0.0.1:4000/host/host-teams#earnings-and-payouts) — `MCL-ff0e592ec9d37394`

**Status:** UNVALIDATED

**Literal source text:** | Owner or billing administrator | Configure the team payout account. |

**Required proof:** Published Vendor Documentation, Static Context Review, Accountable Owner Confirmation

**Existing proof / limit:** [TEAMS-CONSOLE-MCL-ff0e592ec9d37394-1](evidence/2026-09-15-host-continuation-88-attempt-01/c-teams-source/guides-excerpts.json) — No payout settings were opened or changed by this lane. Manager/owner UI differences from other teams cannot isolate the payout permission rule.; [TEAMS-CONSOLE-MCL-ff0e592ec9d37394-2](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/a-policy-account/published-current.json) — No payout settings were opened or changed by this lane. Manager/owner UI differences from other teams cannot isolate the payout permission rule.; [TEAMS-CONSOLE-MCL-ff0e592ec9d37394-3](evidence/2026-09-15-host-continuation-teams-account-attempt-01/context-review.json) — No payout settings were opened or changed by this lane. Manager/owner UI differences from other teams cannot isolate the payout permission rule.; [RECOVERY-EARNINGS-MCL-ff0e592ec9d37394-1](evidence/2026-09-15-host-continuation-earnings-ui-attempt-01/source-excerpts-03.json) — No payout, export, account mutation or settlement was performed. Frontend source supports displayed controls and declared calculations only; no backend financial/account ownership or team-permission guarantee is inferred. Existing procedure status and historical attempts remain unchanged.

**Responsible role:** Teams permissions and Host payouts owner

**Next:** Confirm which current team permissions allow configuring payout accounts; clarify whether owner or billing administrator are applicable role names.

### [Earnings And Payouts](http://127.0.0.1:4000/host/host-teams#earnings-and-payouts) — `MCL-fe79b15ff39543a3`

**Status:** UNVALIDATED

**Literal source text:** The payout account is configured on the team account. Individual members do not receive separate payouts for team-owned machine rentals.

**Required proof:** Published Vendor Documentation, Static Context Review, Accountable Owner Confirmation

**Existing proof / limit:** [TEAMS-CONSOLE-MCL-fe79b15ff39543a3-1](evidence/2026-09-15-host-continuation-88-attempt-01/c-teams-source/guides-excerpts.json) — No settlement, bank/provider destination or member payout behavior was observed. This is a substantive source gap, not an unavailable-hardware blocker.; [TEAMS-CONSOLE-MCL-fe79b15ff39543a3-2](evidence/2026-09-15-host-continuation-teams-account-attempt-01/context-review.json) — No settlement, bank/provider destination or member payout behavior was observed. This is a substantive source gap, not an unavailable-hardware blocker.; [RECOVERY-EARNINGS-MCL-fe79b15ff39543a3-1](evidence/2026-09-15-host-continuation-earnings-ui-attempt-01/source-excerpts-03.json) — No payout, export, account mutation or settlement was performed. Frontend source supports displayed controls and declared calculations only; no backend financial/account ownership or team-permission guarantee is inferred. Existing procedure status and historical attempts remain unchanged.

**Responsible role:** Host finance or Teams product owner

**Next:** Confirm team payout-account ownership and whether member-specific payouts or splits exist for team-owned machine rentals.

## [Host Diagnostics](http://127.0.0.1:4000/host/common-errors-diagnostics)

### [Logs And Support Bundles](http://127.0.0.1:4000/host/common-errors-diagnostics#logs-and-support-bundles) — `MCL-3aca6b1f291d4d0c`

**Status:** BLOCKED

**Literal source text:** ```bash vastai self-test machine <machine_id> \   --support-bundle-dir /path/to/output ```

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** [EV-HOST-CLOSURE-MCL-3aca6b1f291d4d0c-1](evidence/2026-09-09-host-ssh-jupyter-selftest-attempt-01/selftest-normal-preflight-01.json) — Normal support-bundle CLI command reached requirements, success=false; offer reliability0.8506588 and upload221.1Mb/s failed >0.90/500 thresholds; mode0600 failure archive with four hashed members. Advertised values at that time, not present state/new bandwidth measurement. No create request, diagnostic image, runtime result, remote workload logs or settled billing; raw exit0 is not success.; [EV-HOST-SELF-TEST-01](evidence/2026-09-02-host-self-test-attempt-01/result.md) — Static or partial evidence does not establish the prohibited or unavailable runtime behavior.; [ADA-01](evidence/2026-09-08-host-ada-readiness-attempt-01/api-01.json) — Read-only candidate access/metadata snapshot only; it is not authorization, reservation, workload execution, health, or cleanup proof.

**Responsible role:** Backend and Host-daemon source owner; Authorized Host/API operator

**Next:** For the remaining official diagnostic workload, use a currently suitable authorized machine and bounded window; reconfirm occupancy and cleanup scope. Retain the exact diagnostic result, not only preflight.

### [GPU And Kernel Diagnostics](http://127.0.0.1:4000/host/common-errors-diagnostics#gpu-and-kernel-diagnostics) — `MCL-037cb23e40e39e59`

**Status:** BLOCKED

**Literal source text:** ```bash sudo docker run --rm --runtime=nvidia oguzpastirmaci/gpu-burn 60 ```

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** [EV-DIA-E03-GPU-BURN-MANIFEST-01](evidence/2026-09-01-host-gpu-burn-manifest-attempt-01/result.md) — Static or partial evidence does not establish the prohibited or unavailable runtime behavior.

**Responsible role:** Authorized Host/API operator

**Next:** Under explicit authorization, provide this prerequisite for CLM-1112ca628ad4639f: An authorized idle workload-capable Host and explicit approval to run GPU burn are unavailable under this task scope. Then retain the exact observation and cleanup.

## [Host Payouts](http://127.0.0.1:4000/host/payment)

### [Introduction](http://127.0.0.1:4000/host/payment) — `MCL-b5b2716c025774a3`

**Status:** UNVALIDATED

**Literal source text:** For team-owned host machines, earnings and payout settings belong to the team account. See [Host Teams](/host/host-teams#earnings-and-payouts).

**Required proof:** Canonical Implementation Source, Product Publication Source, Accountable Owner Confirmation

**Existing proof / limit:** [RECOVERY-EARNINGS-MCL-b5b2716c025774a3-1](evidence/2026-09-15-host-continuation-earnings-ui-attempt-01/source-excerpts-03.json) — No payout, export, account mutation or settlement was performed. Frontend source supports displayed controls and declared calculations only; no backend financial/account ownership or team-permission guarantee is inferred. Existing procedure status and historical attempts remain unchanged.

**Responsible role:** Host finance or Teams product owner

**Next:** Confirm ownership of earnings and payout settings for team-owned machines and how account context applies.

## [Workload Policy](http://127.0.0.1:4000/host/workload-policy)

### [Host Responsibilities](http://127.0.0.1:4000/host/workload-policy#host-responsibilities) — `MCL-d2898c17f7c44453`

**Status:** UNVALIDATED

**Literal source text:** An idle-looking rental can still be active. Renters may run notebooks, services, build jobs, CPU-heavy work, or bursty workloads.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Documentation technical-source reviewer

**Next:** Locate the exact canonical implementation/schema/configuration for this behavior and reuse applicable retained source/execution/UI evidence. Client dispatch or documentation alone cannot prove backend effects.

### [Can I Message A Client?](http://127.0.0.1:4000/host/workload-policy#can-i-message-a-client) — `MCL-3e1e416bd8472c73`

**Status:** UNVALIDATED

**Literal source text:** No. Hosts do not have an established direct client-message flow. If a workload looks broken, idle, abusive, or policy-sensitive, follow the escalation guidance below.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Documentation technical-source reviewer

**Next:** Locate the exact canonical implementation/schema/configuration for this behavior and reuse applicable retained source/execution/UI evidence. Client dispatch or documentation alone cannot prove backend effects.

### [Renter Reports And Host Logs](http://127.0.0.1:4000/host/workload-policy#renter-reports-and-host-logs) — `MCL-fb62978710afd9ae`

**Status:** UNVALIDATED

**Literal source text:** Renters can report machine issues from their instance using **Report Machine**. Report categories include startup failures, slow instance load, less disk space than requested, port issues, lower-than-expected performance, and other issues. The report can also include a written description from the renter.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-fb62978710afd9ae and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Renter Reports And Host Logs](http://127.0.0.1:4000/host/workload-policy#renter-reports-and-host-logs) — `MCL-d5fea2f21fcfad56`

**Status:** UNVALIDATED

**Literal source text:** <Frame caption="Report Machine issue categories">

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-d5fea2f21fcfad56 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Renter Reports And Host Logs](http://127.0.0.1:4000/host/workload-policy#renter-reports-and-host-logs) — `MCL-e9a34cb581243524`

**Status:** UNVALIDATED

**Literal source text:** <Frame caption="Report Machine detail field">

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Product and Legal policy owner; Authorized Host/API operator

**Next:** The Product and Legal policy owner supplies the exact repository, revision, path, and symbol/operation locator; bind it to MCL-e9a34cb581243524 and retain the focused source check. An authorized Host/API operator runs only an approved representative check for MCL-e9a34cb581243524 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Renter Reports And Host Logs](http://127.0.0.1:4000/host/workload-policy#renter-reports-and-host-logs) — `MCL-1c462c12bc152d84`

**Status:** UNVALIDATED

**Literal source text:** - Pull daemon-side instance logs with [`vastai logs <instance_id> --daemon-logs`](/cli/reference/logs) when you have the affected instance ID.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Product and Legal policy owner; Authorized Host/API operator

**Next:** The Product and Legal policy owner supplies the exact repository, revision, path, and symbol/operation locator; bind it to MCL-1c462c12bc152d84 and retain the focused source check. An authorized Host/API operator runs only an approved representative check for MCL-1c462c12bc152d84 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Renter Reports And Host Logs](http://127.0.0.1:4000/host/workload-policy#renter-reports-and-host-logs) — `MCL-9cc77fee7767140d`

**Status:** UNVALIDATED

**Literal source text:** - Check kernel GPU, PCIe, AER, and Xid logs for hardware or driver symptoms.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-9cc77fee7767140d and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Renter Reports And Host Logs](http://127.0.0.1:4000/host/workload-policy#renter-reports-and-host-logs) — `MCL-423f3130db7b0aa7`

**Status:** UNVALIDATED

**Literal source text:** - Compare the report with the machine's listing, port range, storage setup, recent maintenance, and any active contract terms.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Documentation technical-source reviewer

**Next:** Record the engineering rationale, inspect relevant canonical technical behavior, and reuse applicable retained observations. Split guidance from any actual obligation or effect when their methods differ.

### [What To Do](http://127.0.0.1:4000/host/workload-policy#what-to-do) — `MCL-c9b78dc9fc910dff`

**Status:** UNVALIDATED

**Literal source text:** | Renter reports a machine issue | Review user reports, collect host-side logs, and compare the report with listing, storage, ports, performance, and recent maintenance. |

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-c9b78dc9fc910dff and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [What To Do](http://127.0.0.1:4000/host/workload-policy#what-to-do) — `MCL-4f5c171b6c5356dc`

**Status:** UNVALIDATED

**Literal source text:** | Rental affects machine stability | Check host hardware, thermals, power, drivers, Docker, daemon logs, and kernel GPU/PCIe logs. |

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Product and Legal policy owner; Authorized Host/API operator

**Next:** The Product and Legal policy owner supplies the exact repository, revision, path, and symbol/operation locator; bind it to MCL-4f5c171b6c5356dc and retain the focused source check. An authorized Host/API operator runs only an approved representative check for MCL-4f5c171b6c5356dc and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [What To Do](http://127.0.0.1:4000/host/workload-policy#what-to-do) — `MCL-ea917dd3feed8209`

**Status:** UNVALIDATED

**Literal source text:** | Suspected abuse | Collect timestamps, symptoms, screenshots, and visible instance details; contact support. |

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-ea917dd3feed8209 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

## [Hosting Agreement](http://127.0.0.1:4000/host/hosting-agreement)

### [Where to find and accept it](http://127.0.0.1:4000/host/hosting-agreement#where-to-find-and-accept-it) — `MCL-0eeef126e388e068`

**Status:** UNVALIDATED

**Literal source text:** | Acceptance flow | Linked from the first paragraph of the [host setup guide](https://cloud.vast.ai/host/setup/) during account conversion — see [Account & Hosting Agreement](/host/account-hosting-agreement) |

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Documentation technical-source reviewer

**Next:** Inspect canonical account/team/auth/invoice/payout configuration and applicable retained console or API observation for the exact transition. Existing general docs are navigation to sources, not terminal proof.

## [Discord & Community](http://127.0.0.1:4000/host/community)

### [Introduction](http://127.0.0.1:4000/host/community) — `MCL-c6ebcea88a54fe64`

**Status:** UNVALIDATED

**Literal source text:** Use community channels for host discussion, peer help, and machine-specific setup questions.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-c6ebcea88a54fe64 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Joining the host Discord channels](http://127.0.0.1:4000/host/community#joining-the-host-discord-channels) — `MCL-ea942f347579d4b4`

**Status:** UNVALIDATED

**Literal source text:** Join [Discord](https://discord.gg/hSuEbSQ4X8), then connect your Vast host account to unlock the **host-only channels**.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-ea942f347579d4b4 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [What to include when asking for help](http://127.0.0.1:4000/host/community#what-to-include-when-asking-for-help) — `MCL-48ab2d6eb2bb085f`

**Status:** UNVALIDATED

**Literal source text:** - The exact error string or symptom shown in the console, CLI, or self-test output.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host Product and Documentation content owner; Authorized Host/API operator

**Next:** The Host Product and Documentation content owner supplies the exact repository, revision, path, and symbol/operation locator; bind it to MCL-48ab2d6eb2bb085f and retain the focused source check. An authorized Host/API operator runs only an approved representative check for MCL-48ab2d6eb2bb085f and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [What to include when asking for help](http://127.0.0.1:4000/host/community#what-to-include-when-asking-for-help) — `MCL-14bbb819dce26701`

**Status:** UNVALIDATED

**Literal source text:** - Machine ID and host context when safe to share in the channel.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-14bbb819dce26701 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [What to include when asking for help](http://127.0.0.1:4000/host/community#what-to-include-when-asking-for-help) — `MCL-132dbf35d8056c28`

**Status:** UNVALIDATED

**Literal source text:** - For network problems, the tested external IP:port the CLI reported.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host Product and Documentation content owner; Authorized Host/API operator

**Next:** The Host Product and Documentation content owner supplies the exact repository, revision, path, and symbol/operation locator; bind it to MCL-132dbf35d8056c28 and retain the focused source check. An authorized Host/API operator runs only an approved representative check for MCL-132dbf35d8056c28 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [What to expect](http://127.0.0.1:4000/host/community#what-to-expect) — `MCL-9baa8e943abc39f0`

**Status:** UNVALIDATED

**Literal source text:** Community help is peer support from other hosts. Vast staff may read along, but there is no response-time guarantee. For account state, payouts, backend machine records, and other platform-side issues, [escalate to support](/host/common-errors-diagnostics#escalate-support).

**Required proof:** Authoritative Documentation Citation, Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Documentation authoritative-source reviewer

**Next:** Inspect the retained Performance of Services or applicable official support/account publication first; inspect implementation and retained UI for any actual account, networking, or support capability assertion.
