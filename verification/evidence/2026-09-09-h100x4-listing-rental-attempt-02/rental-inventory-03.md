# Corrected final-search offer binding — before creation

Two pre-create guards stopped safely without issuing any create request.
The earlier source-independent expected id was50363390; diagnostic search
returned50363393; the next retained fresh quote returned50363390 again, with
the same machine150296, oneGPU, is_bid=false and unchanged pricing/expiry.
The record does not establish why the service selected different ids.

Correction: do not require an offer id from a different, earlier search.
The runner selects exactly one matching row from its own final search, retains
that row and its id, then uses that exact id in the ensuing create request.
Machine150296, oneGPU, rentable=true, rented=false, is_bid=false, current
client quote<=4.10/hour and<=0.014/GB each direction, and fixed expiry remain
hard predicates. Zero or multiple matching rows stop creation. This fixes the
test expectation, not the product, and does not permit another machine/rate.

All remaining rental-inventory-01.md safeguards and cost limitations persist.
Use label host-docs-vv-150296-20260909-attempt02-run03 and append all records
under rental-run-03/. Earlier failures and frozen inventories are preserved.
The exact body/offer/image/program remains retained BEFORE dispatch of PUT.
