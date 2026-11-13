# Proof Ledger

An offline Python desktop notebook for grid deductions. Propose a verdict only when it follows from the published evidence. Every proved identity opens a new truthful statement. Hint and automatic deduction use the same public-only proof rules.

The interface uses a light card matrix, an investigation library, and Evidence / Chronology / Analysis tabs. Every card shows its name, profession and face-up/down state; only published cards expose their statements. It includes six original investigations, two each at 3×3, 4×4 and 5×5. No reference portraits, source files, branding or puzzle prose are bundled. See [NOTICE.md](NOTICE.md) for reference credit and unknown original license status.

The course PDF has now been audited: see [requirements audit](docs/COURSE_REQUIREMENTS.md) and the detailed [Vietnamese report outline and demo script](docs/REPORT_OUTLINE_VI.md). The outline is not a completed Report.pdf or an uploaded demonstration video.

## Setup and launch

Python 3.11+ with Tkinter is required. There are no third-party runtime dependencies. On Linux, install your distribution's Python Tk package if it is missing. On Windows, include Tcl/Tk when installing Python.

Run these commands from the repository root:

```powershell
python main.py
```

This direct entry needs no package installation. For an editable development environment:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"
.venv\Scripts\python -m proofledger
```

On macOS/Linux, use `.venv/bin/python` in place of `.venv\Scripts\python`. Alternatively, launch directly from source without installing dependencies:

```powershell
$env:PYTHONPATH = "src"
python -m proofledger
```

For POSIX shells: `PYTHONPATH=src python -m proofledger`. The installed desktop shortcut is `proof-ledger`.

## Play

Choose an investigation in the library and press **Begin selected**, or open a compatible JSON file. Hands-on mode lets you select unresolved coordinates and propose a criminal or innocent verdict. Observe mode allows inspection of published identities while automation performs deductions.

- **Hint / H** selects the first provable unresolved identity without revealing its statement.
- **Auto Solve / A** starts or pauses one deduction at a time. It stops when complete or when no verdict is forced.
- **Restart / R** restores starting evidence and clears the deduction history.
- **Escape** pauses automation and opens the library. Arrow keys move board focus; Enter selects; Tab traverses controls.
- Select a published identity to read its full statement and highlight its references. Reference buttons focus a coordinate without replacing the statement being inspected.

The outline marks selection in indigo and references in ochre. Text and symbols distinguish criminal (◆), innocent (○), and unresolved (—), independently of color. The library collapses on smaller windows and the board/notebook scroll vertically. Verdict controls, automation controls and result messages stay visible in a fixed footer. Minimum window size is 640×600. No progress is saved after closing or changing investigations.

An undecided proposal, a proposal opposed by the evidence, and inconsistent evidence produce distinct messages. None reveals a statement. The app does not infer a verdict merely because it matches the supplied solution.

## Test and package

```powershell
python -m compileall -q src
python -m ruff check src tests
python -m unittest discover -s tests -v
python -m build --wheel
```

Use the activated virtual environment or its full Python path. Ruff and build are development extras. GUI integration tests instantiate Tk windows and need a graphical desktop; on headless Linux use a virtual display such as Xvfb. Tests are not silently skipped if Tk is unavailable. Other test modules run without a display, for example `python -m unittest discover -s tests -p test_sat_oracle.py -v`.

Tests derive from [SPEC.md](docs/SPEC.md), with exhaustive truth tables as an independent SAT/clue oracle, generated CNFs, lifecycle/worker tests, desktop geometry checks, and complete sample solves. The reference project and its tests are never imported. See [PARITY.md](docs/PARITY.md) for the actual final verification results and limitations.

## Batch experiments

```powershell
python -m proofledger.reports --output output --timeout 30
python -m proofledger.reports --puzzles path/to/json-cases --output output/custom --timeout 30
```

Each file is validated and solved independently in a process, for both optimization settings, with the same timeout and input set. Exit 0 means all runs solved; exit 1 means reports were written with at least one STALLED, INVALID, ERROR or TIMEOUT row. Exit 2 means command-level configuration failed, such as an empty directory or a nonpositive/nonfinite timeout. Duplicate puzzle IDs in different files remain separate rows/traces, identified by source_file. The command overwrites three files:

| File | Content |
|---|---|
| experiments.csv | Per-case dimensions, CNF size, classification counters, progress, all-clue uniqueness and duration |
| deduction_traces.json | Accepted steps, pre-move public clue IDs, actual SAT assumptions/results, cell/verdict and newly opened clue ID/content |
| pure_literal_ablation.csv | Deterministic solver counters and times with pure-literal elimination off/on |

CSV retains the original metric columns and adds status/error/source_file; ablation adds each mode's status/error. Clause counts, auxiliary variables and branching counters differ because the implementation and encodings differ. Classification counters include each pre-move analysis and a terminal stalled analysis; uniqueness queries are excluded. No redundant post-completion analysis is counted. Runtime includes initial analysis and all deduction work, but excludes input validation, full-evidence encoding/uniqueness, process startup and file output. The worker timeout covers its entire run, including validation and final uniqueness; startup/termination overhead can exceed the configured duration. GUI Analysis reports the current snapshot's counters and **current public** uniqueness; batch uniqueness uses **all clues without solution facts**. Timings are machine-dependent. Counters unavailable after a timeout remain blank rather than fabricated as zero.

Reproduce explicit failure cases and a deliberately tiny timeout:

```powershell
python -m proofledger.reports --puzzles examples/diagnostics --output output/diagnostics --timeout 30
python -m proofledger.reports --output output/timeout_probe --timeout 0.001
```

Both intentionally return exit 1 while preserving all result rows. The timeout probe tests the timeout mechanism, not normal puzzle performance.

## Puzzle files

UTF-8 JSON root fields: `id`, `title`, `size`, `characters`, `solution`, `clues`, `initially_revealed`; `description` is optional. See `src/proofledger/samples/01_3x3.json` for an original complete example.

- `size`: integer 3, 4 or 5. Coordinates run A1 through the appropriate last column/row, in row-major order.
- `characters`: exactly one `{cell, name, profession}` record per coordinate. Names must be alphabetically ordered over row-major coordinates, as the assignment requires. Identities have no logical meaning.
- `solution`: coordinate-to-`CRIMINAL`/`INNOCENT` mapping.
- `clues`: one object per owner coordinate with `type`, `data`, optional unique `id`, optional `text`. Missing IDs are generated from the owner. Text is presentation only; structured data defines truth.
- `initially_revealed`: unique coordinates whose **status and statement** both start public; an empty list is allowed, as is a completely revealed board.

| Clue | Data |
|---|---|
| FACT | `cell`, binary `status` |
| SAME / DIFFERENT / IMPLIES | distinct coordinates `a`, `b`; implication means criminal(a) implies criminal(b) |
| EXACTLY / AT_LEAST / AT_MOST | `region`, integer `k` between zero and region size |
| PARITY | `region`, `parity` = EVEN or ODD |

Region objects use `kind`: ROW with one-based integer `index`; COLUMN with letter `index`; NEIGHBORS with center `cell` (diagonals included, center excluded); EXPLICIT with unique `cells`; CORNERS; or BOUNDARY. Regions must be nonempty. Clue kinds, region kinds, parity, region coordinates and starting coordinates normalize case; binary/FACT coordinates use canonical uppercase. All clues must be true under the supplied solution. The complete clue set must determine exactly one primary board assignment. Progressive solvability is not mandatory: a globally unique puzzle can still stall with insufficient starting evidence.

The approved loader intentionally rejects duplicate records/JSON keys/reveals, fractional counts/dimensions, UNKNOWN solution or FACT statuses, and unsupported board dimensions. Invalid files produce recoverable desktop errors rather than crashing the case catalog.

## Architecture

The source separates three responsibility domains across small, dependency-focused packages:

```text
src/proofledger/
  contracts/                        # immutable values and public snapshots
  cases/                            # loader, validation, catalog and private Vault
  investigation/                    # verdicts, revisions, journal and Auto Solve
  reasoning/                        # regions, evaluator, CNF, DPLL and inference
  reports/                          # headless experiments and CSV/JSON exports
  desktop/
    shell.py, library.py            # application, navigation and Load
    workspace.py, board.py          # controls and visible cards
    notebook.py, guidance.py        # evidence, history, metrics and help
    appearance.py, tasks.py         # styling and background worker lifecycle
  samples/                          # six original JSON puzzles
  launch.py, __main__.py            # thin entry points
```

The `logic_game` domain consists of `contracts`, `cases`, `investigation`, and `samples`; it owns the complete puzzle and authorized reveal state. The solver domain consists of `reasoning` and `reports`. The UI domain is `desktop` plus the thin entry points. Algorithms in `reasoning` import only public `contracts`; they receive a `PublicSnapshot` and cannot import the private vault, loader, coordinator, or desktop. `reports` composes the engine and solver without loading Tkinter. See the [architecture diagrams](docs/ARCHITECTURE.md) for dependency and deduction-flow views.

The CNF encoder also validates clues and known verdicts when called directly without JSON loading. Invalid FACT targets, counts, relation endpoints and coordinates raise errors instead of becoming evidence.

The worker receives only a `PublicSnapshot`, containing identities, published clues and known facts. Session ID and revision checks discard stale results after reset/case changes. Only an accepted proved verdict can publish a status and its statement together. Restart cancels work and invalidates the old revision. Worker errors are distinct from UNSAT and cannot justify verdicts. The desktop remains responsive during SAT work; navigation and inspection are available while new proposals wait.

The solver is deterministic, self-written **recursive** DPLL with unit propagation, branching/backtracking, conflict detection and optional pure-literal elimination. A failed recursive child increments backtracks; a root contradiction alone does not. Cardinality circuits use quadratic bounded thresholds and parity uses linear XOR chains. Auxiliary assignments are ignored when checking uniqueness of the board. Large imported constraints can still take exponential search time or exceed Python's recursion limit. Desktop cancellation terminates the analysis worker; batch experiments have an explicit per-run timeout.

This is an educational local application. Puzzle files contain solutions, so public-only reasoning is a correctness boundary rather than protection from a user reading files. There is no network service, account, telemetry or database. [DESIGN.md](docs/DESIGN.md) records the original UI concept; [ARCHITECTURE.md](docs/ARCHITECTURE.md) records the current package structure.

## Course submission

The report outline explains the required planning/contribution table, problem formulation, binary/counting CNF derivations, algorithms, experiments, references, AI disclosure and 5–10 minute video. The actual PDF, student contribution information and publicly viewable Drive demo link must be completed by the team.

Once those exist, package a clean submission without local environments/caches:

```powershell
python tools/prepare_submission.py --ids StudentID1 StudentID2 --report path/to/Report.pdf
```

Replace IDs with real ones. The helper creates `StudentID1_StudentID2.zip` with `Source/main.py`, README, requirements, source/tests/docs/results and `Report.pdf`. It refuses to overwrite an existing archive. Verify video sharing in an incognito window; archives over 20 MB must be shared through Drive according to the assignment. Do not submit the `.qa` or virtualenv folders.
