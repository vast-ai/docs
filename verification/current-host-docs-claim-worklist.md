# Current Host Docs claim worklist

Current-source claims requiring proof or correction. Historical evidence is carried only where exact source identity is recorded.

Current dispositions: 2008 occurrences (1624 PASS, 94 editorial NOT_APPLICABLE, 290 requiring review or evidence). Most dispositions are automated or exact historical carry-forward; this package records no invented manual completion.

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

## [Is Vast for Me?](http://127.0.0.1:4000/host/persona-decision-guide)

### [Introduction](http://127.0.0.1:4000/host/persona-decision-guide) — `MCL-f083550c42fc86c8`

**Status:** UNVALIDATED

**Literal source text:** Vast is a GPU marketplace, not a managed setup service. Hosts operate their own hardware, OS, drivers, storage, networking, pricing, uptime, and maintenance.

**Required proof:** Authoritative Documentation Citation, Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Documentation authoritative-source reviewer

**Next:** Inspect the retained Performance of Services or applicable official support/account publication first; inspect implementation and retained UI for any actual account, networking, or support capability assertion.

### [Good Fit](http://127.0.0.1:4000/host/persona-decision-guide#good-fit) — `MCL-790e88587331e783`

**Status:** UNVALIDATED

**Literal source text:** - The host can run native Ubuntu/Linux.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-790e88587331e783 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Wait Or Reconsider](http://127.0.0.1:4000/host/persona-decision-guide#wait-or-reconsider) — `MCL-a568f51323f7bb7b`

**Status:** UNVALIDATED

**Literal source text:** | Mixed, old, or low-VRAM GPUs | Can fail checks or attract little demand. |

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-a568f51323f7bb7b and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Wait Or Reconsider](http://127.0.0.1:4000/host/persona-decision-guide#wait-or-reconsider) — `MCL-853d9d5e70a408f1`

**Status:** UNVALIDATED

**Literal source text:** | Expecting guaranteed verification or earnings | Eligibility does not guarantee search placement, rentals, or revenue. |

**Required proof:** Authoritative Documentation Citation, Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Documentation authoritative-source reviewer

**Next:** Inspect the current official datacenter application/program publication or verification requirements as applicable, then applicable configuration/enforcement and retained UI. Do not use a generic marketing page to prove a specific threshold.

### [Wait Or Reconsider](http://127.0.0.1:4000/host/persona-decision-guide#wait-or-reconsider) — `MCL-805284879080bb07`

**Status:** UNVALIDATED

**Literal source text:** | Daily gaming/workstation machine | Rented workloads need a stable dedicated host. |

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-805284879080bb07 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Choose Your Path](http://127.0.0.1:4000/host/persona-decision-guide#choose-your-path) — `MCL-bb2881170fb6d050`

**Status:** UNVALIDATED

**Literal source text:** | Linux-comfortable operator | [Hardware Prep](/host/hardware-prep), then [Install Host Software](/host/installing-host-software) |

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-bb2881170fb6d050 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Choose Your Path](http://127.0.0.1:4000/host/persona-decision-guide#choose-your-path) — `MCL-1b442dba638539f1`

**Status:** UNVALIDATED

**Literal source text:** | Headless/datacenter operator | [Headless Install](/host/headless-install) and [Fleet Operations](/host/fleet-operations) |

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-1b442dba638539f1 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Decision Checklist](http://127.0.0.1:4000/host/persona-decision-guide#decision-checklist) — `MCL-b75892e2e903169d`

**Status:** UNVALIDATED

**Literal source text:** - Hardware, CPU, RAM, PCIe, storage, and network match [Supported Hardware](/host/supported-hardware).

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-b75892e2e903169d and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Decision Checklist](http://127.0.0.1:4000/host/persona-decision-guide#decision-checklist) — `MCL-ece014e8a4de5632`

**Status:** UNVALIDATED

**Literal source text:** - The host can run native Ubuntu/Linux.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-ece014e8a4de5632 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Decision Checklist](http://127.0.0.1:4000/host/persona-decision-guide#decision-checklist) — `MCL-d1f6300817228049`

**Status:** UNVALIDATED

**Literal source text:** - You can keep the machine powered, cooled, stable, and online during rentals.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-d1f6300817228049 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

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

## [Storage Setup](http://127.0.0.1:4000/host/storage-setup)

### [Introduction](http://127.0.0.1:4000/host/storage-setup) — `MCL-13e3cc23c02bd0de`

**Status:** UNVALIDATED

**Literal source text:** Formatting a disk or LVM volume destroys data. Identify the OS disk and any provider data mount before running `mkfs`.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-13e3cc23c02bd0de and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Docker Storage Layout](http://127.0.0.1:4000/host/storage-setup#docker-storage-layout) — `MCL-94fa4408dc40a365`

**Status:** UNVALIDATED

**Literal source text:** Current listing guidance expects at least 128 GB of fast SSD storage per GPU. Docker storage should:

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-94fa4408dc40a365 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Docker Storage Layout](http://127.0.0.1:4000/host/storage-setup#docker-storage-layout) — `MCL-7928ad4ab732dd5e`

**Status:** UNVALIDATED

**Literal source text:** - Mount predictably at boot before Docker and the host daemon start.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host installer and operations engineering owner; Authorized Host/API operator

**Next:** The Host installer and operations engineering owner supplies the exact repository, revision, path, and symbol/operation locator; bind it to MCL-7928ad4ab732dd5e and retain the focused source check. An authorized Host/API operator runs only an approved representative check for MCL-7928ad4ab732dd5e and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Docker Storage Layout](http://127.0.0.1:4000/host/storage-setup#docker-storage-layout) — `MCL-d390fab4066502be`

**Status:** UNVALIDATED

**Literal source text:** - Have enough capacity for active rentals, stopped instances, cached images, and any volume offers.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-d390fab4066502be and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [XFS Project Quotas](http://127.0.0.1:4000/host/storage-setup#xfs-project-quotas) — `MCL-a8b24ed1c77188ae`

**Status:** UNVALIDATED

**Literal source text:** Add `pquota` or `prjquota` to the mount-options column for the `/var/lib/docker` XFS mount in `/etc/fstab`. In the example below, the mount-options column is `rw,auto,pquota,nofail`:

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-a8b24ed1c77188ae and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [XFS Project Quotas](http://127.0.0.1:4000/host/storage-setup#xfs-project-quotas) — `MCL-d540ae3801c031c2`

**Status:** UNVALIDATED

**Literal source text:** After editing `/etc/fstab`, mount and verify:

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-d540ae3801c031c2 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [XFS Project Quotas](http://127.0.0.1:4000/host/storage-setup#xfs-project-quotas) — `MCL-7a5577cd886c6773`

**Status:** UNVALIDATED

**Literal source text:** The mount should be XFS, include `pquota` or `prjquota`, and show project quota accounting/enforcement as ON.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-7a5577cd886c6773 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [XFS Project Quotas](http://127.0.0.1:4000/host/storage-setup#xfs-project-quotas) — `MCL-33e586fa772afcab`

**Status:** UNVALIDATED

**Literal source text:** Do not work around quota errors by removing Docker quota settings. Fix the filesystem and mount instead.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-33e586fa772afcab and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Disposable Device Example](http://127.0.0.1:4000/host/storage-setup#disposable-device-example) — `MCL-9d3a9f79513985b1`

**Status:** UNVALIDATED

**Literal source text:** ```bash export VAST_DOCKER_DEVICE=/dev/mapper/vg1-lv--1 lsblk -f "$VAST_DOCKER_DEVICE" findmnt -S "$VAST_DOCKER_DEVICE" || true if findmnt -S "$VAST_DOCKER_DEVICE" >/dev/null; then   sudo umount "$VAST_DOCKER_DEVICE" fi sudo mkfs.xfs -f "$VAST_DOCKER_DEVICE" sudo mkdir -p /var/lib/docker sudo blkid "$VAST_DOCKER_DEVICE" ```

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-9d3a9f79513985b1 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Disposable Device Example](http://127.0.0.1:4000/host/storage-setup#disposable-device-example) — `MCL-984d77eda277edf8`

**Status:** UNVALIDATED

**Literal source text:** Comment out any old `/data0` line for the same device, add the `/var/lib/docker` fstab line, then mount:

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-984d77eda277edf8 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Disposable Device Example](http://127.0.0.1:4000/host/storage-setup#disposable-device-example) — `MCL-9d63eb54604a21f2`

**Status:** UNVALIDATED

**Literal source text:** If you are starting from a raw disk, create a partition first. The [Headless Install Path](/host/headless-install) includes a `cfdisk` example.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-9d63eb54604a21f2 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Example fstab Line](http://127.0.0.1:4000/host/storage-setup#example-fstab-line) — `MCL-850c39d1d4307b70`

**Status:** UNVALIDATED

**Literal source text:** The mount should be XFS, include `pquota` or `prjquota`, and show project quota accounting/enforcement as ON.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-850c39d1d4307b70 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Docker pquota Error](http://127.0.0.1:4000/host/storage-setup#docker-pquota-error) — `MCL-fe4d33b75a767db5`

**Status:** UNVALIDATED

**Literal source text:** Move Docker's data root to a correctly mounted XFS filesystem, verify quotas, then restart Docker and the host software.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host installer and operations engineering owner; Authorized Host/API operator

**Next:** The Host installer and operations engineering owner supplies the exact repository, revision, path, and symbol/operation locator; bind it to MCL-fe4d33b75a767db5 and retain the focused source check. An authorized Host/API operator runs only an approved representative check for MCL-fe4d33b75a767db5 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Installer Connection](http://127.0.0.1:4000/host/storage-setup#installer-connection) — `MCL-218ac128caa872b6`

**Status:** UNVALIDATED

**Literal source text:** The Host Installer Wizard should detect prepared Docker storage. If you use the [headless fallback installer](/host/installing-host-software#headless-fallback), pass the block device behind the Docker mount:

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host installer and operations engineering owner; Authorized Host/API operator

**Next:** The Host installer and operations engineering owner supplies the exact repository, revision, path, and symbol/operation locator; bind it to MCL-218ac128caa872b6 and retain the focused source check. An authorized Host/API operator runs only an approved representative check for MCL-218ac128caa872b6 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Installer Connection](http://127.0.0.1:4000/host/storage-setup#installer-connection) — `MCL-4bdffb1f97655ab7`

**Status:** UNVALIDATED

**Literal source text:** ```bash sudo python3 ./install "$VAST_HOST_KEY" \   --no-driver \   --docker-partition /dev/mapper/vg1-lv--1 \   --ports 40000 40799 ```

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host installer and operations engineering owner; Authorized Host/API operator

**Next:** The Host installer and operations engineering owner supplies the exact repository, revision, path, and symbol/operation locator; bind it to MCL-4bdffb1f97655ab7 and retain the focused source check. An authorized Host/API operator runs only an approved representative check for MCL-4bdffb1f97655ab7 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Volume Offers And Cached Images](http://127.0.0.1:4000/host/storage-setup#volume-offers-and-cached-images) — `MCL-82c1fad30ffec299`

**Status:** UNVALIDATED

**Literal source text:** Rented volume space reduces storage available to GPU offers. Cached images can be reused when possible instead of redownloaded.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-82c1fad30ffec299 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Does Vast redownload images that were already used?](http://127.0.0.1:4000/host/storage-setup#does-vast-redownload-images-that-were-already-used) — `MCL-62d2ad8178f52aea`

**Status:** UNVALIDATED

**Literal source text:** Prior images are cached when possible. If a renter uses an image already present on the machine, the system can reuse it.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-62d2ad8178f52aea and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

## [Headless Hosting Guide](http://127.0.0.1:4000/host/headless-install)

### [Step 8: Configure GRUB Only When Needed](http://127.0.0.1:4000/host/headless-install#step-8-configure-grub-only-when-needed) — `MCL-673370399b8669d9`

**Status:** BLOCKED

**Literal source text:** ```bash sudo update-grub ```

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** [EV-HOST-COMMAND-OCCURRENCE-RECONCILIATION-01](evidence/2026-09-03-host-repository-rebase-01/result.md) — Static or partial evidence does not establish the prohibited or unavailable runtime behavior.

**Responsible role:** Authorized Host/API operator

**Next:** Under explicit authorization, provide this prerequisite for CLM-2872a25df6add3a5: Explicit operator authorization and a controlled disposable or idle Host are unavailable for changing the bootloader configuration. Then retain the exact observation and cleanup.

## [VMs & IOMMU](http://127.0.0.1:4000/host/vms)

### [Introduction](http://127.0.0.1:4000/host/vms) — `MCL-0bf59b7057f2d62a`

**Status:** UNVALIDATED

**Literal source text:** Vast can run KVM virtual machines in addition to Docker containers. VM support is optional and depends heavily on hardware, BIOS, kernel, and GPU configuration.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-0bf59b7057f2d62a and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Introduction](http://127.0.0.1:4000/host/vms) — `MCL-9ca15e77224c7a3d`

**Status:** UNVALIDATED

**Literal source text:** VMs interact more directly with hardware than containers. Enable them only when the machine supports IOMMU and remains stable.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-9ca15e77224c7a3d and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [When VM Support Helps](http://127.0.0.1:4000/host/vms#when-vm-support-helps) — `MCL-6b11a6264600fa57`

**Status:** UNVALIDATED

**Literal source text:** Single-GPU hosts usually have the lowest VM risk. Multi-GPU RTX 40-series hosts may also benefit. Multi-GPU datacenter hosts should be more cautious until VM P2P/NVLink behavior is a good fit for the workload.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-6b11a6264600fa57 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Tradeoffs](http://127.0.0.1:4000/host/vms#tradeoffs) — `MCL-6cb4c04ce10a0fe3`

**Status:** UNVALIDATED

**Literal source text:** - IOMMU settings can reduce PCIe peer-to-peer performance on some multi-GPU systems.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-6cb4c04ce10a0fe3 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Check VM Status](http://127.0.0.1:4000/host/vms#check-vm-status) — `MCL-654633f50eb39f25`

**Status:** UNVALIDATED

**Literal source text:** These values describe VM configuration state only. They do not confirm that the Host is idle or that a VM workload is healthy.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-654633f50eb39f25 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Disable VM Support](http://127.0.0.1:4000/host/vms#disable-vm-support) — `MCL-442f5fb5941fefd1`

**Status:** UNVALIDATED

**Literal source text:** Disabling VM support changes Host configuration and can disrupt running work. Prevent new rentals during the approved maintenance window, then confirm the machine has no active rentals or other workloads.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-442f5fb5941fefd1 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Disable VM Support](http://127.0.0.1:4000/host/vms#disable-vm-support) — `MCL-805d144f549c45af`

**Status:** UNVALIDATED

**Literal source text:** ```bash sudo python3 /var/lib/vastai_kaalia/enable_vms.py off ```

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-805d144f549c45af and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Disable VM Support](http://127.0.0.1:4000/host/vms#disable-vm-support) — `MCL-ecf1826f8fa24508`

**Status:** UNVALIDATED

**Literal source text:** The command marks VM enablement disabled and removes the VM configuration entry when present. It does not stop workloads, end rentals, or verify that the Host is safe to change.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** VM platform and Host integration source owner; Authorized Host/API operator

**Next:** The VM platform and Host integration source owner supplies the exact repository, revision, path, and symbol/operation locator; bind it to MCL-ecf1826f8fa24508 and retain the focused source check. An authorized Host/API operator runs only an approved representative check for MCL-ecf1826f8fa24508 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Disable VM Support](http://127.0.0.1:4000/host/vms#disable-vm-support) — `MCL-a9c03c643398c554`

**Status:** UNVALIDATED

**Literal source text:** Run [Check VM Status](#check-vm-status) afterwards and confirm it reports `off`. Most hosts do not need to disable anything; unsupported machines are detected automatically.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-a9c03c643398c554 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Kernel Options](http://127.0.0.1:4000/host/vms#kernel-options) — `MCL-24d79fc676359985`

**Status:** UNVALIDATED

**Literal source text:** ```text GRUB_CMDLINE_LINUX="intel_iommu=on nvidia_drm.modeset=0" ```

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-24d79fc676359985 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Kernel Options](http://127.0.0.1:4000/host/vms#kernel-options) — `MCL-9c24c283be82dd31`

**Status:** UNVALIDATED

**Literal source text:** ```text rd.driver.blacklist=nouveau modprobe.blacklist=nouveau ```

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-9c24c283be82dd31 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Kernel Options](http://127.0.0.1:4000/host/vms#kernel-options) — `MCL-5edc91d67bb8cea6`

**Status:** UNVALIDATED

**Literal source text:** Apply and reboot:

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-5edc91d67bb8cea6 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Kernel Options](http://127.0.0.1:4000/host/vms#kernel-options) — `MCL-64fd1fc1c1ba0bf8`

**Status:** BLOCKED

**Literal source text:** ```bash sudo update-grub sudo reboot ```

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** [EV-HOST-COMMAND-OCCURRENCE-RECONCILIATION-01](evidence/2026-09-03-host-repository-rebase-01/result.md) — Static or partial evidence does not establish the prohibited or unavailable runtime behavior.

**Responsible role:** Authorized Host/API operator

**Next:** Under explicit authorization, provide this prerequisite for CLM-1e2f077efd167bfd: Explicit operator authorization and a controlled disposable or idle VM-capable Host are unavailable for changing the bootloader configuration and rebooting it. Then retain the exact observation and cleanup.

### [Display Managers And GPU Processes](http://127.0.0.1:4000/host/vms#display-managers-and-gpu-processes) — `MCL-2cf47916d16787bb`

**Status:** UNVALIDATED

**Literal source text:** Disable display managers, XOrg/Wayland sessions, and background GPU processes. `nvidia-persistenced` is okay because it is managed by the host stack.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-2cf47916d16787bb and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Retry Enablement](http://127.0.0.1:4000/host/vms#retry-enablement) — `MCL-256a7246625a0529`

**Status:** UNVALIDATED

**Literal source text:** This is a forced, state-changing setup retry—not a simple toggle. It can install VM packages, pull a test image, restart Host services, and run a GPU-passthrough test. Prevent new rentals during the approved maintenance window, then confirm there are no active rentals, containers, or GPU workloads.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-256a7246625a0529 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Retry Enablement](http://127.0.0.1:4000/host/vms#retry-enablement) — `MCL-1bbbc88edc5f88d7`

**Status:** UNVALIDATED

**Literal source text:** ```bash sudo python3 /var/lib/vastai_kaalia/enable_vms.py on -f ```

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-1bbbc88edc5f88d7 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Retry Enablement](http://127.0.0.1:4000/host/vms#retry-enablement) — `MCL-60ec9280a68ab6d7`

**Status:** BLOCKED

**Literal source text:** ```bash python3 /var/lib/vastai_kaalia/enable_vms.py check nvidia-smi -L systemctl is-active vastai.service docker.service ```

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** [EV-HOST-COMMAND-OCCURRENCE-RECONCILIATION-01](evidence/2026-09-03-host-repository-rebase-01/result.md) — Static or partial evidence does not establish the prohibited or unavailable runtime behavior.

**Responsible role:** VM platform and Host integration source owner; Authorized Host/API operator

**Next:** Under explicit authorization, provide this prerequisite for CLM-0fa4c0088a41c909: A representative authorized VM-capable Host in the post-enable state is unavailable for checking VM state, GPU visibility, and Host service health together. Then retain the exact observation and cleanup.

### [Retry Enablement](http://127.0.0.1:4000/host/vms#retry-enablement) — `MCL-6ebe7cf6297a6cbd`

**Status:** UNVALIDATED

**Literal source text:** Treat only exact `on` status, visible expected GPUs, and active Host services as a successful enablement. Treat `pending`, `off`, error or abort text, an unexpected status, a missing GPU, or an inactive service as a failure. If IOMMU groups are not set up, correct the BIOS and kernel IOMMU configuration, reboot, and verify the grouping before retrying.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** VM platform and Host integration source owner; Authorized Host/API operator

**Next:** The VM platform and Host integration source owner supplies the exact repository, revision, path, and symbol/operation locator; bind it to MCL-6ebe7cf6297a6cbd and retain the focused source check. An authorized Host/API operator runs only an approved representative check for MCL-6ebe7cf6297a6cbd and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

## [How to Self-Test](http://127.0.0.1:4000/host/how-to-self-test)

### [Introduction](http://127.0.0.1:4000/host/how-to-self-test) — `MCL-c1dac7780d26eb96`

**Status:** UNVALIDATED

**Literal source text:** Passing self-test makes a machine eligible for verification. It does not guarantee verification, search placement, or rentals.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-c1dac7780d26eb96 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Before You Run It](http://127.0.0.1:4000/host/how-to-self-test#before-you-run-it) — `MCL-8ba9c19714b4151b`

**Status:** UNVALIDATED

**Literal source text:** - Install the [Vast CLI](https://cloud.vast.ai/cli/), then follow [CLI Hello World](/cli/hello-world) to authenticate and verify the installation. For host-oriented command guidance, see [Host CLI/API/SDK](/host/cli-api-sdk).

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Self-Test and Verification source owner; Authorized Host/API operator

**Next:** The Self-Test and Verification source owner supplies the exact repository, revision, path, and symbol/operation locator; bind it to MCL-8ba9c19714b4151b and retain the focused source check. An authorized Host/API operator runs only an approved representative check for MCL-8ba9c19714b4151b and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Before You Run It](http://127.0.0.1:4000/host/how-to-self-test#before-you-run-it) — `MCL-683196d886341a05`

**Status:** UNVALIDATED

**Literal source text:** - Set the API key for the host-enabled account that owns the machine. For host key guidance, see [Host Account Security](/host/account-security-for-hosts).

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Self-Test and Verification source owner; Authorized Host/API operator

**Next:** The Self-Test and Verification source owner supplies the exact repository, revision, path, and symbol/operation locator; bind it to MCL-683196d886341a05 and retain the focused source check. An authorized Host/API operator runs only an approved representative check for MCL-683196d886341a05 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Before You Run It](http://127.0.0.1:4000/host/how-to-self-test#before-you-run-it) — `MCL-048a299e10fd84c5`

**Status:** UNVALIDATED

**Literal source text:** - List the machine.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-048a299e10fd84c5 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Before You Run It](http://127.0.0.1:4000/host/how-to-self-test#before-you-run-it) — `MCL-19008f1355053cd3`

**Status:** UNVALIDATED

**Literal source text:** - Make sure no client is actively renting it.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-19008f1355053cd3 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Before You Run It](http://127.0.0.1:4000/host/how-to-self-test#before-you-run-it) — `MCL-a94f1650b8004457`

**Status:** UNVALIDATED

**Literal source text:** - Run from outside the host LAN when testing ports, such as a cloud VM or mobile connection. Same-LAN tests can be confused by NAT hairpinning.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-a94f1650b8004457 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Before You Run It](http://127.0.0.1:4000/host/how-to-self-test#before-you-run-it) — `MCL-9ad33b25fd88c5cb`

**Status:** FAIL

**Literal source text:** ```bash vastai set api-key <API_KEY> ```

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** [EV-CLI-SET-API-KEY-PERMISSIONS-01](evidence/2026-09-02-cli-set-api-key-permissions-attempt-01/result.md) — The retained adverse command result concerns a security/output property not asserted by the literal fenced syntax alone; the exact documentation claim remains UNVALIDATED rather than being falsely contradicted.; [EVIDENCE-REUSE-MCL-9ad33b25fd88c5cb-1](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/b-hardware-install/sources/auth.py) — Exact retained selector; source/runtime boundary is stated in the passage review.

**Responsible role:** Self-Test and Verification source owner; Authorized Host/API operator

**Next:** Provide a secure key-storage path or verify a corrected CLI release; retain the existing isolated0644 failure and test a restrictive new-file/existing-file workflow before promoting this credential instruction.

### [What Self-Test Checks](http://127.0.0.1:4000/host/how-to-self-test#what-self-test-checks) — `MCL-f67dccb3df0a9e2b`

**Status:** UNVALIDATED

**Literal source text:** The CLI first checks listing requirements. If preflight passes, it rents a temporary diagnostic instance, starts the self-test image, polls progress, reports results, and destroys the instance.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Self-Test and Verification source owner; Authorized Host/API operator

**Next:** The Self-Test and Verification source owner supplies the exact repository, revision, path, and symbol/operation locator; bind it to MCL-f67dccb3df0a9e2b and retain the focused source check. An authorized Host/API operator runs only an approved representative check for MCL-f67dccb3df0a9e2b and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [What Self-Test Checks](http://127.0.0.1:4000/host/how-to-self-test#what-self-test-checks) — `MCL-2a90267a6c93782e`

**Status:** UNVALIDATED

**Literal source text:** Before renting the temporary diagnostic instance, the CLI checks whether the machine can be tested at all:

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Self-Test and Verification source owner; Authorized Host/API operator

**Next:** The Self-Test and Verification source owner supplies the exact repository, revision, path, and symbol/operation locator; bind it to MCL-2a90267a6c93782e and retain the focused source check. An authorized Host/API operator runs only an approved representative check for MCL-2a90267a6c93782e and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [What Self-Test Checks](http://127.0.0.1:4000/host/how-to-self-test#what-self-test-checks) — `MCL-be9a0aa02a879fe7`

**Status:** UNVALIDATED

**Literal source text:** - The machine has a rentable offer.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-be9a0aa02a879fe7 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [What Self-Test Checks](http://127.0.0.1:4000/host/how-to-self-test#what-self-test-checks) — `MCL-d4c66781870fa855`

**Status:** UNVALIDATED

**Literal source text:** - The API key can inspect the machine and offer.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Self-Test and Verification source owner; Authorized Host/API operator

**Next:** The Self-Test and Verification source owner supplies the exact repository, revision, path, and symbol/operation locator; bind it to MCL-d4c66781870fa855 and retain the focused source check. An authorized Host/API operator runs only an approved representative check for MCL-d4c66781870fa855 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [What Self-Test Checks](http://127.0.0.1:4000/host/how-to-self-test#what-self-test-checks) — `MCL-c7d653bb5b01f0a2`

**Status:** UNVALIDATED

**Literal source text:** - Direct ports are at least 3 ports per listed GPU.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-c7d653bb5b01f0a2 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [What Self-Test Checks](http://127.0.0.1:4000/host/how-to-self-test#what-self-test-checks) — `MCL-9051c0fd8445ad78`

**Status:** UNVALIDATED

**Literal source text:** - GPU VRAM is greater than 7 GB per GPU.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-9051c0fd8445ad78 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [What Self-Test Checks](http://127.0.0.1:4000/host/how-to-self-test#what-self-test-checks) — `MCL-5ec86097f680592e`

**Status:** UNVALIDATED

**Literal source text:** - System RAM is close to total GPU VRAM, capped around 2 TB for very high-VRAM machines.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-5ec86097f680592e and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [What Self-Test Checks](http://127.0.0.1:4000/host/how-to-self-test#what-self-test-checks) — `MCL-c386934182436dae`

**Status:** UNVALIDATED

**Literal source text:** - UDP echo on the mapped UDP port.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-c386934182436dae and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [What Self-Test Checks](http://127.0.0.1:4000/host/how-to-self-test#what-self-test-checks) — `MCL-f01d5d98ccf76175`

**Status:** UNVALIDATED

**Literal source text:** - PyTorch/CUDA import and GPU visibility.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-f01d5d98ccf76175 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [What Self-Test Checks](http://127.0.0.1:4000/host/how-to-self-test#what-self-test-checks) — `MCL-3011db17a84b2209`

**Status:** UNVALIDATED

**Literal source text:** - CUDA ResNet workload across all visible GPUs.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-3011db17a84b2209 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [What Self-Test Checks](http://127.0.0.1:4000/host/how-to-self-test#what-self-test-checks) — `MCL-0cbfe140f1ad9606`

**Status:** UNVALIDATED

**Literal source text:** - GPU memory allocation, including ECC-capable memory allocation checks where applicable.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-0cbfe140f1ad9606 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [What Self-Test Checks](http://127.0.0.1:4000/host/how-to-self-test#what-self-test-checks) — `MCL-514549d33ef5b213`

**Status:** UNVALIDATED

**Literal source text:** - NCCL initialization and synchronization across visible GPUs; see [`nccl_failed`](/host/self-test-reference#nccl-failed) if this stage fails.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-514549d33ef5b213 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [What Self-Test Checks](http://127.0.0.1:4000/host/how-to-self-test#what-self-test-checks) — `MCL-1b8afabd02aa1ba9`

**Status:** UNVALIDATED

**Literal source text:** - `stress-ng` and `gpu-burn` running together for 60 seconds.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-1b8afabd02aa1ba9 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Run The Test](http://127.0.0.1:4000/host/how-to-self-test#run-the-test) — `MCL-8a89e9f9e038dbe8`

**Status:** UNVALIDATED

**Literal source text:** <Frame caption="The Machines list exposes the Test machine action for a listed host.">

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-8a89e9f9e038dbe8 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Run The Test](http://127.0.0.1:4000/host/how-to-self-test#run-the-test) — `MCL-5278daabe8c0235e`

**Status:** UNVALIDATED

**Literal source text:** <Frame caption="Self-Test confirmation dialog before starting the diagnostic run.">

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-5278daabe8c0235e and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Run The Test](http://127.0.0.1:4000/host/how-to-self-test#run-the-test) — `MCL-d964b7fce869d64b`

**Status:** UNVALIDATED

**Literal source text:** To choose where failure bundles are saved:

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-d964b7fce869d64b and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Run The Test](http://127.0.0.1:4000/host/how-to-self-test#run-the-test) — `MCL-eeaf6da83da9eca7`

**Status:** BLOCKED

**Literal source text:** ```bash vastai self-test machine <machine_id> \   --support-bundle-dir /path/to/output ```

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** [CONNECTION-MCL-eeaf6da83da9eca7-01](current-host-connection-adjudications.json) — Exact normal support-bundle preflight only. No diagnostic rental, image execution, remote logs, runtime workload, verification, kernel result, or final billing outcome occurred.; [SELFTEST_PREFLIGHT](evidence/2026-09-09-host-ssh-jupyter-selftest-attempt-01/selftest-normal-preflight-01.json) — Exact normal support-bundle preflight only. No diagnostic rental, image execution, remote logs, runtime workload, verification, kernel result, or final billing outcome occurred.; [CANONICAL_CLI](evidence/2026-09-09-host-ssh-jupyter-selftest-attempt-01/canonical-cli-source-01.json) — Exact normal support-bundle preflight only. No diagnostic rental, image execution, remote logs, runtime workload, verification, kernel result, or final billing outcome occurred.

**Responsible role:** Self-Test and Verification source owner; Authorized Host/API operator

**Next:** Resolve the measured reliability and upload prerequisites, then use a new approved idle rental to rerun the normal support-bundle command. Do not call raw exit 0 or this preflight outcome a self-test runtime PASS.

### [Run The Test](http://127.0.0.1:4000/host/how-to-self-test#run-the-test) — `MCL-ec35bbf56e9767c4`

**Status:** UNVALIDATED

**Literal source text:** Do not paste API keys or account-specific commands into public channels.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Self-Test and Verification source owner; Authorized Host/API operator

**Next:** The Self-Test and Verification source owner supplies the exact repository, revision, path, and symbol/operation locator; bind it to MCL-ec35bbf56e9767c4 and retain the focused source check. An authorized Host/API operator runs only an approved representative check for MCL-ec35bbf56e9767c4 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Run The Test](http://127.0.0.1:4000/host/how-to-self-test#run-the-test) — `MCL-0047da81ba902254`

**Status:** UNVALIDATED

**Literal source text:** If the test passes, the CLI reports success.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Self-Test and Verification source owner; Authorized Host/API operator

**Next:** The Self-Test and Verification source owner supplies the exact repository, revision, path, and symbol/operation locator; bind it to MCL-0047da81ba902254 and retain the focused source check. An authorized Host/API operator runs only an approved representative check for MCL-0047da81ba902254 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Run The Test](http://127.0.0.1:4000/host/how-to-self-test#run-the-test) — `MCL-47b2f2cb0f66b096`

**Status:** UNVALIDATED

**Literal source text:** If it fails, look up the exact error in the [Self-Test Reference](/host/self-test-reference), fix the cause, and rerun.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Self-Test and Verification source owner; Authorized Host/API operator

**Next:** The Self-Test and Verification source owner supplies the exact repository, revision, path, and symbol/operation locator; bind it to MCL-47b2f2cb0f66b096 and retain the focused source check. An authorized Host/API operator runs only an approved representative check for MCL-47b2f2cb0f66b096 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Machine Not Found Or Not Rentable](http://127.0.0.1:4000/host/how-to-self-test#machine-not-found-or-not-rentable) — `MCL-7fc173764084ca15`

**Status:** UNVALIDATED

**Literal source text:** - The machine is listed.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-7fc173764084ca15 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Machine Not Found Or Not Rentable](http://127.0.0.1:4000/host/how-to-self-test#machine-not-found-or-not-rentable) — `MCL-8b223ce2d1087391`

**Status:** UNVALIDATED

**Literal source text:** - There are active offers.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-8b223ce2d1087391 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Machine Not Found Or Not Rentable](http://127.0.0.1:4000/host/how-to-self-test#machine-not-found-or-not-rentable) — `MCL-a45474ed843299f1`

**Status:** UNVALIDATED

**Literal source text:** - The account owns the machine.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-a45474ed843299f1 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Machine Not Found Or Not Rentable](http://127.0.0.1:4000/host/how-to-self-test#machine-not-found-or-not-rentable) — `MCL-0686490d4a626113`

**Status:** UNVALIDATED

**Literal source text:** - Reliability is above the gate unless using diagnostic mode.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-0686490d4a626113 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Machine Not Found Or Not Rentable](http://127.0.0.1:4000/host/how-to-self-test#machine-not-found-or-not-rentable) — `MCL-e542992c1948de75`

**Status:** UNVALIDATED

**Literal source text:** - The Machines page has no red errors.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-e542992c1948de75 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Machine Not Found Or Not Rentable](http://127.0.0.1:4000/host/how-to-self-test#machine-not-found-or-not-rentable) — `MCL-d14fe9113b9c32b8`

**Status:** UNVALIDATED

**Literal source text:** - Upload speed, download speed, RAM, and ports are populated.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-d14fe9113b9c32b8 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Fresh Install Self-Test](http://127.0.0.1:4000/host/how-to-self-test#fresh-install-self-test) — `MCL-9930b0a427f841c4`

**Status:** UNVALIDATED

**Literal source text:** The installer can start self-test automatically after the daemon comes online. On a fresh host, it may wait about 10 minutes before listing the machine and starting the temporary diagnostic instance.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Self-Test and Verification source owner; Authorized Host/API operator

**Next:** The Self-Test and Verification source owner supplies the exact repository, revision, path, and symbol/operation locator; bind it to MCL-9930b0a427f841c4 and retain the focused source check. An authorized Host/API operator runs only an approved representative check for MCL-9930b0a427f841c4 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Fresh Install Self-Test](http://127.0.0.1:4000/host/how-to-self-test#fresh-install-self-test) — `MCL-00ac616c43d84f6c`

**Status:** UNVALIDATED

**Literal source text:** On the host, watch only for the planned self-test window; press `Ctrl+C` when the self-test ends and confirm that `tail` exits:

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-00ac616c43d84f6c and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Fresh Install Self-Test](http://127.0.0.1:4000/host/how-to-self-test#fresh-install-self-test) — `MCL-aa0536c1bc80adc2`

**Status:** UNVALIDATED

**Literal source text:** If reliability is still `<= 0.90`, the installer may run with `--ignore-requirements` as a diagnostic. That does not qualify the machine for verification.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Self-Test and Verification source owner; Authorized Host/API operator

**Next:** The Self-Test and Verification source owner supplies the exact repository, revision, path, and symbol/operation locator; bind it to MCL-aa0536c1bc80adc2 and retain the focused source check. An authorized Host/API operator runs only an approved representative check for MCL-aa0536c1bc80adc2 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Ignore Requirements Mode](http://127.0.0.1:4000/host/how-to-self-test#ignore-requirements-mode) — `MCL-239743d032b1b204`

**Status:** UNVALIDATED

**Literal source text:** Use `--ignore-requirements` only to diagnose rentability or runtime behavior. A pass in this mode does not mean the machine meets verification requirements.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-239743d032b1b204 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Ignore Requirements Mode](http://127.0.0.1:4000/host/how-to-self-test#ignore-requirements-mode) — `MCL-2504404e933395bb`

**Status:** UNVALIDATED

**Literal source text:** Even with `--ignore-requirements`, the machine still needs at least three direct open ports or self-test can fail.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-2504404e933395bb and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

## [Volume Offers](http://127.0.0.1:4000/host/volume-offers)

### [Introduction](http://127.0.0.1:4000/host/volume-offers) — `VOL-C01`

**Status:** BLOCKED

**Literal source text:** A local volume is persistent storage backed by one physical host machine. It is separate from an instance's container disk: a renter can destroy an instance, keep the volume, and attach it to another Docker instance on the same machine.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** [EV-HOST-VOLUME-OFFERS-STATIC-SOURCE-01](evidence/2026-09-03-host-repository-rebase-01/result.md) — CLI terminology does not prove persistence.

**Responsible role:** Volumes backend lifecycle source owner; Authorized Volumes Host/renter operator

**Next:** Obtain the exact backend lifecycle revision and explicit paid/mutation authorization, then retain the lifecycle run.

### [Introduction](http://127.0.0.1:4000/host/volume-offers) — `VOL-C02`

**Status:** BLOCKED

**Literal source text:** A local volume is persistent storage backed by one physical host machine. It is separate from an instance's container disk: a renter can destroy an instance, keep the volume, and attach it to another Docker instance on the same machine.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** [EV-HOST-VOLUME-OFFERS-STATIC-SOURCE-01](evidence/2026-09-03-host-repository-rebase-01/result.md) — Machine-id fields corroborate identity but do not prove enforcement.

**Responsible role:** Volumes and scheduler backend source owner; Authorized Volumes Host/renter operator

**Next:** Bind the scheduler constraint and retain positive/adverse runs.

### [Introduction](http://127.0.0.1:4000/host/volume-offers) — `VOL-C03`

**Status:** BLOCKED

**Literal source text:** A local volume is persistent storage backed by one physical host machine. It is separate from an instance's container disk: a renter can destroy an instance, keep the volume, and attach it to another Docker instance on the same machine.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** [EV-HOST-VOLUME-OFFERS-STATIC-SOURCE-01](evidence/2026-09-03-host-repository-rebase-01/result.md) — Separate client endpoints are indirect evidence only.

**Responsible role:** Instances and Volumes backend source owners; Authorized Volumes Host/renter operator

**Next:** Inspect cascade policy and retain create/write/destroy/re-attach/read evidence.

### [Volume Lifecycle](http://127.0.0.1:4000/host/volume-offers#volume-lifecycle) — `VOL-C11`

**Status:** BLOCKED

**Literal source text:** 1. **Prepare host storage.** Put Docker's data root on fast SSD or NVMe storage using XFS project quotas. See [Storage Setup](/host/storage-setup).

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** [EV-HOST-VOLUME-OFFERS-STATIC-SOURCE-01](evidence/2026-09-03-host-repository-rebase-01/result.md) — The local wizard corroborates the gate but is not the full installer/backend.; [SCAN-VOL-C11-PARTIAL-5d984da0](evidence/2026-09-08-h100x4-safe-installer-attempt-01/source-review-summary.json) — Retained public installer identity is available: https://console.vast.ai/install SHA256 6b00488ccf837ed6b7b5375270b75db284c3906f6aec832ad9c8573f44eaac6c; source inspection includes Docker mount reuse lines 1096–1168. This summary is context, not terminal code proof.; [SCAN-VOL-C11-PARTIAL-974f62a4](evidence/2026-09-09-h100x4-direct-install-attempt-02/postcheck-02.json) — POST-05/06/07 report the observed /var/lib/docker XFS mount, persistent pquota entry, and project-quota accounting/enforcement ON on NEW_H100X4_HOST. This is a point-in-time retained observation, not all-Host fast-storage/Volume applicability proof.

**Responsible role:** Documentation technical-source reviewer

**Next:** Start with the already retained installer bytes identified in source-review-summary.json and the POST-05/06/07 XFS observation. Bind exact storage prerequisite logic and determine what residual fast-storage/Volume applicability needs a representative authorized check. Escalate only a concrete unavailable source or conflict; do not request a generic owner decision.

### [Volume Lifecycle / Shared Disk Capacity](http://127.0.0.1:4000/host/volume-offers#volume-lifecycle-shared-disk-capacity) — `VOL-C13`

**Status:** BLOCKED

**Literal source text:** 2. **Publish a volume offer.** Create it with the machine listing or list storage separately. This advertises a maximum rentable capacity; it does not create a renter volume. The capacity in a volume offer is the maximum amount renters may allocate; publishing the offer does not itself create a renter volume. When a renter creates a volume, its requested size is allocated from that offer and must be included when you plan the shared disk pool.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** [EV-HOST-VOLUME-OFFERS-STATIC-SOURCE-01](evidence/2026-09-03-host-repository-rebase-01/result.md) — Client help is a contract hint, not enforcement proof.

**Responsible role:** Volumes allocation backend source owner; Authorized Volumes Host/renter operator

**Next:** Bind the allocation implementation and retain offer-only, partial, exact, and over-capacity observations.

### [Volume Lifecycle](http://127.0.0.1:4000/host/volume-offers#volume-lifecycle) — `VOL-C15`

**Status:** BLOCKED

**Literal source text:** 3. **A renter creates a volume.** The renter searches offers and chooses a fixed size. That allocation persists independently of any one instance.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** [EV-HOST-VOLUME-OFFERS-STATIC-SOURCE-01](evidence/2026-09-03-host-repository-rebase-01/result.md) — Separate endpoints are indirect evidence.

**Responsible role:** Volumes and Instances ownership/cascade source owner; Authorized Volumes Host/renter operator

**Next:** Bind the exact backend ownership/cascade source, then retain create/write/attach/destroy/re-attach/read runtime evidence under explicit authorization.

### [Volume Lifecycle](http://127.0.0.1:4000/host/volume-offers#volume-lifecycle) — `VOL-C17`

**Status:** BLOCKED

**Literal source text:** 4. **The renter attaches it to an instance.** A new or existing volume is linked while a Docker instance is created and appears at the selected mount path.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** [EV-HOST-VOLUME-OFFERS-STATIC-SOURCE-01](evidence/2026-09-03-host-repository-rebase-01/result.md) — Static payload construction cannot prove a working mount.

**Responsible role:** Authorized Volumes Host/renter operator

**Next:** Retain target IDs, revision, cost, mount/read/write observation, and cleanup.

### [Volume Lifecycle](http://127.0.0.1:4000/host/volume-offers#volume-lifecycle) — `VOL-C18`

**Status:** BLOCKED

**Literal source text:** 5. **The renter reuses or deletes it.** Destroying the instance leaves the volume intact. To delete the volume permanently, the renter must first destroy every instance using it.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** [EV-HOST-VOLUME-OFFERS-STATIC-SOURCE-01](evidence/2026-09-03-host-repository-rebase-01/result.md) — No retained volume lifecycle run exists.

**Responsible role:** Instances and Volumes cascade source owner; Authorized Volumes Host/renter operator

**Next:** Inspect cascade policy and execute the preservation test under explicit authorization.

### [Volume Lifecycle](http://127.0.0.1:4000/host/volume-offers#volume-lifecycle) — `VOL-C19`

**Status:** BLOCKED

**Literal source text:** 5. **The renter reuses or deletes it.** Destroying the instance leaves the volume intact. To delete the volume permanently, the renter must first destroy every instance using it.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** [EV-HOST-VOLUME-OFFERS-STATIC-SOURCE-01](evidence/2026-09-03-host-repository-rebase-01/result.md) — CLI/API docstrings state the prerequisite but do not prove enforcement.

**Responsible role:** Volumes enforcement and error-contract source owner; Authorized Volumes Host/renter operator

**Next:** Confirm the error contract and retain both outcomes.

### [Publish Local Storage](http://127.0.0.1:4000/host/volume-offers#publish-local-storage) — `VOL-C38`

**Status:** UNVALIDATED

**Literal source text:** Set `--vol_size 0` when you do not want the machine listing to include a volume offer. Pass an explicit size and price so the advertised capacity is intentional.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Documentation technical-source reviewer

**Next:** Inspect the pinned option/dispatch and backend handling of the exact values, then bind applicable retained execution/readback. Do not promote backend semantics from a generated client schema.

### [Shared Disk Capacity](http://127.0.0.1:4000/host/volume-offers#shared-disk-capacity) — `VOL-C25`

**Status:** BLOCKED

**Literal source text:** Local volume allocations use the same machine storage pool as renter instance disks. Stopped instances, cached images, and other allocated storage also need space in that pool.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** [EV-HOST-VOLUME-OFFERS-STATIC-SOURCE-01](evidence/2026-09-03-host-repository-rebase-01/result.md) — Installer wording does not prove marketplace accounting.

**Responsible role:** Host daemon and storage-accounting source owner; Authorized Volumes Host/renter operator

**Next:** Bind storage-accounting source and retain per-allocation before/after values.

### [Shared Disk Capacity](http://127.0.0.1:4000/host/volume-offers#shared-disk-capacity) — `VOL-C26`

**Status:** BLOCKED

**Literal source text:** The capacity in a volume offer is the maximum amount renters may allocate; publishing the offer does not itself create a renter volume. When a renter creates a volume, its requested size is allocated from that offer and must be included when you plan the shared disk pool.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** [EV-HOST-VOLUME-OFFERS-STATIC-SOURCE-01](evidence/2026-09-03-host-repository-rebase-01/result.md) — Client help does not expose the backend transaction.

**Responsible role:** Volumes and storage-allocation source owner; Authorized Volumes Host/renter operator

**Next:** Inspect allocation code and retain offer capacity before/after create/delete.

### [Shared Disk Capacity](http://127.0.0.1:4000/host/volume-offers#shared-disk-capacity) — `VOL-C27`

**Status:** UNVALIDATED

**Literal source text:** For example, if you advertise a 500 GB offer and a renter creates a 200 GB volume, include that 200 GB allocation in your storage plan. Keep enough headroom for active volume contracts and new instance creation.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Documentation technical-source reviewer

**Next:** Record the engineering rationale, inspect relevant canonical technical behavior, and reuse applicable retained observations. Split guidance from any actual obligation or effect when their methods differ.

### [Local Volume Limits](http://127.0.0.1:4000/host/volume-offers#local-volume-limits) — `VOL-C29`

**Status:** BLOCKED

**Literal source text:** - Stays on the physical machine where the renter created it.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** [EV-HOST-VOLUME-OFFERS-STATIC-SOURCE-01](evidence/2026-09-03-host-repository-rebase-01/result.md) — machine_id fields do not prove non-migration.

**Responsible role:** Volumes placement and migration source owner; Authorized Volumes Host/renter operator

**Next:** Bind the exact placement/migration implementation source, then retain a representative create/attach/reuse lifecycle observation on the same and a different machine.

### [Local Volume Limits](http://127.0.0.1:4000/host/volume-offers#local-volume-limits) — `VOL-C30`

**Status:** BLOCKED

**Literal source text:** - Can attach only to instances scheduled on that same machine.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** [EV-HOST-VOLUME-OFFERS-STATIC-SOURCE-01](evidence/2026-09-03-host-repository-rebase-01/result.md) — Client/OpenAPI fields do not encode equality enforcement.

**Responsible role:** Volumes and scheduler constraint source owner; Authorized Volumes Host/renter operator

**Next:** Bind the constraint and retain positive/adverse outcomes.

### [Local Volume Limits](http://127.0.0.1:4000/host/volume-offers#local-volume-limits) — `VOL-C32`

**Status:** BLOCKED

**Literal source text:** - Works with Docker instances, not VM instances.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** [EV-HOST-VOLUME-OFFERS-STATIC-SOURCE-01](evidence/2026-09-03-host-repository-rebase-01/result.md) — The current public schema has no mutual-exclusion rule.

**Responsible role:** Volumes and VM compatibility source owner; Authorized Volumes Host/renter operator

**Next:** Confirm the backend rule, update the schema if applicable, and retain Docker-positive/VM-negative evidence.

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

## [Understanding Verification](http://127.0.0.1:4000/host/understanding-verification)

### [How Verification Works](http://127.0.0.1:4000/host/understanding-verification#how-verification-works) — `MCL-70b4fe37c8aad7ec`

**Status:** UNVALIDATED

**Literal source text:** Verification is automated. A machine becomes eligible when it passes self-test and meets reliability, performance, hardware, network, and marketplace gates.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-70b4fe37c8aad7ec and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Main Factors](http://127.0.0.1:4000/host/understanding-verification#main-factors) — `MCL-6c6a3378c5fb5ba0`

**Status:** UNVALIDATED

**Literal source text:** | Reliability | The machine enters the verification pool when reliability is greater than 0.9. Higher reliability improves confidence. |

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-6c6a3378c5fb5ba0 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Main Factors](http://127.0.0.1:4000/host/understanding-verification#main-factors) — `MCL-ef6d9e219ca7cc52`

**Status:** UNVALIDATED

**Literal source text:** | Hardware balance | GPU model/count, VRAM, CPU, RAM, PCIe bandwidth, storage, and network should match the GPU tier. |

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-ef6d9e219ca7cc52 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Main Factors](http://127.0.0.1:4000/host/understanding-verification#main-factors) — `MCL-24f252ff0846659b`

**Status:** UNVALIDATED

**Literal source text:** | Network | Stable bandwidth and reachable direct ports. |

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-24f252ff0846659b and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Main Factors](http://127.0.0.1:4000/host/understanding-verification#main-factors) — `MCL-042c5f8aaccb7a52`

**Status:** UNVALIDATED

**Literal source text:** | Software | Compatible NVIDIA/AMD driver stack, CUDA/runtime health, Docker/GPU runtime health, and a clean host. |

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-042c5f8aaccb7a52 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Main Factors](http://127.0.0.1:4000/host/understanding-verification#main-factors) — `MCL-cf040efee02904ba`

**Status:** UNVALIDATED

**Literal source text:** | DLPerf | Sustained real-world GPU throughput; PCIe, thermals, power, and drivers can affect it. |

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-cf040efee02904ba and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Main Factors](http://127.0.0.1:4000/host/understanding-verification#main-factors) — `MCL-35c45594b2973fb7`

**Status:** UNVALIDATED

**Literal source text:** | Marketplace demand | In-demand GPUs, strong reliability, enough VRAM, and good network/location are more likely to be prioritized. |

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-35c45594b2973fb7 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Supply And Demand](http://127.0.0.1:4000/host/understanding-verification#supply-and-demand) — `MCL-3d1c0fd6c2f50184`

**Status:** UNVALIDATED

**Literal source text:** Verification also considers renter demand and available supply. A healthy machine can wait if demand for that configuration is low, while scarce or high-demand configurations may be prioritized.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-3d1c0fd6c2f50184 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Supply And Demand](http://127.0.0.1:4000/host/understanding-verification#supply-and-demand) — `MCL-7d798f0938fa39dc`

**Status:** UNVALIDATED

**Literal source text:** - Use in-demand GPU models.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-7d798f0938fa39dc and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Supply And Demand](http://127.0.0.1:4000/host/understanding-verification#supply-and-demand) — `MCL-f6193d7f5743d7a6`

**Status:** UNVALIDATED

**Literal source text:** - Enable VM support only when the machine supports it cleanly.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-f6193d7f5743d7a6 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [How Long Can Verification Take?](http://127.0.0.1:4000/host/understanding-verification#how-long-can-verification-take) — `MCL-8b6c160b1c6208cb`

**Status:** UNVALIDATED

**Literal source text:** There is no fixed timeline. Passing self-test makes the machine eligible, but timing depends on automated checks, reliability, machine health, supply, demand, and platform policy.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Documentation technical-source reviewer

**Next:** Inspect verification scheduler/gate/configuration and exact self-test versus backend checks. Reuse compatible observations and keep any unsupported timeline/guarantee statement unresolved.

### [Can Support Verify My Machine?](http://127.0.0.1:4000/host/understanding-verification#can-support-verify-my-machine) — `MCL-e7728d8a2327a1ed`

**Status:** UNVALIDATED

**Literal source text:** No. Support can help with account issues or backend anomalies, but ordinary verification is not a manual support queue. Keep the machine healthy, eligible, and competitively listed while automation evaluates it.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-e7728d8a2327a1ed and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Avoid](http://127.0.0.1:4000/host/understanding-verification#avoid) — `MCL-16222ee75946f1ba`

**Status:** UNVALIDATED

**Literal source text:** - Reducing GPU count, RAM, disk, or other capacity after machine creation.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-16222ee75946f1ba and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Read Next](http://127.0.0.1:4000/host/understanding-verification#read-next) — `MCL-e93d1657e1f7f725`

**Status:** UNVALIDATED

**Literal source text:** | Run diagnostics | [How to Self-Test](/host/how-to-self-test) |

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-e93d1657e1f7f725 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Read Next](http://127.0.0.1:4000/host/understanding-verification#read-next) — `MCL-b0cfd010cb0e16f6`

**Status:** UNVALIDATED

**Literal source text:** | Market fit | [GPU Market Metrics](/host/market-metrics) |

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-b0cfd010cb0e16f6 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

## [Verification Stages](http://127.0.0.1:4000/host/verification-stages)

### [Lifecycle](http://127.0.0.1:4000/host/verification-stages#lifecycle) — `CUR-718eae8798859de8`

**Status:** UNVALIDATED

**Literal source text:** ```text Unverified -> Verified -> Deverified -> Unverified ```

**Required proof:** Canonical Implementation Source

**Existing proof / limit:** [EVIDENCE-REUSE-CUR-718eae8798859de8-1](evidence/2026-09-15-host-unvalidated-source-families-attempt-01/s2-s3/owner-58492.md) — Exact retained selector; source/runtime boundary is stated in the passage review.; [EVIDENCE-REUSE-CUR-718eae8798859de8-2](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/c-operations-verification/sources/upstream-verification.mdx) — Exact retained selector; source/runtime boundary is stated in the passage review.; [EVIDENCE-REUSE-CUR-718eae8798859de8-3](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/c-operations-verification/sources/context_verification-stages.mdx) — Exact retained selector; source/runtime boundary is stated in the passage review.; [EVIDENCE-REUSE-CUR-718eae8798859de8-4](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/c-operations-verification/sources/setup-requirement-excerpts.json) — Exact retained selector; source/runtime boundary is stated in the passage review.

**Responsible role:** Documentation technical-source reviewer; implementation source owner only for an unavailable or unclear definition

**Next:** Obtain the verification owner’s state definitions and allowed transitions, then correct or confirm this exact four-state fence. No induced failure or new rental is required merely to document the state model.

### [Lifecycle](http://127.0.0.1:4000/host/verification-stages#lifecycle) — `CUR-e388e981c1bb088c`

**Status:** UNVALIDATED

**Literal source text:** Automation evaluates reliability, performance, hardware, network, and current marketplace demand.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host implementation source owner

**Next:** Bind an exact canonical source, authorized runtime observation, or accountable-owner decision before changing status.

### [Lifecycle](http://127.0.0.1:4000/host/verification-stages#lifecycle) — `CUR-2a4d8f7b6bf42c0c`

**Status:** UNVALIDATED

**Literal source text:** Top-tier AI GPUs are prioritized for verification because demand for them is highest. This includes datacenter GPUs such as B300, B200, H200, and H100, and dense premium builds such as RTX PRO 6000 (Server/WS/Max-Q), 8x RTX 5090, and 8x RTX 4090.

**Required proof:** Canonical Implementation Source

**Existing proof / limit:** [EVIDENCE-REUSE-CUR-2a4d8f7b6bf42c0c-1](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/c-operations-verification/sources/upstream-verification.mdx) — Exact retained selector; source/runtime boundary is stated in the passage review.; [EVIDENCE-REUSE-CUR-2a4d8f7b6bf42c0c-2](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/c-operations-verification/sources/context_verification-stages.mdx) — Exact retained selector; source/runtime boundary is stated in the passage review.; [EVIDENCE-REUSE-CUR-2a4d8f7b6bf42c0c-3](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/c-operations-verification/sources/setup-requirement-excerpts.json) — Exact retained selector; source/runtime boundary is stated in the passage review.

**Responsible role:** Documentation technical-source reviewer; implementation source owner only for an unavailable or unclear definition

**Next:** Ask the verification owner to confirm the current prioritized GPU families and whether these dense configurations are priority criteria; retain a dated rule and remove unsupported demand superlatives if needed.

### [Listing Minimums](http://127.0.0.1:4000/host/verification-stages#listing-minimums) — `CUR-42b4af76ba6c2110`

**Status:** UNVALIDATED

**Literal source text:** Start with [Supported Hardware](/host/supported-hardware) when planning a machine. Listing a machine and passing Self-Test do not guarantee verification; review the verification requirements below before preparing hardware.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host implementation source owner

**Next:** Bind an exact canonical source, authorized runtime observation, or accountable-owner decision before changing status.

### [Verification Requirements](http://127.0.0.1:4000/host/verification-stages#verification-requirements) — `CUR-8dcdb5c689a3c52d`

**Status:** UNVALIDATED

**Literal source text:** Your machine must meet all of the following.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host implementation source owner

**Next:** Bind an exact canonical source, authorized runtime observation, or accountable-owner decision before changing status.

### [GPU](http://127.0.0.1:4000/host/verification-stages#gpu) — `CUR-b296cc09bf311833`

**Status:** UNVALIDATED

**Literal source text:** | GPU | NVIDIA, Maxwell or newer |

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host implementation source owner

**Next:** Bind an exact canonical source, authorized runtime observation, or accountable-owner decision before changing status.

### [GPU](http://127.0.0.1:4000/host/verification-stages#gpu) — `CUR-1efcf4fe36961e1b`

**Status:** UNVALIDATED

**Literal source text:** | VRAM per GPU | More than 7 GB |

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host implementation source owner

**Next:** Bind an exact canonical source, authorized runtime observation, or accountable-owner decision before changing status.

### [GPU](http://127.0.0.1:4000/host/verification-stages#gpu) — `CUR-af6394a0e4e545eb`

**Status:** UNVALIDATED

**Literal source text:** | GPU models | All identical, do not mix models in one machine |

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host implementation source owner

**Next:** Bind an exact canonical source, authorized runtime observation, or accountable-owner decision before changing status.

### [GPU](http://127.0.0.1:4000/host/verification-stages#gpu) — `CUR-667565d054d6b5f0`

**Status:** UNVALIDATED

**Literal source text:** | PCIe bandwidth | More than 2.85 GiB/s per GPU |

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host implementation source owner

**Next:** Bind an exact canonical source, authorized runtime observation, or accountable-owner decision before changing status.

### [CPU](http://127.0.0.1:4000/host/verification-stages#cpu) — `CUR-0186c37202bd5029`

**Status:** UNVALIDATED

**Literal source text:** | CPU architecture | x86_64 or ARM64 |

**Required proof:** Canonical Implementation Source

**Existing proof / limit:** [EVIDENCE-REUSE-CUR-0186c37202bd5029-1](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/requirement-con-1516.json) — Exact retained selector; source/runtime boundary is stated in the passage review.; [EVIDENCE-REUSE-CUR-0186c37202bd5029-2](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/c-operations-verification/sources/upstream-verification.mdx) — Exact retained selector; source/runtime boundary is stated in the passage review.; [EVIDENCE-REUSE-CUR-0186c37202bd5029-3](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/c-operations-verification/sources/image_build.json) — Exact retained selector; source/runtime boundary is stated in the passage review.; [EVIDENCE-REUSE-CUR-0186c37202bd5029-4](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/c-operations-verification/sources/context_verification-stages.mdx) — Exact retained selector; source/runtime boundary is stated in the passage review.; [EVIDENCE-REUSE-CUR-0186c37202bd5029-5](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/c-operations-verification/sources/setup-requirement-excerpts.json) — Exact retained selector; source/runtime boundary is stated in the passage review.

**Responsible role:** Documentation technical-source reviewer; implementation source owner only for an unavailable or unclear definition

**Next:** Obtain one current owner ruling defining supported ARM64 host families, any beta/access conditions, and how the instruction-set rule differs from x86_64; reconcile this row and Supported Hardware together.

### [CPU](http://127.0.0.1:4000/host/verification-stages#cpu) — `CUR-1da68c391b45b80a`

**Status:** UNVALIDATED

**Literal source text:** | Instruction set | AVX |

**Required proof:** Canonical Implementation Source

**Existing proof / limit:** [EVIDENCE-REUSE-CUR-1da68c391b45b80a-1](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/c-operations-verification/sources/upstream-verification.mdx) — Exact retained selector; source/runtime boundary is stated in the passage review.; [EVIDENCE-REUSE-CUR-1da68c391b45b80a-2](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/requirement-con-1516.json) — Exact retained selector; source/runtime boundary is stated in the passage review.; [EVIDENCE-REUSE-CUR-1da68c391b45b80a-3](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/c-operations-verification/sources/context_verification-stages.mdx) — Exact retained selector; source/runtime boundary is stated in the passage review.; [EVIDENCE-REUSE-CUR-1da68c391b45b80a-4](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/c-operations-verification/sources/setup-requirement-excerpts.json) — Exact retained selector; source/runtime boundary is stated in the passage review.

**Responsible role:** Documentation technical-source reviewer; implementation source owner only for an unavailable or unclear definition

**Next:** Have the hardware/verification owner specify whether AVX applies only to x86_64 and what ARM64 instruction requirements replace it. Correct the paired architecture rows as one topic.

### [CPU](http://127.0.0.1:4000/host/verification-stages#cpu) — `CUR-30081ec0010a73f8`

**Status:** UNVALIDATED

**Literal source text:** | Physical CPU cores | 2 per GPU |

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host implementation source owner

**Next:** Bind an exact canonical source, authorized runtime observation, or accountable-owner decision before changing status.

### [Memory](http://127.0.0.1:4000/host/verification-stages#memory) — `CUR-a29f135ae78bb7ea`

**Status:** UNVALIDATED

**Literal source text:** | System RAM | At least 95% of total GPU VRAM |

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host implementation source owner

**Next:** Bind an exact canonical source, authorized runtime observation, or accountable-owner decision before changing status.

### [Memory](http://127.0.0.1:4000/host/verification-stages#memory) — `CUR-0ebfb18040c812be`

**Status:** UNVALIDATED

**Literal source text:** **Formula:** system RAM >= 0.95 x VRAM per GPU x number of GPUs

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host implementation source owner

**Next:** Bind an exact canonical source, authorized runtime observation, or accountable-owner decision before changing status.

### [Network](http://127.0.0.1:4000/host/verification-stages#network) — `CUR-5c4c047c25d90041`

**Status:** UNVALIDATED

**Literal source text:** | Forwarded ports | 5 ports per GPU, 100 ports per GPU recommended |

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host implementation source owner

**Next:** Bind an exact canonical source, authorized runtime observation, or accountable-owner decision before changing status.

### [Network](http://127.0.0.1:4000/host/verification-stages#network) — `CUR-0f437f612009c03d`

**Status:** UNVALIDATED

**Literal source text:** Renters connect directly to the machine over the WAN, so it needs a public IPv4 address with the port range forwarded to it. Machines behind CGNAT or a shared ISP IP cannot be used for hosting.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host implementation source owner

**Next:** Bind an exact canonical source, authorized runtime observation, or accountable-owner decision before changing status.

### [Operating System](http://127.0.0.1:4000/host/verification-stages#operating-system) — `CUR-a0ffa22c770d647e`

**Status:** UNVALIDATED

**Literal source text:** | NVIDIA driver | A currently supported release for your GPU |

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host implementation source owner

**Next:** Bind an exact canonical source, authorized runtime observation, or accountable-owner decision before changing status.

### [Operating System](http://127.0.0.1:4000/host/verification-stages#operating-system) — `CUR-79462c4dbc69459e`

**Status:** UNVALIDATED

**Literal source text:** | SSH access keys | A unique key pair per machine, never shared or reused |

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host implementation source owner

**Next:** Bind an exact canonical source, authorized runtime observation, or accountable-owner decision before changing status.

### [Operating System](http://127.0.0.1:4000/host/verification-stages#operating-system) — `CUR-ac44298a51ffb285`

**Status:** UNVALIDATED

**Literal source text:** Keeping the kernel patched is the host's responsibility. "Latest security patch level" means the newest patch for the LTS release you are on, not a release upgrade. Machines running a kernel with a known exploited vulnerability are restricted on the marketplace and can lose verification. See [Upgrade the Kernel](/host/upgrade-kernel).

**Required proof:** Canonical Implementation Source

**Existing proof / limit:** [EVIDENCE-REUSE-CUR-ac44298a51ffb285-1](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/c-operations-verification/sources/upstream-verification.mdx) — Exact retained selector; source/runtime boundary is stated in the passage review.; [EVIDENCE-REUSE-CUR-ac44298a51ffb285-2](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/a-policy-account/agreement-clauses.json) — Exact retained selector; source/runtime boundary is stated in the passage review.; [EVIDENCE-REUSE-CUR-ac44298a51ffb285-3](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/c-operations-verification/sources/context_verification-stages.mdx) — Exact retained selector; source/runtime boundary is stated in the passage review.; [EVIDENCE-REUSE-CUR-ac44298a51ffb285-4](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/c-operations-verification/sources/setup-requirement-excerpts.json) — Exact retained selector; source/runtime boundary is stated in the passage review.

**Responsible role:** Documentation technical-source reviewer; implementation source owner only for an unavailable or unclear definition

**Next:** Obtain a current security/verification owner rule identifying the exploited-vulnerability restriction and its effect; otherwise retain security-update advice without claiming the undocumented enforcement.

### [Operating System](http://127.0.0.1:4000/host/verification-stages#operating-system) — `CUR-4d045dd2542b936b`

**Status:** UNVALIDATED

**Literal source text:** SSH password login must be disabled for security. SSH password login enabled will fail verification. See [Disable SSH Password Login](/host/disable-ssh-password-login).

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host implementation source owner

**Next:** Bind an exact canonical source, authorized runtime observation, or accountable-owner decision before changing status.

### [Operating System](http://127.0.0.1:4000/host/verification-stages#operating-system) — `CUR-69ed2795fe11a780`

**Status:** UNVALIDATED

**Literal source text:** Use a separate SSH key pair for each machine you operate. One key reused across your fleet means a single compromise exposes every machine you host.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host implementation source owner

**Next:** Bind an exact canonical source, authorized runtime observation, or accountable-owner decision before changing status.

### [Reliability](http://127.0.0.1:4000/host/verification-stages#reliability) — `CUR-0425ac251168cd22`

**Status:** UNVALIDATED

**Literal source text:** Reliability starts low on a new machine and grows the longer the machine stays online. A stable machine typically reaches 90% within a few days.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host implementation source owner

**Next:** Bind an exact canonical source, authorized runtime observation, or accountable-owner decision before changing status.

### [Self-Test](http://127.0.0.1:4000/host/verification-stages#self-test) — `CUR-de92dc8e56f1205c`

**Status:** UNVALIDATED

**Literal source text:** You can check whether your machine is ready for verification by running a Self-Test. See [How to Self-Test](/host/how-to-self-test).

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host implementation source owner

**Next:** Bind an exact canonical source, authorized runtime observation, or accountable-owner decision before changing status.

### [Self-Test](http://127.0.0.1:4000/host/verification-stages#self-test) — `CUR-c9fb04361f13a554`

**Status:** UNVALIDATED

**Literal source text:** **Dedicated machines only.** Any personal workload, such as mining, gaming, running your own jobs, or using the machine as a desktop, will automatically fail verification.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host implementation source owner

**Next:** Bind an exact canonical source, authorized runtime observation, or accountable-owner decision before changing status.

### [Self-Test](http://127.0.0.1:4000/host/verification-stages#self-test) — `CUR-0a98c29bec96763b`

**Status:** UNVALIDATED

**Literal source text:** Meeting these minimum requirements makes your machine eligible for verification, but does not automatically guarantee verification. [Read more about verification](/host/understanding-verification).

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host implementation source owner

**Next:** Bind an exact canonical source, authorized runtime observation, or accountable-owner decision before changing status.

### [Self-Test](http://127.0.0.1:4000/host/verification-stages#self-test) — `CUR-185473e95045d9ae`

**Status:** UNVALIDATED

**Literal source text:** Meeting requirements makes the machine eligible. It does not guarantee immediate verification, search placement, or rentals.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host implementation source owner

**Next:** Bind an exact canonical source, authorized runtime observation, or accountable-owner decision before changing status.

### [Unverified](http://127.0.0.1:4000/host/verification-stages#unverified) — `CUR-e36681923da53b7c`

**Status:** UNVALIDATED

**Literal source text:** Unverified means the machine is new, under evaluation, or not currently meeting verification conditions.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host implementation source owner

**Next:** Bind an exact canonical source, authorized runtime observation, or accountable-owner decision before changing status.

### [Unverified](http://127.0.0.1:4000/host/verification-stages#unverified) — `CUR-6e3d0db9202f88f7`

**Status:** UNVALIDATED

**Literal source text:** - Fix driver, network, storage, and daemon errors.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host implementation source owner

**Next:** Bind an exact canonical source, authorized runtime observation, or accountable-owner decision before changing status.

### [Unverified](http://127.0.0.1:4000/host/verification-stages#unverified) — `CUR-c204e449470aaf92`

**Status:** UNVALIDATED

**Literal source text:** - Avoid background workloads outside the Jobs tab or `create job`.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host implementation source owner

**Next:** Bind an exact canonical source, authorized runtime observation, or accountable-owner decision before changing status.

### [Verified](http://127.0.0.1:4000/host/verification-stages#verified) — `CUR-aeb3f65db94f2b59`

**Status:** UNVALIDATED

**Literal source text:** Verified means the machine passed automated checks and currently meets platform standards.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host implementation source owner

**Next:** Bind an exact canonical source, authorized runtime observation, or accountable-owner decision before changing status.

### [Verified](http://127.0.0.1:4000/host/verification-stages#verified) — `CUR-1c1e2e9a916538c2`

**Status:** UNVALIDATED

**Literal source text:** - Avoiding hardware reductions after the machine is created.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host implementation source owner

**Next:** Bind an exact canonical source, authorized runtime observation, or accountable-owner decision before changing status.

### [Verified](http://127.0.0.1:4000/host/verification-stages#verified) — `CUR-a90cff1e4afa7e86`

**Status:** UNVALIDATED

**Literal source text:** - Responding quickly to red machine errors.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host implementation source owner

**Next:** Bind an exact canonical source, authorized runtime observation, or accountable-owner decision before changing status.

### [Deverified](http://127.0.0.1:4000/host/verification-stages#deverified) — `CUR-a63ed08c27be586c`

**Status:** UNVALIDATED

**Literal source text:** - Network instability, closed ports, or low bandwidth.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host implementation source owner

**Next:** Bind an exact canonical source, authorized runtime observation, or accountable-owner decision before changing status.

### [Deverified](http://127.0.0.1:4000/host/verification-stages#deverified) — `CUR-a2750f0751af855a`

**Status:** UNVALIDATED

**Literal source text:** - GPU, NVML, Xid, PCIe, power, thermal, or storage errors.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host implementation source owner

**Next:** Bind an exact canonical source, authorized runtime observation, or accountable-owner decision before changing status.

### [Deverified](http://127.0.0.1:4000/host/verification-stages#deverified) — `CUR-cf2eefcdd5cc64b6`

**Status:** UNVALIDATED

**Literal source text:** Fix the underlying issue and wait for automation to refresh state. Most machine error states clear only after the platform sees sustained healthy behavior.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host implementation source owner

**Next:** Bind an exact canonical source, authorized runtime observation, or accountable-owner decision before changing status.

### [Read Next](http://127.0.0.1:4000/host/verification-stages#read-next) — `CUR-19f4db0b224d0347`

**Status:** UNVALIDATED

**Literal source text:** | Direct ports | [Network & Ports](/host/network-ports) |

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host implementation source owner

**Next:** Bind an exact canonical source, authorized runtime observation, or accountable-owner decision before changing status.

## [Why Isn't My Machine in Search?](http://127.0.0.1:4000/host/not-in-search)

### [Listed and visible are different things](http://127.0.0.1:4000/host/not-in-search#listed-and-visible-are-different-things) — `MCL-86d19ded9c417bbf`

**Status:** UNVALIDATED

**Literal source text:** Separate "listed" from "visible in a normal broad search." Marketplace search is not a complete inventory dump. It limits result sets, ranks and groups similar offers, tries to avoid race conditions, and usually shows the best matches first. Search can be affected by ranking, grouping, filters, verification state, offer state, rental state, reliability, price, supply and demand, or machine errors.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Documentation technical-source reviewer

**Next:** Locate the exact canonical implementation/schema/configuration for this behavior and reuse applicable retained source/execution/UI evidence. Client dispatch or documentation alone cannot prove backend effects.

### [Check the machine directly](http://127.0.0.1:4000/host/not-in-search#check-the-machine-directly) — `MCL-8bc7e0b5a446da8e`

**Status:** UNVALIDATED

**Literal source text:** Start in the Machines page for the host account. Confirm that the machine is online, listed, has active offers, has no red machine errors, and is not currently rented in a way that hides the offer you expect to see. Also confirm required details such as direct ports, RAM, upload speed, and download speed are populated, and that reliability is above the relevant gate.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-8bc7e0b5a446da8e and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Check the machine directly](http://127.0.0.1:4000/host/not-in-search#check-the-machine-directly) — `MCL-6d7bd69f9ec1c562`

**Status:** UNVALIDATED

**Literal source text:** Confirm the CLI is authenticated to the same host-enabled account:

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Marketplace search and Host listing backend owner; Authorized Host/API operator

**Next:** The Marketplace search and Host listing backend owner supplies the exact repository, revision, path, and symbol/operation locator; bind it to MCL-6d7bd69f9ec1c562 and retain the focused source check. An authorized Host/API operator runs only an approved representative check for MCL-6d7bd69f9ec1c562 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Check the machine directly](http://127.0.0.1:4000/host/not-in-search#check-the-machine-directly) — `MCL-a34e22ce7cb35e93`

**Status:** UNVALIDATED

**Literal source text:** Then search directly by machine ID:

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-a34e22ce7cb35e93 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Check the machine directly](http://127.0.0.1:4000/host/not-in-search#check-the-machine-directly) — `MCL-56036fd86e83c011`

**Status:** UNVALIDATED

**Literal source text:** If you need to ignore the CLI's default search filters while troubleshooting, add `-n`:

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Marketplace search and Host listing backend owner; Authorized Host/API operator

**Next:** The Marketplace search and Host listing backend owner supplies the exact repository, revision, path, and symbol/operation locator; bind it to MCL-56036fd86e83c011 and retain the focused source check. An authorized Host/API operator runs only an approved representative check for MCL-56036fd86e83c011 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Check the machine directly](http://127.0.0.1:4000/host/not-in-search#check-the-machine-directly) — `MCL-48dc9f23a1a7555f`

**Status:** UNVALIDATED

**Literal source text:** You can also keep the normal command form but explicitly include the offer states that commonly hide a machine:

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Marketplace search and Host listing backend owner; Authorized Host/API operator

**Next:** The Marketplace search and Host listing backend owner supplies the exact repository, revision, path, and symbol/operation locator; bind it to MCL-48dc9f23a1a7555f and retain the focused source check. An authorized Host/API operator runs only an approved representative check for MCL-48dc9f23a1a7555f and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Check the machine directly](http://127.0.0.1:4000/host/not-in-search#check-the-machine-directly) — `MCL-704984284fa4cd00`

**Status:** UNVALIDATED

**Literal source text:** If the machine looks healthy there but is hard to find in marketplace search, narrow the search by GPU model, region, verification state, price range, and rentable/rented state. The machine can be listed correctly but still not appear in a broad search because other machines rank higher, similar offers are grouped, or your filters exclude it.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Documentation technical-source reviewer

**Next:** Locate the exact canonical implementation/schema/configuration for this behavior and reuse applicable retained source/execution/UI evidence. Client dispatch or documentation alone cannot prove backend effects.

### [Comparing your ranking](http://127.0.0.1:4000/host/not-in-search#comparing-your-ranking) — `MCL-d7643ee2685f24ec`

**Status:** UNVALIDATED

**Literal source text:** The default Auto Sort combines ranking factors with an element of randomness, so position varies between searches.

**Required proof:** Canonical Implementation Source

**Existing proof / limit:** [EVIDENCE-REUSE-MCL-d7643ee2685f24ec-1](evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/c-operations-verification/sources/context_not-in-search.mdx) — Exact retained selector; source/runtime boundary is stated in the passage review.

**Responsible role:** Documentation technical-source reviewer; implementation source owner only for an unavailable or unclear definition

**Next:** Resolve together with existing MCL-b106578dbaccc269: obtain the search owner’s current AutoSort definition or remove the unsupported randomness explanation. Treat both occurrences as one source follow-up topic.

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

## [Host Glossary](http://127.0.0.1:4000/host/glossary)

### [Auto Sort](http://127.0.0.1:4000/host/glossary#auto-sort) — `MCL-b106578dbaccc269`

**Status:** UNVALIDATED

**Literal source text:** The default marketplace search order. It uses ranking factors plus randomness, so position can vary. See [Not in Search](/host/not-in-search).

**Required proof:** Canonical Implementation Source

**Existing proof / limit:** [SOURCE-FAMILY-MCL-b106578dbaccc269-1](evidence/2026-09-15-host-unvalidated-source-families-attempt-01/s2-s3/cli-vastai_cli_commands_offers.py-25-35.txt) — Exact retained selector; source/runtime boundary is stated in the passage review.; [SOURCE-FAMILY-MCL-b106578dbaccc269-2](evidence/2026-09-15-host-unvalidated-source-families-attempt-01/s2-s3/context-review.json) — Exact retained selector; source/runtime boundary is stated in the passage review.

**Responsible role:** Documentation technical-source reviewer; implementation source owner only for an unavailable or unclear definition

**Next:** The checked CLI search ordering is not the console AutoSort algorithm. No retained owner definition or exact console implementation in this review establishes default selection, ranking inputs and randomness together. Obtain the AutoSort implementation/owner definition; a command search result is insufficient.

### [CGNAT](http://127.0.0.1:4000/host/glossary#cgnat) — `MCL-d992675b43bdcf7f`

**Status:** UNVALIDATED

**Literal source text:** Carrier-grade NAT. Your router does not have its own public IPv4 address, so inbound connections cannot reliably reach the host. Vast hosting requires a real public inbound TCP/UDP path; CGNAT and double NAT without public forwarding are not supported hosting setups. See [Network & Ports](/host/network-ports#cgnat-starlink-ipv6).

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-d992675b43bdcf7f and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Deverified](http://127.0.0.1:4000/host/glossary#deverified) — `MCL-541ce31c31e435bc`

**Status:** UNVALIDATED

**Literal source text:** A previously verified machine that no longer meets requirements. See [Verification Stages](/host/verification-stages).

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-541ce31c31e435bc and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Direct ports (direct_port_count)](http://127.0.0.1:4000/host/glossary#direct-ports-direct-port-count) — `MCL-51df0d3231b1cd10`

**Status:** UNVALIDATED

**Literal source text:** Externally reachable TCP/UDP ports forwarded to the host. Self-test requires at least 3 per listed GPU; production hosts should usually plan about 100 per listed GPU for headroom. See [Network & Ports](/host/network-ports#ports-per-gpu).

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-51df0d3231b1cd10 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Instance](http://127.0.0.1:4000/host/glossary#instance) — `MCL-77aaa70c71e8414a`

**Status:** UNVALIDATED

**Literal source text:** The renter workload running on your machine, usually a container or VM created from an offer.

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-77aaa70c71e8414a and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Interruptible rental](http://127.0.0.1:4000/host/glossary#interruptible-rental) — `MCL-73ed4f2f89d6a3d6`

**Status:** UNVALIDATED

**Literal source text:** Lower-priority bid rental. Higher bids run first; stopped containers and data remain on the machine. See [rental types](/guides/reference/faq/rental-types).

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-73ed4f2f89d6a3d6 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Machines tab](http://127.0.0.1:4000/host/glossary#machines-tab) — `MCL-38d3e256db801f2f`

**Status:** UNVALIDATED

**Literal source text:** The host console page for your machines. It appears after host account conversion. See [Account & Hosting Agreement](/host/account-hosting-agreement#host-features-tab).

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Documentation technical-source reviewer

**Next:** Inspect canonical account/team/auth/invoice/payout configuration and applicable retained console or API observation for the exact transition. Existing general docs are navigation to sources, not terminal proof.

### [Min GPU / min_chunk](http://127.0.0.1:4000/host/glossary#min-gpu-min-chunk) — `MCL-c67de49209260232`

**Status:** UNVALIDATED

**Literal source text:** The smallest GPU group a renter can select on a multi-GPU machine. See [Pricing Your Listing](/host/pricing-your-listing#listing-controls).

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Documentation technical-source reviewer

**Next:** Locate the exact canonical implementation/schema/configuration for this behavior and reuse applicable retained source/execution/UI evidence. Client dispatch or documentation alone cannot prove backend effects.

### [NAT hairpinning](http://127.0.0.1:4000/host/glossary#nat-hairpinning) — `MCL-7c397c27baa76270`

**Status:** UNVALIDATED

**Literal source text:** Router behavior that makes same-LAN public-IP port tests unreliable. Test from outside the LAN. See [Network & Ports](/host/network-ports#test-ports-outside-lan).

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-7c397c27baa76270 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Offer](http://127.0.0.1:4000/host/glossary#offer) — `MCL-38c7d83d897eb05c`

**Status:** UNVALIDATED

**Literal source text:** A listing renters can accept, including price, offer end date, minimum GPU chunk, and other terms. See [Hosting Overview](/host/hosting-overview).

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Documentation technical-source reviewer

**Next:** Locate the exact canonical implementation/schema/configuration for this behavior and reuse applicable retained source/execution/UI evidence. Client dispatch or documentation alone cannot prove backend effects.

### [On-demand rental](http://127.0.0.1:4000/host/glossary#on-demand-rental) — `MCL-89c022e1c11da0a9`

**Status:** UNVALIDATED

**Literal source text:** Standard highest-priority rental at the listed price. See [rental types](/guides/reference/faq/rental-types).

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Documentation technical-source reviewer

**Next:** Locate the exact canonical implementation/schema/configuration for this behavior and reuse applicable retained source/execution/UI evidence. Client dispatch or documentation alone cannot prove backend effects.

### [Reliability](http://127.0.0.1:4000/host/glossary#reliability) — `MCL-f71bf6315902fcf9`

**Status:** UNVALIDATED

**Literal source text:** Vast's stability score for a machine. Reliability greater than 0.9 is an eligibility gate. See [Reliability & Uptime](/host/reliability-uptime).

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-f71bf6315902fcf9 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Reserved rental](http://127.0.0.1:4000/host/glossary#reserved-rental) — `MCL-02d20673fc531b05`

**Status:** UNVALIDATED

**Literal source text:** Longer-term prepaid rental at a host-controlled discount. See [Pricing Your Listing](/host/pricing-your-listing#listing-controls).

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Documentation technical-source reviewer

**Next:** Locate the exact canonical implementation/schema/configuration for this behavior and reuse applicable retained source/execution/UI evidence. Client dispatch or documentation alone cannot prove backend effects.

### [Self-test](http://127.0.0.1:4000/host/glossary#self-test) — `MCL-1398154162e4eeda`

**Status:** UNVALIDATED

**Literal source text:** CLI diagnostic that checks requirements, rents a temporary instance, runs runtime tests, reports results, and cleans up. See [How to Self-Test](/host/how-to-self-test).

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host Product and Documentation content owner; Authorized Host/API operator

**Next:** The Host Product and Documentation content owner supplies the exact repository, revision, path, and symbol/operation locator; bind it to MCL-1398154162e4eeda and retain the focused source check. An authorized Host/API operator runs only an approved representative check for MCL-1398154162e4eeda and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Unlist vs. delete](http://127.0.0.1:4000/host/glossary#unlist-vs-delete) — `MCL-70ff89543d4f4eea`

**Status:** UNVALIDATED

**Literal source text:** Unlisting stops new rentals. Deleting removes the machine record. Existing commitments must be understood first. See [Remove or Recreate](/host/removing-recreating-machines).

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-70ff89543d4f4eea and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Verification / verified](http://127.0.0.1:4000/host/glossary#verification-verified) — `MCL-78770a59873b66e2`

**Status:** UNVALIDATED

**Literal source text:** Automated status indicating a machine meets platform standards. See [Verification Stages](/host/verification-stages).

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-78770a59873b66e2 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [vericode](http://127.0.0.1:4000/host/glossary#vericode) — `MCL-6d3078c053d4ad1d`

**Status:** UNVALIDATED

**Literal source text:** `vericode=8` means the platform has a host-facing machine `error_msg`. `Port Networking Issues` is one common `vericode=8` message, but the same bit can also appear for other machine errors such as Docker/NVIDIA runtime, CDI, PCIe, or daemon errors.

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host Product and Documentation content owner; Authorized Host/API operator

**Next:** The Host Product and Documentation content owner supplies the exact repository, revision, path, and symbol/operation locator; bind it to MCL-6d3078c053d4ad1d and retain the focused source check. An authorized Host/API operator runs only an approved representative check for MCL-6d3078c053d4ad1d and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [vericode](http://127.0.0.1:4000/host/glossary#vericode) — `MCL-92becfba53d0bd15`

**Status:** UNVALIDATED

**Literal source text:** Use the exact console message when choosing a fix. For `Port Networking Issues`, common causes include closed external ports, forwarding to the wrong LAN IP, CGNAT or double NAT without a real public forwarding path, no inbound public IP, host firewall rules, TCP/UDP mismatch, or stale port range. See [Self-Test Reference: vericode=8](/host/self-test-reference#vericode-8), [Machine Error Reference](/host/machine-errors), and [Network & Ports](/host/network-ports).

**Required proof:** Canonical Implementation Source, Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Host Product and Documentation content owner; Authorized Host/API operator

**Next:** The Host Product and Documentation content owner supplies the exact repository, revision, path, and symbol/operation locator; bind it to MCL-92becfba53d0bd15 and retain the focused source check. An authorized Host/API operator runs only an approved representative check for MCL-92becfba53d0bd15 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

### [Volume offer](http://127.0.0.1:4000/host/glossary#volume-offer) — `MCL-9d2fe906a3395548`

**Status:** UNVALIDATED

**Literal source text:** A storage-only offer on a machine. Rented volume space reduces disk available to GPU offers. See [Hosting Overview](/host/hosting-overview#volume-offers).

**Required proof:** Runtime Or Ui Observation

**Existing proof / limit:** No retained proof

**Responsible role:** Authorized Host/API operator

**Next:** An authorized Host/API operator runs only an approved representative check for MCL-9d2fe906a3395548 and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence.

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
