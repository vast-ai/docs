# Host-team CLI static catalog attempt 01

> **Portability amendment (2026-09-03; clarified 2026-09-04):** The original
> committed record is preserved as Git blob
> `522f72c64841ed896892a6aa991985fe36b218f2`. This amendment removes the
> workstation-local working-table dependency and reproduces its 17-carrier
> scope below. It does not change the attempt's target, observation, status, or
> limitations.

- Attempt ID: `ATTEMPT-2026-09-01-HOST-TEAM-CATALOG-01`
- Evidence ID: `EV-TEAM-C01-CATALOG-01`
- Scope: `TS-TEAM-C01` static catalog conformance only; branch `TEAM-C01-B01`; step `TEAM-C01-B01-S01`.

## Bound targets

- Current documentation revision/tree: `14d9af21fe8a6df205180d6f211415bf750ee4b8` / `2eded9e87079a3cb2517ee7a7448018c388b122b`.
- Canonical test-set raw snapshot SHA-256: `50b010956942a3294ea12cbc3936330fbad2be932948a9b4b3e747c8c72c051a` (`verification/host-docs-test-sets.json`).
- Current Host-team page: `host/host-teams.mdx`; SHA-256 `a056c762d6fbf968e1972a129d1abb45154bfb52b537a35d0240d5b1d0c330ee`.
- Current CLI revision/tree: `18c4f2ccd6da587d5352f8741c71805a9a18e1ae` / `46530a7c5ff62345109d6a2cd04d048bc9466533`.
- Historical working-table SHA-256: `3fd5bc8995a319898376ece975b5d82680f2781a25ae55bad76a040aaaf44484`. The tracked result below is self-contained; no ignored or workstation-local report is required.

The canonical test-set artifact declares an earlier source revision/tree. Its raw snapshot hash is recorded above for joinability; this attempt's static observations are bound separately to the current documentation revision/tree and page hash and do not retroactively rewrite that declaration.

## Method and observation

The complete 17-carrier `NON_EXECUTABLE_DISPLAY` catalog was inspected by resolving each linked in-repository documentation target and inspecting the current CLI console-entrypoint parser/help contract. All 17 help inspections returned exit `0`, produced nonempty help, and produced no stderr. No catalog operation was run; no authentication, credentials, network/API request, Host interaction, or mutation occurred.

The 17 exact carrier IDs are:

`CLM-1b189d051c9468e5`, `CLM-1cb07ec233c461b2`,
`CLM-38257bb7c2529187`, `CLM-40b2f1682f7e1b79`,
`CLM-46d0c5ce2153a004`, `CLM-4f08d5cc9817690b`,
`CLM-5f1ad892e6c8e34c`, `CLM-6a6993c68a1f04e4`,
`CLM-923d7604e486acd4`, `CLM-961b4271992ad45f`,
`CLM-965828ea630d32ff`, `CLM-b10173dc22deecd2`,
`CLM-bb31da6105c31a7c`, `CLM-c6370bac1c24cf5d`,
`CLM-da373c4653a28e82`, `CLM-e6bffefe839b663c`, and
`CLM-fa287335656da956`.

## Disposition

| Claim population | Method | Coverage | Disposition |
| --- | --- | ---: | --- |
| Static carrier catalog-validation claims | `STATIC_SOURCE` | 17/17 | `PASS` |
| `TEAM-C01-B01-S01` | `STATIC_SOURCE` | 17/17 carriers | `PASS` |
| `TEAM-C01-B01` | `STATIC_SOURCE` | 1/1 step | `PASS` |
| `TS-TEAM-C01` | `STATIC_SOURCE` | 1/1 branch | `PASS` |

Every one of the 17 carrier claims retains semantic score `2`: relevant but partial static semantic support. The PASS outcomes establish only that the documented catalog paths are linked and accepted by the current console-entrypoint help contract.

## Explicit runtime exclusion

Runtime account/team authorization, role permissions, billing visibility, mutation behavior, result shape, cleanup, and external API behavior are `UNVALIDATED` for all 17 catalog operations. This static evidence must not be used as proof of any live command outcome.
