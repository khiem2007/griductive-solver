# Core feature parity and verification

## Course-audit addendum — 2026-11-08

The original 2026-11-07 verification below is a historical checkpoint. The subsequent full assignment review is recorded in COURSE_REQUIREMENTS.md. The source now has recursive DPLL; alphabetical-name/full-clue uniqueness validation; names/professions and public statements on every card; a fixed control/message footer; actual SAT-query assumptions/results and revealed clue content in traces; and per-input/per-mode benchmark workers that preserve failures/timeouts. The original permissive uniqueness/import and trace/export statements below are superseded by this addendum and the current README.

Current verification: the final full course-audit suite passed all 40 tests in 13.731 seconds (0 failures/errors/skips), including the fixed-footer change. Ruff and compileall pass. Six original cases solved with full-clue UNIQUE; diagnostic output retains STALLED/INVALID and a deliberately tiny timeout probe retains TIMEOUT in both optimization modes. The wheel rebuilt, reinstalled into an isolated venv and passed its GUI/worker/hint smoke check. The submission helper passed a source-layout/cache-exclusion smoke check. Final evidence is recorded in COURSE_REQUIREMENTS.md.

The user explicitly requested an outline instead of creating Report.pdf: REPORT_OUTLINE_VI.md includes the detailed report structure, actual encoder derivations, experiment interpretation, AI disclosure guidance, a seven-minute demo script and submission checklist. No final PDF/video/upload or real student contribution data is claimed. main.py and requirements.txt support direct source execution; tools/prepare_submission.py packages an existing final PDF with actual IDs.

At the start of this review, git already showed the assignment PDF deleted from the parent directory and present inside the new project. That pre-existing user file move was preserved. Source edits in this review remain inside griductive-rebuild.

## Original implementation checkpoint

Completed 2026-11-07 after approval of the specification and design. New product: Proof Ledger, Python/Tkinter. All implementation, original content, tests, documents and generated artifacts are inside griductive-rebuild. The reference was inspected/read but its code and tests were not imported or executed. A final git diff check found no tracked reference changes.

## CORE feature status

| Feature | Status | Verification | Known behavioral differences |
|---|---|---|---|
| C1 Load/validate | done | Import/region tests cover 3/4/5 boards, malformed inputs, duplicates, false statements, status/count bounds and independent catalog failures. All six reference-format files were read and solved by the new implementation. Installed wheel discovers six packaged original cases. Desktop failed-open test preserves the current session. | Approved strict rejection of ambiguous/malformed inputs; supported dimensions explicitly 3-5. Recoverable file errors replace reference initialization failures. New library and native file picker replace scene navigation. |
| C2 Public-only progressive reveal | done | Snapshot/atomic reveal tests; hidden-clue mutation leaves public classifications unchanged; immutable message values; stale results rejected; initially solved board tested. Worker receives public snapshots only. | Snapshots deeply immutable through frozen values/tuples; analysis has session/revision protection and runs outside the UI process. |
| C3 Verdict proof and rejection | done | Unit fixtures distinguish accepted, not provable, contradicted and inconsistent; refusal changes no state; private mismatch rejected; generated SAT and exhaustive model oracles support entailment correctness. Live contradicted proposal exposed nothing. | Original explanatory messages; INVALID and PENDING additionally describe UI misuse/in-flight work. No change to the four logical outcome meanings. |
| C4 Eight clues/six regions | done | Every supported statement tested against all assignments on four primary cells, including every count boundary and auxiliary completions. Region tests cover exact membership, diagonal neighbors, duplicate/empty/out-of-board failures. Bundled content exercises all eight types and six selectors. | Prefix-bound cardinality circuits and XOR chains introduce auxiliary variables; CNF size and search counters differ. Structured JSON tokens stay compatible. Display text is independently authored. |
| C5 No-reveal deterministic hint | done | Hint selects first row-major unresolved forced cell, repeats without mutation, refuses inconsistency/no-move; live hint selected an unresolved identity and preserved its hidden evidence. | Context pointers appear in original wording. They identify referencing public clues rather than a minimal formal proof. |
| C6 Automatic deduction | done | Fake-clock tests verify pause/resume, one step per cycle, awaiting analysis, completion and stall. Six original cases solve with optimization on/off and matching traces. Live Run opened proved identities; A paused while retaining evidence. Worker failures are distinct from UNSAT. | Steps await asynchronous analysis, so wall-clock intervals can exceed 650 ms; no fixed solving timeout. Pausing keeps the current analysis work, while reset/switch/close cancel it. |
| C7 Restart/case switching | done | Reset restores initial evidence and clears journal/selection. Revision and case isolation tested. Desktop test switches cases during worker activity, ignores old work and confirms reset stops automation. Live reset restored only starting evidence; clean window close completed. | Persistent library, mode toggle and help panel replace menu/scene routes. Escape pauses and opens the library. No save/resume was added. |
| C8 Evidence inspection | done | Exact public reference sets, hidden selection clearing and Observe restrictions tested. Focus chips preserve the inspected clue. Live 5x5 selection highlighted the correct endpoints and showed the full statement; scrolling exposed chips/actions. | Compact coordinate tiles replace portraits and clue-filled cards. Clues live in a scrollable notebook; original text is not truncated into tiles. |

## Supporting features

- Both Hands-on and Observe modes include load, reset, hint and run/pause.
- Current-public uniqueness and diagnostics appear in the Analysis tab. Batch all-clue uniqueness excludes solution facts and ignores auxiliary-only differences.
- Chronology records accepted deductions; CSV/JSON exports retain documented column/field names and before-move clue IDs.
- Six original investigations replace reference content: Glasshouse Register, Harbor Receipts, Clockmakers Circle, Orchard Dispatch, Lantern Archive and Observatory Roster.
- Original guidance, native keyboard focus, coordinate navigation, H/A/R shortcuts, small-window library overlay and scrolling are implemented.
- Pure-literal ablation exports are implemented. Portraits, flip animations and a reveal pulse were omitted; static selection/reference outlines and text/shape verdict markers provide feedback.

## Executed commands and outcomes

Commands ran inside the new project. During development PYTHONPATH=src;.qa/tools exposed source and locally installed QA tools; the isolated wheel checks explicitly removed PYTHONPATH.

| Command/check | Result |
|---|---|
| python -m compileall -q src | Passed |
| python -m ruff check . | Passed |
| python -m unittest discover -s tests -v | 33 tests passed; 0 failures/errors/skips; final full run 22.839 seconds |
| python -m proofledger.reports --output output | Exit 0; all 6 original cases solved; 3 report files generated |
| Read-only run_case over ../puzzles/*.json using only new imports | All 6 reference-format cases validated and solved; all-clue UNIQUE; 7/14/23 deductions for 3/4/5 boards |
| python -m build --wheel --no-isolation | Built dist/proof_ledger-0.1.0-py3-none-any.whl |
| python -m venv .qa/wheel-env, followed by local wheel installation with --no-index --no-deps | Installed successfully with no runtime third-party dependencies |
| Installed-wheel desktop/worker smoke script | Imported from isolated site-packages; six packaged cases found; Tk launched, asynchronous analysis returned, hint worked and window/worker closed |
| Isolated python -m proofledger.reports --output .qa/installed-reports | Exit 0; all 6 packaged cases solved; 3 reports generated |
| Wheel ZIP inventory | Includes all 6 original JSON samples and dist-info/licenses/NOTICE.md |
| git diff --exit-code | Exit 0; no tracked reference edits; new project remains untracked pending user's version-control workflow |

Milestone checkpoints: 6 tests after foundation, 14 after reasoning, 22 after lifecycle, 27 after desktop, 31 after samples/reports, and 33 in final verification. All corresponding syntax/lint checks passed. The first QA tool download was blocked by sandbox networking; a network-authorized retry installed tools locally. A slow intermediate cardinality implementation was replaced before completion; final correctness and sample tests were rerun successfully.

The exhaustive suite compares all 352 four-cell clue/assignment combinations, 160 generated CNFs with both optimization settings, and all public-state classifications along both original 3×3 sample traces against direct Boolean enumeration. Larger original cases and all six reference files were solved by SAT entailment; no exhaustive 2^25 oracle run is claimed.

## Original sample batch results

Representative source-run timings; they are observations on this machine, not performance guarantees. Both optimization settings solved every sample and produced the same accepted trace.

| ID | Board | Accepted deductions | Solved | All-clue uniqueness | Runtime ms |
|---|---|---|---|---|---|
| ledger_01 | 3x3 | 7 | yes | UNIQUE | 109.483 |
| ledger_02 | 3x3 | 7 | yes | UNIQUE | 52.996 |
| ledger_03 | 4x4 | 14 | yes | UNIQUE | 329.046 |
| ledger_04 | 4x4 | 14 | yes | UNIQUE | 81.465 |
| ledger_05 | 5x5 | 23 | yes | UNIQUE | 4109.414 |
| ledger_06 | 5x5 | 23 | yes | UNIQUE | 119.086 |

Metrics differ intentionally: prefix counters/XORs add auxiliaries; branching strategy and propagation counters differ. New batch runtime includes initial evidence analysis, while the reference starts its timer after initial session analysis. Classification counters exclude uniqueness queries; traces store the pre-move analysis SAT-call count. Solved boards do not incur a redundant final batch analysis.

## Desktop verification and limits

Live Windows inspection confirmed the light notebook layout, readable clue font, reset, no-reveal hint, contradicted verdict refusal, published-cell reference outlines, Observe-mode hidden verdict controls, Run/Pause, compact library navigation, minimum 640x600 5×5 board fit, and access to evidence/actions through scrolling. The environment rendered at its current display scaling; multiple Windows scaling settings were not changed or tested.

Automated Tk integration additionally checks 640/800/1100-pixel layouts, exact right-edge board fit, scroll extent, failed-open recovery, focus chips, Observe restrictions, an event-loop heartbeat during reasoning, cancellation on case change and stopping automation on reset. Process tests verify actual Windows spawn results, cancellation and error delivery. Native file-picker interaction, all keyboard navigation combinations, extreme Unicode/very long text, screen-reader compatibility, Linux/macOS behavior and additional DPI configurations have not been comprehensively manually certified. Tk tests require a graphical display and intentionally do not silently skip.

No saved sessions, online services or localization were added. Pathological valid imported puzzles can still require exponential DPLL search; the isolated process keeps navigation usable and can be cancelled. File export is not a multi-file atomic transaction if the operating system fails during writing.

Original license status remains unknown, as recorded in NOTICE.md. The course PDF was outside the approved implementation scope; course-specific report/deliverable compliance is not asserted.
