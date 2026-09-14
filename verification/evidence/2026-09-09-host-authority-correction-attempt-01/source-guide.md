# What these sources establish

This is a guide to independent source evidence, not product evidence by itself.
The exact reviewed page wording and original finding are recorded in the
[candidate inventory](candidate-inventory-01.json).

## Listing controls

The [pinned Vast CLI source](cli-listing-source-01.json) was fetched from the
public Vast repository and compared byte-for-byte with the inspected checkout.
It declares the controls below and maps them into the listing API request.

| Documentation concept | CLI option | API request field | Evidence limit |
| --- | --- | --- | --- |
| Minimum GPUs per rental | `--min_chunk` | `min_chunk` | Exposed setting; observed minimum1. Not a test rejecting a smaller rental. `min_gpu` is not this CLI option. |
| Interruptible minimum bid | `--price_min_bid` | `price_min_bid` | Exposed minimum-bid field; observed0.30. Not a low-bid enforcement test. |
| Maximum prepaid discount | `--discount_rate` | `credit_discount_max` | Exposed discount field; observed0.0. Not a nonzero-discount calculation. |
| Offer end date | `--end_date` | `end_date` | Exposed expiry field; observed stored date. Not an expiry or existing-contract guarantee. |

The earlier successful listing request and independent Host readback are retained
in [the listing readback check](../2026-09-09-h100x4-listing-rental-attempt-02/rate-001/listing-readback-verification-01.json).
This correction reuses that dated observation; it does not run another listing.

## Host responsibilities

The source is the actual [Standard Hosting Agreement](https://cloud.vast.ai/host/agreement),
not the Host Docs summary. The [public rendered capture](agreement-source-01.json)
retains the exact relevant sections and their hashes, observed9September2026.
The public rendering did not expose a version label or section-anchor IDs;
citations therefore name the actual headings instead of inventing fragment URLs.

| Agreement section | Supported subject | Important limit |
| --- | --- | --- |
| Performance of Services | Provider responsibility for running, troubleshooting and maintaining hardware; limits on Vast setup technical assistance. | Does not establish Discord availability or individual installation procedures. |
| Operation and Maintenance | Maintenance duties and timing; qualified best-efforts availability; prohibition on reviewing or retaining renter data. | Not an absolute uptime guarantee, rental-term immutability rule, or permission to inspect renter data through an unspecified support exception. |
| Intellectual Property and Data Security | Supporting technology responsibilities and reasonable security safeguards. | Not proof that a particular host is secure or that a technical isolation mechanism works. |

A clause can support multiple matching documentation occurrences. Each occurrence
still needs its own source binding and scope comparison. No new owner approval
is implied. Mixed statements retain any unsupported remainder explicitly.

## Still separate

These sources do not establish multiple concurrent independent rental contracts,
all terms being permanently locked, all allowed pricing values, stock-installer
success, or a complete self-test. Those existing findings remain separately
reviewable; they must not inherit a PASS from these controls or agreement clauses.
