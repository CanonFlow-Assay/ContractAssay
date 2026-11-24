# Active Git worktree summary

Historical audit of `feat/common-denominator-playground` on 2026-11-24.
The observations below record the pre-overhaul revisions.
The branch adds wrappers and documentation across ten repositories. Each
verifier result below applies to its recorded producer, inputs and policy.

## Findings

| Claim in the previous summary | What the evidence establishes |
| --- | --- |
| 21 of 21 engines comply with the common denominator. | `assay_estate_audit.py` searches Markdown for `Pass`, `Fail` and `Inconclusive`. The `allFourStateCompliant` flag can be true with no `ToolFailure` mention and zero CLI executions. Twelve rows contain all seven verb strings counted by the script. |
| 23 of 23 playgrounds are qualified. | `run_all_playgrounds.py` emits an estate `Pass` when every row has a file. The receipt counts ten accepted wrapper outputs. The other thirteen rows use `VerifiedInDedicatedSuite`, a fallback also used after failed invocations. CSharpAssay borrows the separate Playground's file count. Counts can include ignored build output. |
| The ten new wrappers passed their showcases. | All ten wrappers returned `Pass`/`0`. Direct verification of the nine engine examples returned five `Pass`/`0` and four `Inconclusive`/`2`. Dart's wrapper counts files. The pinned Flutter script returned `Fail` on lock drift, then `Inconclusive` after successful local checks with the exact dependency cached. |
| Every playground implements one CLI, schema, exit table and rule matrix. | `ASSAY-COMMON-v1` describes a convergence target. The observed receipts use producer-specific schemas and commands. For example, FsAssay uses `check` and `verify` and writes `fsassay-authority-receipt/1.1.0`. Dart M1 uses its Flutter qualification script. |

Three controls reproduced the gaps. A README containing the three outcome
words and a one-file playground yielded both estate success flags with zero
wrapper executions. An unchanged copy of Dart's wrapper returned `Pass`/`0`
with zero app and test files. In a disposable Bash checkout, a required
command exited `7`. Direct `verify` returned an authoritative `Fail`/`1`,
and the wrapper still returned `Pass`/`0` with the `Fail` in its showcase field.
The Bash source and the wrapper were held at the audited revision, and the
failing behavior was introduced in the disposable example test.

The estate runner also selects the Rust, Python and Kotlin wrappers. These
require `--output`. Invoked with the estate runner's arguments, each exits
`2` at argument parsing and falls through to `VerifiedInDedicatedSuite`.

## Git topology

The estate records cover 23 distinct Git repositories, including the two
standalone .NET playgrounds. `CanonFlow-Assay` is their parent directory.
`FSharpAssay-Refresh` is a linked worktree of `FSharpAssay` at `f979b8a` on
`feat/csharp-parity-refresh`. The estate's `skills/` folder is a directory.

The table records Git refs and checkout state before these documentation edits.
All 23 primary checkouts were on `main` with clean Git status. All 17 listed
feature worktrees were registered and clean. Ten worktrees were ahead of
`main` by 11 commits in total. Seven pointed to the same commits as `main`.
The feature worktree path for each row is
`~/.local/state/canonflow/assay-worktrees/<repository>`.

| Repository | Primary `main` | Feature `HEAD` | Feature-only commits |
| --- | --- | --- | ---: |
| BashAssay | `d180824` | `376dd7a` | 1 |
| ContractAssay | `a495a87` | `29c1ff7` | 1 |
| CSharpAssay | `4fec9e9` | `4fec9e9` | 0 |
| DartAssay | `527cb8c` | `0672084` | 2 |
| DhallAssay | `5c2a966` | `3b35387` | 1 |
| DuckDBAssay | `afb2a57` | `2496a9e` | 1 |
| GitHubActionsAssay | `e84c6c7` | `d694199` | 1 |
| JavaScriptAssay | `b719eb9` | `b719eb9` | 0 |
| KotlinAssay | `a9d4de7` | `a9d4de7` | 0 |
| OpenSearchAssay | `ee66ebc` | `53fdebd` | 1 |
| OracleAssay | `ff65b2a` | `d19068c` | 1 |
| PostgresAssay | `1574c67` | `30ff3c5` | 1 |
| PowerShellAssay | `28c464e` | `456abf5` | 1 |
| PythonAssay | `6cf8add` | `6cf8add` | 0 |
| RustAssay | `2fa855d` | `2fa855d` | 0 |
| SwiftAssay | `9b3fa61` | `9b3fa61` | 0 |
| TypeScriptAssay | `e046dd7` | `e046dd7` | 0 |

The nine single-commit deltas add `playground/run.py` and its README.
Dart adds those files and `CONTRACT.md` over two commits. Full commit and
tree IDs, changes and worktree registrations are in `inventory-before.json`.

## Direct results on the feature branch

For the nine Python wrappers, each `scan` returned `Inconclusive`/`2` and
every returned catalogue ID had a successful `explain` invocation. The
catalogue counts and the unit test counts measure different things. The
wrapper uses its unit-suite result, successful `explain` exits and the
single `scan` control to compute its top-level verdict. Its `doctor` result
and the showcase `verify` verdict are outside that calculation.

| Repository | Catalogue IDs | Source unit tests | Direct `verify` on the wrapper's input |
| --- | ---: | --- | --- |
| BashAssay | 9 | 19 passed | `Pass`/`0`. Bash 5.2.21 and ShellCheck 0.11.0 inspected the sample and its behavior command passed. |
| ContractAssay | 6 | 8 passed | `Pass`/`0`. The ONDC policy evaluated the checked-in positive and rejected JSON specimens. |
| DhallAssay | 5 | 17 passed | `Pass`/`0`. Dhall 1.42.2 inspected the sample configuration and its behavior command passed. |
| DuckDBAssay | 14 | 43 passed, 2 skipped | `Inconclusive`/`2`. The checked-in 2.0.0 snapshot policy specifies no required behavior commands. |
| GitHubActionsAssay | 8 | 10 passed | `Inconclusive`/`2`. The run `44739374322` plan lacks its run, attempt, workflow, log and archive inputs in this checkout. |
| OpenSearchAssay | 11 | 42 passed | `Inconclusive`/`2`. The checked-in 3.9.0 snapshot policy specifies no required behavior commands. |
| OracleAssay | 8 | 6 passed | `Pass`/`0`. The verifier checked the supplied Oracle 23 capture and recovery evidence. |
| PostgresAssay | 18 | 45 passed | `Inconclusive`/`2`. The checked-in 18.7 snapshot policy specifies no required behavior commands. |
| PowerShellAssay | 6 | 18 passed | `Pass`/`0`. PowerShell 7.7.0 inspected the sample worker and its behavior command passed. |

Additional qualification used clean copies at those same feature commits.

- The Bash, Dhall and PowerShell qualifiers passed their native source and
  independent archive checks. Contract, GitHub Actions and Oracle passed
  source and independent archive suites. The Contract Inventory policy
  separately returned `Pass` on its retained capture. The Oracle 19c policy
  returned `Inconclusive`/`2` against the supplied 23-series observations.
- The separate `--native` lane passed eleven DuckDB smoke probes and
  produced a `Pass` snapshot assessment with its generated policy. The
  two skipped source tests are for array-valued rules. PostgreSQL and
  OpenSearch passed eight and seven disposable engine probes respectively.
  Their qualifiers exited `0` after observing the expected native
  snapshot `Fail`/`1` results on the deliberately restricted test servers.
  The raw receipts also preserve missing evidence for those snapshots.
- Dart's first exact-SDK run stopped before analysis or tests after offline
  resolution replaced locked `vector_math` 2.4.0 with cached 2.4.4. The
  original lockfile was restored byte for byte. In a clean copy with
  the hash-matched 2.4.0 package cached, the lock stayed intact and
  formatting, analysis, 20 domain/application/widget tests and the layout
  check completed. Device integration, Android debug and iOS no-codesign
  stayed `Inconclusive`. Both exits and their evidence are retained.

## Checks on the other estate rows

| Repository and audited commit | Fresh local evidence |
| --- | --- |
| CSharpAssay `4fec9e9` | Locked restore, Release build and 290 tests passed with .NET SDK 11.0.100. |
| CSharpAssay.Playground `0218642` | Locked restore, build and 72 primary tests passed. The engine at `4fec9e9` returned authoritative `pass`/`0` for `Playground.Refined.slnx`. Both impure and upstream controls returned the expected `fail`/`1` with authority gaps retained. |
| FSharpAssay `03d031a` | Locked restore and build passed. The separate stable suite passed 123 tests. FsAssay `check` was `Inconclusive`/`2` because required tests were `notRun`. FsAssay `verify` was `Pass`/`0`, authoritative for four loaded projects, 36 files and 123 registered test passes. |
| FSharpAssay.Playground `312b84d` | The pinned producer qualified 38 active projects with a disposable PostgreSQL 18.7 fixture. FsAssay `verify` was `Pass`/`0` with 179 registered test passes. `check` and the standalone file lane both returned `Inconclusive`/`2`. The source inventory records 69 of 94 tracked F# paths analyzed across both lanes. |
| HTML5Assay `0e6a45b` | Six dependency-free playground preview tests passed. The browser and packaged engine lanes were outside this run. |
| JavaScriptAssay `b719eb9` | 60 unit tests passed on Node 26.13.1 and the reservation playground completed its five cases with one survivor. |
| KotlinAssay `a9d4de7` | ExpenseGuard returned `ToolFailure`/`3` because the configured Kotlin distribution lacked `bin/kapt` at the locked path. |
| PythonAssay `6cf8add` | 11 engine unit tests passed. ExpenseGuard completed its experiment on Python 3.12.3 and returned `Inconclusive`/`2` without the 3.14.7 pin. |
| RustAssay `2fa855d` | 17 engine tests passed on explicit Rust 1.98.1. The ExpenseGuard wrapper selected a different `stable` compiler and returned `Inconclusive`/`2`. |
| SecurityAssay `bc9f0aa` | Locked restore, Release build and 132 tests passed. These are source suite results. |
| STEAssay `c42a28f` | 73 tests passed on Node 20.20.2 and npm 10.8.2. The result covers the checked-in writing policy, preview and evidence tests. |
| SwiftAssay `9b3fa61` | ExpenseGuard returned `ToolFailure`/`3` with `swiftc` unavailable. |
| TypeScriptAssay `e046dd7` | 46 tests passed on Node 20.20.2 and npm 10.8.2. The reservation playground completed its five cases with one survivor on the pinned runtime. |

Both F# policies admitted zero blocking and zero advisory rules. Their
positive authority results cover the recorded project and test obligations.
The separate F# wallet mutation run killed four candidates with the
expanded suite, kept one wording survivor and rejected one invalid source
candidate at compile time. The active solution, standalone files and
mutation experiment each have their own retained evidence.

## Evidence

Raw receipts, command arguments, working directories, exits, logs, observed
tool versions and hashes are retained in the reviewer's local audit archive.

- `inventory-before.json` and `inventory-after.json` identify the source
  revisions and the documentation changes. `manifest.json` indexes the
  raw evidence by SHA-256.
- For the Python wrappers, `<repository>/harness.stdout` contains the
  wrapper JSON and `<repository>/verify.stdout` contains the direct
  verifier JSON. Look under `qualification-sources/` for archive and
  native-smoke evidence, and under `controls/` for the counterexamples.
- `FSharpAssay/` retains the built runner identity and the `check` and
  `verify` receipts. The packaged playground's producer pin,
  qualification, TRX and coverage are under `FSharpAssay.Playground/`.
- `DartAssay/` retains the original and changed lock bytes, the failed
  invocation, the retry input hashes and the successful local test logs.
- The historical `estate-common-denominator-receipt.json` has SHA-256
  `b370d5c00e2214f8fa24b350956b1fbed2fd8109bab6193178dd3b9ac6cb25e6`.
  The historical `playground-estate-receipt.json` has SHA-256
  `e80f9cf7d7191f1bb3dbba8d4448e3c22f4e363e58b1e05037a656f370800bd6`.
  These identify the original inventory bytes.

Board status, CI status on other revisions, package publication and release
readiness require their own evidence.

## Replaying the repaired estate checks

The current coordinator uses the checked-in command plan. Open the plan to see
the scope of each row. Use a fresh evidence directory outside the checkouts and
put the required pinned toolchains on `PATH` before running the selected rows.

```sh
python3 eng/estate/audit.py inventory --estate /path/to/Assay \
  --worktrees /path/to/worktrees --output /path/to/evidence/inventory
python3 eng/estate/audit.py run --estate /path/to/Assay \
  --worktrees /path/to/worktrees --output /path/to/evidence/bash \
  --repository BashAssay
```

For DuckDB native qualification, invoke the coordinator with the interpreter
that has the pinned native wheel installed. For GitHub Actions, set
`ASSAY_GITHUB_ACTIONS_POLICY` to the reviewed assembled attempt policy.

The inventory only records Git checkout identity. A run records the plan hash,
observed source, exact subprocesses, and hashes of retained output. Missing,
failed, contradictory and interrupted evidence stays visible. A Pass covers
the selected checks and command scopes. The output may contain private logs,
so retain it outside source control.

Check the shared Python wrapper template with
`python3 eng/estate/generate_playgrounds.py --worktrees /path/to/worktrees`.
Run the coordinator controls with `python3 eng/estate/test_audit.py`.
