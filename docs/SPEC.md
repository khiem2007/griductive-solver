# Behavioral specification

Phase 1 complete: static, read-only analysis of the reference. No application code has been written or executed. Date: 2026-11-07.

Implementation decision record: the user subsequently approved Phases 1-2, accepting the proposed Q1-Q4 choices below. The phase-completion statement above describes the planning snapshot, not the current implementation state. Q5 remains unknown.

Course-audit update (2026-11-08): the user subsequently requested full PDF compliance. The assignment now takes priority where the original behavior differs: alphabetical display-name order, full-clue uniqueness validation, recursive DPLL, explicit SAT-query/revealed-statement trace, full card identities/clues, and retention of experiment failures/timeouts. See COURSE_REQUIREMENTS.md. Report.pdf creation was explicitly excluded by the user; REPORT_OUTLINE_VI.md supplies the requested detailed outline instead.

## Provenance and scope

Reference: parent directory, Griductive Solver. Its configured upstream is https://github.com/TranTai35/griductive-solver (repository owner: TranTai35; authorship not independently verified). No LICENSE, COPYING, or NOTICE file was found locally. License status is unknown. The user explicitly requested skipping the license question; no license grant is inferred. See ../NOTICE.md.

Evidence inspected: README, requirements, entry points, controller, core models/loader/regions/engine, session, logical evaluator/encoder/DPLL/agent, all scene behaviors, button/theme/avatar utilities, and puzzle structures. Existing tests are not the source of this contract. The accompanying course PDF has not been analyzed; whether its requirements also apply is an open question.

The product is an offline desktop deduction game and teaching aid for players and introductory AI students. Players classify people on a square board by logical entailment. Students inspect SAT analysis and automated deduction. Cosmetic identity has no logical meaning. Every clue is truthful, including clues owned by criminals.

## Feature inventory

| ID | Priority | User-facing behavior |
|---|---|---|
| C1 | CORE | Discover and load structured puzzles; validate board, solution, clues and starting reveals |
| C2 | CORE | Public-only knowledge, progressive reveal, and complete-board detection |
| C3 | CORE | Manual verdict submission with distinct acceptance/rejection outcomes |
| C4 | CORE | Six basic clue types, both extensions, and six region selectors |
| C5 | CORE | Deterministic hint with no reveal |
| C6 | CORE | Start/pause automatic deduction without guessing |
| C7 | CORE | Restart and switch cases; independent new session |
| C8 | CORE | Inspect revealed clues and highlight referenced cells |
| S1 | SECONDARY | Separate manual-play and solver-view entry paths; solver view hides verdict buttons and disallows selecting hidden cards |
| S2 | SECONDARY | Public-state uniqueness and analysis metrics |
| S3 | SECONDARY | Ordered deduction trace and headless CSV/JSON experiment exports |
| S4 | SECONDARY | Six bundled examples: two each at 3x3, 4x4 and 5x5; extensions in larger cases |
| S5 | SECONDARY | Tutorial describing entailment, reveal, and error outcomes |
| S6 | SECONDARY | H hint, A auto/pause, R restart, Escape case list; menu/back/load/quit navigation |
| S7 | SECONDARY | Resizable desktop window; reference scales a 1280x760 canvas with preserved aspect ratio |
| N1 | NICE-TO-HAVE | Stable unique character portraits per puzzle; reference selects from 50 PNGs and caches scaled images |
| N2 | NICE-TO-HAVE | Card flip animation, hover effects, colored verdict borders and progress counter |
| N3 | NICE-TO-HAVE | Solver pure-literal optimization comparison report |

Priority is proposed product scope, not a claim that the reference labels these features this way. Extensions are included in C4 because existing valid puzzles depend on them.

## CORE contracts

### C1 — Load and validate

Input: UTF-8 JSON file. Output: validated private puzzle and initial public state. The reference catalog scans its puzzles/*.json in filename order and displays title, description, dimensions and initial clue count. Loading another puzzle starts over; there is no resume.

Required root fields: id, title, size, characters, solution, clues, initially_revealed. description is optional. The loader coerces size to integer; the observed examples use 3, 4 or 5. Cells are uppercase single column letters and positive decimal row numbers, e.g. A1; rows increase top to bottom and columns left to right. Board cells must be covered by characters, solution and clue owners. Each character has cell, name and profession. Each clue has type, optional id (generated from owner when absent), optional data object, and optional display text. Clue IDs must be unique. Every clue must evaluate true under the supplied full solution. Initially revealed coordinates are uppercased and must belong to the board.

Clue validation rejects unknown types, invalid/out-of-board references, identical endpoints in binary relations, empty/duplicate regions, invalid count bounds and invalid parity. JSON parsing, missing keys, conversions, invalid statuses and false clues raise errors; the reference GUI does not provide a recovery dialog and can fail while constructing the catalog. A unique solution and a forced first move are recommendations, not loader requirements. No forced move is a valid stalled state.

Observed gaps, not approved requirements: duplicate character entries collapse by cell despite a misleading error message; duplicate starting reveals are tolerated; UNKNOWN can pass status parsing in solution/FACT; numeric values are coerced; size has no explicit positive bound. These need a policy decision before implementation (Q1).

### C2 — Knowledge and reveal

Private input: full puzzle. Public output: puzzle ID, board size, identities, revealed clue objects, and proved statuses. Initial reveal publishes BOTH the true status and the owner's clue. Hidden clues and hidden labels must never be passed to the reasoning service. Character names and jobs do not affect reasoning.

Transition on accepted verdict: add that cell's status and clue together, append one trace event, then recompute public analysis and uniqueness. Rejections leave public knowledge and trace unchanged. Solved means every cell has a published status, including starting reveals; an entirely revealed starting board is already solved. Reasoning must use a consistent snapshot; stale analysis must not authorize a later reveal.

The reference snapshot copies dictionaries but shares nested clue objects; stronger immutability is a proposed implementation improvement, not an observed guarantee. Local files contain the answers, so this boundary protects solver correctness rather than providing tamper resistance.

### C3 — Submit a verdict

Inputs: selected unresolved cell and CRIMINAL or INNOCENT. No selection or an already revealed selection produces UI feedback without submission. Define K as the conjunction of published clues and published status facts, and x as the cell being criminal.

| Condition | Classification / result | State effect |
|---|---|---|
| K is unsatisfiable | INCONSISTENT | None |
| Both K AND x and K AND NOT x are satisfiable | UNKNOWN / NOT_PROVABLE | None |
| Only K AND x is satisfiable | CRIMINAL forced | Accept criminal; reject innocent as CONTRADICTED |
| Only K AND NOT x is satisfiable | INNOCENT forced | Accept innocent; reject criminal as CONTRADICTED |
| Forced verdict disagrees with private solution | INCONSISTENT | None |

An accepted verdict reveals its owner's clue even if that clue is logically redundant. Both statuses cannot be treated as entailed when K is inconsistent. Finding one satisfying assignment is insufficient proof. On completion, stop automation and show completion feedback. Literal result identifiers above are protocol/domain tokens; new explanatory UI wording must be original.

### C4 — Clue and region semantics

Input: structured clue and board assignment; output: truth value, or validated Boolean constraints for reasoning. All counts refer to criminals.

| Type | Data | Meaning |
|---|---|---|
| FACT | cell, status | Selected cell has the specified binary status |
| SAME | a, b | Both statuses match |
| DIFFERENT | a, b | Exactly one endpoint is criminal |
| EXACTLY | region, k | Criminal count equals k |
| AT_LEAST | region, k | Criminal count is at least k |
| AT_MOST | region, k | Criminal count is at most k |
| PARITY | region, parity | Count is EVEN or ODD, case insensitive |
| IMPLIES | a, b | If a is criminal, b is criminal; an innocent a satisfies the clue |

Counts allow k=0 and k=region size. A basic count requires 0 <= k <= region size. Binary endpoints must be distinct. Type tokens are normalized to uppercase by the loader. FACT/binary cell references require canonical uppercase; region references and starting reveals normalize case.

| Region kind | Parameters | Membership |
|---|---|---|
| ROW | index (one-based integer) | All cells on that row |
| COLUMN | index (letter) | All cells in that column |
| NEIGHBORS | cell | Up to eight adjacent cells, diagonals included, center excluded |
| EXPLICIT | cells | Exactly the listed cells; duplicates forbidden |
| CORNERS | none | Four corner cells |
| BOUNDARY | none | All outer-edge cells, each once |

Out-of-range row/column selectors produce an empty region and fail validation. A 1x1 neighborhood is empty and corners repeat; these are rejected by existing region validation. Nonempty region requirements apply even to mathematically trivial constraints. The logical evaluator and SAT encoding must agree for every supported valid assignment; display text is not parsed as logic.

### C5 — Hint

Input: current public snapshot and analysis. Output: the first forced unresolved cell in row-major order, its forced verdict, and optionally revealed clue owners directly referencing that cell. Hint selects the cell but does not reveal it or append a deduction. Referencing clues are contextual pointers, not a minimal proof. Inconsistent knowledge produces an inconsistency message. With no forced cell (including a finished board), the reference reports that none is available. Repeated hints without a state change return the same move.

### C6 — Automatic deduction

State: stopped or running. Start is refused when solved or inconsistent. Starting resets its timer; first deduction occurs on the next update, followed by roughly 0.65-second intervals in the reference. Each step chooses C5's first forced cell, submits its proved verdict through C3, and refreshes C2. Pause retains progress. Resume continues from current public knowledge. No forced move stops the run without guessing or revealing anything further. Solving the board stops it. Restart or leaving the active session cancels pending work. No catch-up burst is required after a slow frame. Exact animation duration is presentation behavior, not a logical parity requirement.

### C7 — Restart and navigation

Input: reset or case change. Reset restores only initial published statuses and clues, clears trace/selection/highlights/animations, stops automation and resets its timer, then refreshes analysis. Identities remain stable for the same puzzle. Case change uses independent private/public state; no deductions carry over. Reference navigation: menu -> play/solver -> catalog -> board; load/Escape return to catalog, board Back returns to main menu; tutorial returns to menu. New navigation can differ while preserving these capabilities.

### C8 — Evidence inspection

Input: click a board cell. Revealed cell: select it, show its clue, type/ID and references, and highlight precisely the clue's region/endpoints. Hidden cell in manual play: select it for verdict, clear evidence highlights, expose no clue. Hidden cells in solver view cannot be directly selected. Selection of another cell replaces highlights. Names/professions and coordinate labels identify cells. Reference may truncate long clue text on small cards; preserving truncation is unnecessary.

## Data and persistence

Puzzle JSON schema is described in C1/C4. solution maps each coordinate to a status token; clues maps each owner coordinate to one clue. Runtime state holds public dictionaries, current classifications, analysis counters, uniqueness, selected cell, animation/auto state and a trace list. No accounts, network synchronization, saved games, preferences file or database were observed.

Analysis includes primary/auxiliary variable counts, active clause count, SAT calls, branch decisions, unit propagations, backtracks, pure-literal assignments and solver runtime in milliseconds. Public uniqueness is INCONSISTENT (zero models), UNIQUE (one board assignment), or MULTIPLE (more than one); hidden labels are never evidence. Auxiliary assignments must not create false multiple-board results.

Trace records step number (one-based), active clue IDs BEFORE the move, SAT call count of that analysis, cell, verdict and newly revealed clue ID. Starting reveals and rejected submissions create no trace entries.

Experiment persistence (reference): output/experiments.csv contains puzzle, size, primary_variables, auxiliary_variables, full_clauses, sat_calls, decisions, propagations, backtracks, pure_literals, deduction_steps, solved, uniqueness, runtime_ms. output/deduction_traces.json maps puzzle IDs to trace arrays. output/pure_literal_ablation.csv compares counters and times with optimization off/on. Files are overwritten. Batch uniqueness uses ALL clues but no solution facts; GUI uniqueness uses current public evidence. Reference cumulative counters exclude uniqueness calls and final completed analysis; runtime starts after session construction. These metric conventions must be documented if changed.

## External interfaces

- Desktop launch: python main.py; no application CLI argument parser observed.
- Batch launch: python run_experiments.py; scans bundled files and writes the three outputs above; no arguments observed.
- Test command documented by reference: python -m unittest discover -s tests -v (not run in this analysis to avoid reference writes).
- Python 3.10+ recommended; pygame>=2.5.2,<3.0 declared.
- No HTTP endpoints, third-party services, authentication, environment configuration or telemetry observed. Paths resolve relative to source files, not a required network location.

## Non-functional behavior

Offline after dependencies are installed. Reference redraw target is 60 FPS, but SAT work is synchronous and can block input. Analysis is cached per knowledge change instead of recalculated each frame. Count encodings can grow combinatorially and parity encoding exponentially with region size; there is no timeout/cancellation/size-limit contract. Deterministic cell and hint ordering matters; exact branching counters and runtime are not semantic equivalence requirements.

English interface; no localization framework observed. Some source comments/document bytes appear misdecoded by the shell, which does not establish how UI text renders. New text should use UTF-8 and support Unicode identity strings. Reference relies on color and mouse selection; keyboard shortcuts are limited. New interface should offer text status markers and keyboard traversal. Files are local trusted input in the reference; errors are not sanitized into recoverable UI states.

## Open questions for approval

1. Q1: May the new loader deliberately reject malformed inputs accepted accidentally by the reference (duplicate records/reveals, UNKNOWN solution/FACT, fractional counts, unsupported dimensions)? Proposed: strict binary statuses, integer counts, dimensions 3-5 initially, explicit duplicate rejection and readable file errors.
2. Q2: Does the course PDF impose additional deliverable/algorithm constraints? Proposed: preserve a self-authored DPLL/CNF solver and independent semantic evaluator; assess PDF only if course compliance is required.
3. Q3: Is exact metric/export compatibility required? Proposed: retain export column names, disclose counting conventions, allow different clause/counter values from a new encoding.
4. Q4: Must supplied puzzles be imported? Proposed: retain structural JSON import capability, ship six independently authored puzzles with new identities and wording; do not redistribute reference data or assets.
5. Q5: License remains unknown following the user's request to skip the question; no copyright or license text was available to preserve. This document makes no licensing determination.
