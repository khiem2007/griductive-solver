# Proof Ledger — proposed product design

Phase 2 complete. Implementation requires user approval. This document proposes choices for review; unresolved questions in SPEC.md remain unresolved until approved.

Approval record: the user subsequently replied “approved,” authorizing this design and the proposed SPEC Q1-Q4 choices. Implementation and verification follow below in the repository; this document preserves the original phase boundary.

Course-audit update (2026-11-08): the user's later PDF review request supersedes parts of this initial design. Cards now show names/professions, face-up/down state and published statements; controls/messages stay in a fixed footer. DPLL is recursive, input validates alphabetical names/full-clue uniqueness, and batch workers retain errors/timeouts. The report deliverable requested by the user is a detailed outline, not a generated PDF. See COURSE_REQUIREMENTS.md and REPORT_OUTLINE_VI.md.

## Product and stack

An offline Python desktop investigation notebook. Use Python 3.11+, Tkinter/ttk for native controls and adaptive layout, dataclasses/enums for typed domain values, and a self-written CNF/DPLL reasoning package. Use standard-library unittest for tests and Ruff for development linting. No browser, web service, copied assets, or Pygame dependency. Tkinter availability is checked at installation; some Linux distributions need their system Tk package.

Changing toolkit is proposed within the user's instruction to keep Python. The working folder remains griductive-rebuild; Proof Ledger is new display branding. Original sample content will replace reference titles, people and prose.

## Architecture

Organize by capabilities with narrow immutable messages. UI issues commands; a case coordinator owns reveal authority and state revisions; a reasoning worker receives only a frozen public snapshot. An import adapter creates private definitions. The reasoning package cannot import the private case store. A separate batch adapter composes the same capabilities without importing Tkinter.

```text
griductive-rebuild/
  pyproject.toml
  README.md
  NOTICE.md
  docs/
    SPEC.md
    DESIGN.md
    PARITY.md                 # Phase 4
  src/proofledger/
    __init__.py
    __main__.py               # thin desktop entry
    launch.py                 # composition and dependency wiring
    contracts/
      values.py               # coordinates, verdicts, clue expressions
      messages.py             # public snapshots, commands, results
    cases/
      import_json.py          # compatibility boundary and validation errors
      catalog.py              # catalog metadata, per-file failures
      vault.py                # private definitions and authorized reveals
    reasoning/
      regions.py
      truth.py                # direct expression interpretation
      compiler.py             # clue-to-CNF translation
      search.py               # independent DPLL implementation
      inference.py            # classifications, uniqueness and hint ordering
    investigation/
      coordinator.py          # command handling, revision, session lifecycle
      journal.py              # accepted-move audit events
      automation.py           # scheduled next-move policy
    desktop/
      shell.py                # persistent application frame and routing
      library.py              # case list, mode choice, file open
      workspace.py            # board + notebook composition
      board.py                # coordinate matrix and keyboard focus
      notebook.py             # evidence, chronology and analysis tabs
      guidance.py             # original help text
      appearance.py           # new palette/type/spacing tokens
      tasks.py                # process worker lifecycle and UI polling
    reports/
      __main__.py             # batch entry, explicit input/output paths
      runner.py               # same inference/reveal pipeline without GUI
      export.py               # CSV and JSON serialization
    samples/                  # six original JSON investigations
  tests/
    test_case_import.py
    test_region_contracts.py
    test_clue_truth_tables.py
    test_sat_oracle.py
    test_inference_contracts.py
    test_investigation_flow.py
    test_automation_policy.py
    test_report_formats.py
```

| Reference module | New module(s) | Structural difference |
|---|---|---|
| core/models.py | contracts/values.py, contracts/messages.py, cases/vault.py | Public interchange values separated from private storage; no shared mutable clue dictionaries |
| core/puzzle_loader.py | cases/import_json.py, cases/catalog.py | Format adapter separate from discovery and individual-file error presentation |
| core/regions.py, logic/semantics.py | reasoning/regions.py, reasoning/truth.py | One expression vocabulary shared through immutable contracts; interpretation independent of compilation |
| core/game_engine.py, game/session.py | cases/vault.py, investigation/coordinator.py, journal.py | Private reveal authority separated from command lifecycle and audit history |
| logic/cnf_encoder.py, dpll.py, agent.py | reasoning/compiler.py, search.py, inference.py | Independently implemented algorithms behind value-oriented requests; no copied routines or method hierarchy |
| app_controller.py, main.py | launch.py, desktop/shell.py, desktop/tasks.py | Native event loop and background process messages replace scaled scene rendering |
| scenes/menu/level_select/tutorial | desktop/library.py, guidance.py | Persistent library navigation and contextual help replace a separate menu/tutorial scene chain |
| scenes/game_scene.py | desktop/workspace.py, board.py, notebook.py, investigation/automation.py | Evidence and time controls are separate views/policies, not one drawing/input class |
| ui widgets/theme/avatar_manager | ttk controls, appearance.py, coordinate monograms | Native focusable widgets and original geometry; no portrait asset system |
| run_experiments.py | reports/runner.py, export.py, __main__.py | Reusable batch capability with explicit paths and no desktop dependencies |

The mapping identifies responsibility equivalents, not templates to translate line by line. Reference code must not be imported or used at runtime. No new module may depend on the parent project.

### State and trust boundaries

Case definition -> vault -> public snapshot -> inference request -> analysis result -> coordinator command -> authorized reveal -> new revision.

The vault retains solution and unrevealed clues. Snapshots contain only public facts and already published clues plus identities. Analysis carries the session ID and revision. Coordinator checks both before applying a result; previous-case or previous-revision work is discarded. Published facts and clues are committed atomically. No UI action accepts a proposed classification supplied by a widget as proof.

One worker process handles CPU-bound inference, leaving the Tk event loop responsive. Worker startup is protected for Windows multiprocessing. Requests contain only public data. UI polls a queue using Tk timers; widgets are updated only on the UI thread. Cancel/restart/case-switch invalidates outstanding work; shutdown or hard cancellation terminates and joins the worker. Errors return structured messages rather than revealing private data. While analysis is pending, disable verdict/auto-step actions and show progress; inspection and navigation remain usable.

Separate presentation state (selection, active tab, focus, running/paused) from evidence revision. Hint does not change evidence. Auto mode schedules one deduction at a time after current analysis completes; it never queues speculative reveals. Its default step interval is 650 ms and can be paused. Exact animation/branching order is not a compatibility obligation; row-major hint ordering is.

### Reasoning approach

Keep a pure direct truth evaluator as an oracle independent of CNF. Use a newly written deterministic DPLL with propagation, explicit branch state and optional pure-literal elimination. Initially use independently derived cardinality constraints suitable for 3-5 boards; optimize only after measuring. Parity may use auxiliary XOR constraints to avoid the reference's exhaustive assignment expansion. Uniqueness blocks primary cell assignments only. Auxiliary counts and clause totals may consequently differ; decisions/timing are diagnostic, not parity targets.

Use immutable normalized clue values rather than pervasive untyped data maps after import. JSON compatibility tokens remain confined to the adapter/export boundary. The algorithm should report an interrupted/error outcome distinctly from logical UNSAT; cancellation is never proof.

## UI/UX concept

The reference is a dark, portrait-heavy card grid with a permanent right metrics panel and separate play/solve menus. The new product is a light editorial notebook: a persistent library rail, a compact coordinate matrix without clue text inside cells, and a lower evidence notebook. This changes navigation, information hierarchy, component geometry and interaction, as well as color.

```text
+----------------+------------------------------------------+
| Proof Ledger   | Investigation title       7 / 16 resolved |
| Investigations |                                          |
| size filters   |           A    B    C    D                 |
| case list      |       1  [ ]  [ ]  [ ]  [ ]               |
| Open file      |       2  [ ]  [ ]  [ ]  [ ]               |
|                |       ...                                |
| Guidance       | Selected identity + binary verdict actions|
|                | Evidence | Chronology | Analysis          |
|                | Full clue statement + reference chips     |
|                | Hint       Run / Pause       Reset         |
+----------------+------------------------------------------+
```

- Navigation: open directly to the case library with an empty workspace prompt. Selecting a case loads it into the persistent workspace. A “Hands-on / Observe” segmented choice preserves the two modes without duplicating the catalog. Library toggle returns focus to case selection; help opens in a dismissible native panel.
- Board: compact numbered/lettered matrix with coordinate monograms and optional name under each token. No portraits, flip cards, or hidden clue prose. Status has a textual badge plus a geometric marker (filled diamond for criminal, open circle for innocent, dash for unresolved). Evidence references get an inset outline; current selection gets a separate focus ring. All cells have keyboard focus and a full identity description in the selection row.
- Notebook: Evidence shows the selected revealed clue in full, its type and coordinate chips. Hidden selections show original short guidance only. Chronology lists accepted verdicts in order. Analysis moves diagnostic counters and uniqueness off the main playing surface. Reference chips can focus cells without changing the active clue.
- Actions: manual verdict controls sit next to the selected identity. Hint and Run/Pause live below the notebook; Reset is a quieter adjacent action. Observe mode removes manual verdict controls and hidden-cell activation. Errors appear in a persistent message strip with outcome text; completion offers reset or library navigation. Failed guesses never reveal content.
- Palette: warm paper #F6F2E9, white surfaces #FFFFFF, ink #252A34, muted text #5D6570, primary indigo #493FA8, accent ochre #A66A16, criminal plum #783D68, innocent blue #236C88. Verify actual text contrast during implementation. Status is always encoded with text/shape as well as color.
- Typography: system UI face (Segoe UI on Windows, available platform fallback), body 12 pt, title 22 pt semibold; monospace coordinates using a system fixed font. No bundled reference fonts or icon files. Use text controls and simple independently drawn shapes.
- Components: application shell, library list/filter, mode switch, board matrix, selection summary, verdict group, evidence reader, reference chips, chronology list, analysis table, automation toolbar, message strip and guidance panel.
- Responsive behavior: at >=1100 px show a 220 px library rail. Between 800 and 1099 px collapse it behind a library button. Below 800 px use a vertically scrollable board/notebook stack and a library overlay; do not shrink all text to fit. Board fits available width for 3-5 cells with a minimum target size, then scrolls. Controls wrap; notebook content scrolls independently. Minimum supported window proposed: 640x600. Native DPI/font scaling applies rather than scaling a fixed logical canvas.
- Keyboard: preserve H/A/R shortcuts when not typing, Escape pauses/returns to library as documented in the new UI, arrows move board focus, Enter selects, Tab traverses controls. Shortcuts do not fire inside text inputs. Highlight focus visibly. Exact Escape behavior differs from the reference and will be recorded in PARITY.md.
- Presentation: a brief outline pulse marks reveal; no card flipping. Reduced visual motion can simply disable the pulse. Original wording explains results; domain tokens may appear in the Analysis tab.

## Compatibility and original content

Retain structural JSON import for valid reference-format cases but do not bundle copies of reference puzzles. Ship six freshly authored examples at the same size distribution, with new clue graphs, names, professions, titles and text. Exercise every clue and region across samples/tests. Validate clue truth and a complete no-guess reveal path for each authored sample. A stalled imported puzzle remains valid and must stop gracefully.

Proposed loader improvements and supported dimensions require approval via SPEC Q1. Do not silently implement undocumented coercion or call malformed behavior parity. Export field names can remain compatible while README explains changed metrics. Reports distinguish public-state uniqueness from all-clues uniqueness.

## Test plan derived from SPEC

Use hand-authored fixtures and bounded exhaustive Boolean enumeration as the independent oracle. Do not copy reference tests or expected deduction sequences. Logical unit/integration tests run headlessly without Tk. GUI behavior uses the manual checklist; test the coordinator/timer policies independently where deterministic.

| CORE | Unit / integration verification | Manual acceptance |
|---|---|---|
| C1 | Valid 3/4/5 boards; missing fields/cells; bad JSON; duplicate IDs; false clues; region/count/status failures; approved Q1 rules | Catalog shows dimensions; open valid file; invalid file gives recoverable error and preserves current session |
| C2 | Starting reveals publish clue+status; rejected moves preserve snapshots; hidden-clue changes leave current classifications unchanged; stale revisions rejected; initially complete board | Inspect initial and newly revealed facts; switch cases during analysis and confirm no old reveal appears |
| C3 | Fixtures for accepted, unknown, contradicted, inconsistent; compare classifications to exhaustive models; no rejected trace events; no repeated reveal | Attempt a correct-but-unprovable answer, opposite forced answer, then forced answer; only the last reveals |
| C4 | Truth tables for all eight types; compare CNF satisfiability under every primary assignment to direct evaluation, allowing auxiliary completions; all six regions incl. edge/corner neighbors and k boundaries | Inspect representative clue types and verify highlighted coordinates match statement |
| C5 | Row-major first forced move; repeated hint same result; no public/trace mutation; inconsistent and no-move states | Hint focuses cell and shows verdict, leaves its clue hidden |
| C6 | Fake clock plus coordinator: one accepted move per cycle, pause/resume, stall/completion stop, restart invalidates scheduled work, analysis error cannot become UNSAT | Run, pause mid-case, resume; test a stalled imported fixture and reset during active computation |
| C7 | Restart matches initial public state and clears journal; case/session isolation; old worker response ignored | Make progress, reset, compare to initial view; change case and return without stale progress |
| C8 | Selection policy resolves exact reference set, clears for hidden cell; observe blocks hidden activation | Select each region/binary clue; confirm full text, reference chips, focus and no hidden clue leak |

Additional verification: SAT solver agrees with a truth-table oracle on bounded generated CNFs, handles empty formula/empty clause/conflicting assumptions, and gives same satisfiability with pure literals on/off. Uniqueness tests cover zero, one, multiple primary assignments with auxiliary variables. CSV/JSON tests check schema, ordering, before-move clue IDs and documented counter scope. Six original samples must solve with every accepted verdict justified by exhaustive checks where tractable and SAT entailment on all sizes.

Manual UI checklist also covers both modes, guidance/navigation, all shortcuts, 640/800/1100 px layouts, Windows display scaling, long Unicode identities/clues, visible focus, status without color, and clean exit during worker activity. A responsive-interface check runs a deliberately slow synthetic inference task while interacting with library/help.

Planned commands after implementation (not executed yet):

```powershell
python -m pip install -e ".[dev]"
python -m compileall -q src
python -m ruff check .
python -m unittest discover -s tests -v
python -m proofledger
python -m proofledger.reports --puzzles <directory> --output <directory>
```

Python has no bundle build in the desktop development loop; compileall is the syntax check. Final packaging validation will additionally build a wheel using the configured build backend and install/run it from an isolated environment. Commands will be run from the new project only; artifacts stay there. No tests have been claimed as passing during planning.

## Implementation milestones (after approval)

1. Foundation and import: package configuration, immutable contracts, strict approved loader/regions, structured errors and original tiny fixtures. Run syntax/lint/import and region tests.
2. Reasoning: direct evaluator, independent compiler/DPLL, entailment, uniqueness, diagnostic definitions. Run truth-table oracle, SAT and inference tests plus all accumulated checks.
3. Investigation lifecycle: vault, coordinator, public revisions, journal, hints, reset and auto policy. Run no-leak/rejection/state-transition/timer tests and accumulated checks.
4. Desktop workspace: Tk library, matrix, evidence notebook, modes, help, shortcuts, adaptive layout and worker process. Run accumulated checks and manual UI/DPI/worker lifecycle checks.
5. Original cases and reports: six original investigations, headless batch/export and optimization comparison, setup/run/test/architecture README. Validate all samples, report schemas and accumulated checks.
6. Parity and delivery: create docs/PARITY.md with one row for each C1-C8, done/partial/missing, evidence and differences. Run full lint/tests, wheel build/install smoke check and final manual checklist. Report actual totals, failures/skips and unresolved differences.

After each milestone: fix failing checks before proceeding and provide a concise change/verification report. Broaden testing when new changes justify it. Phase 3 has not started. Approval should confirm this architecture/UI and resolve SPEC Q1-Q4 or explicitly accept their proposed choices; Q5 remains documented as unknown.
