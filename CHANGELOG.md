# Changelog

## 2.2.0 — 2026-07-04

The radio release: SlopeScript programs can talk to the internet.

### Added
- **HTTP builtins**: `radioBase(url, headers?)` (alias `fetch`) for GET,
  `radioJson(url, headers?)` (alias `fetchJson`) for GET-and-parse,
  `radioPost(url, value, headers?)` (alias `post`) — lockers/racks are
  sent as JSON. 30-second timeout; HTTP errors, unreachable hosts, and
  non-JSON replies are all catchable by ski patrol.
- **JSON builtins**: `parseJson(text)` and `toJson(value, pretty?)` —
  JSON maps 1:1 onto racks/lockers/numbers/text/powder/ice/whiteout.
- Browser playground support: `radioBase`/`radioJson` work in the web
  playground through the browser's network stack (subject to CORS);
  `radioPost` reports that it needs the CLI.
- New example `radio_check.slope` (live API call wrapped in patrol);
  radio tests run against a local HTTP server, so the suite (126 tests)
  stays offline-friendly.

## 2.1.0 — 2026-07-04

The "practical release": SlopeScript programs can now span files, talk to
files, treat tricks as values, build text painlessly — and run in a browser.

### Added
- **Browser playground** (`playground/`): the real interpreter compiled to
  WebAssembly via Pyodide — editor, examples, `chairlift` input via browser
  prompts, and shareable program links. Deploys to GitHub Pages
  automatically (`.github/workflows/pages.yml`; enable Pages → Source:
  GitHub Actions once).
- **String interpolation**: `"Run #{n}: {vertical * 2} feet"` — any
  expression inside `{...}` in text; `\{` escapes a literal brace.
- **First-class tricks**: tricks (and builtins) are values — store them,
  pass them, return them. Anonymous tricks:
  `trick(n) stomp n * n runout`. Closures capture their scope. Any
  expression that evaluates to a trick is callable: `rack[0](x)`,
  `locker.fn(x)`.
- **Higher-order builtins**: `map`, `filter`, `reduce`, `each`.
- **Modules**: `traverse "lib/slopemath.slope"` loads another file once,
  relative to the importing file; cycles and repeats are handled.
- **File I/O**: `readFile`, `readLines`, `writeFile`, `appendFile`,
  `fileExists`, `deleteFile` — all failures catchable by ski patrol.
- New examples: `higher_order.slope`, `mountain_tour.slope` (+
  `lib/slopemath.slope`), `trail_journal.slope`; `benchmarks/`.
- Test suite grown to 113 tests.

### Changed
- Interpreter performance: fast paths for number math, truthiness, and
  trick calls — measured ~1.4x on tight loops and ~1.2x on call-heavy
  recursion (`benchmarks/`). Still a tree-walker; still not for
  number-crunching.

## 2.0.0 — 2026-07-04

SlopeScript grows up: from a demo lexer/parser into a complete, tested,
installable language. This is a breaking release — see the migration notes.

### Added
- **Tricks (functions)**: `trick name(params) ... nail`, with `stomp` for
  return values, recursion (with a friendly depth limit), local scope, and
  closures.
- **Lockers (dictionaries)**: `{ key: value }` literals, `locker.key` and
  `locker["key"]` access and assignment, iteration over keys.
- **Ski patrol (error handling)**: `patrol ... patroller (e) ... runout`
  try/catch, and `avalanche value` to throw any value. Runtime wipeouts
  (division by zero, bad indexes, missing keys, type errors) are catchable.
- **The Base Lodge**: ~40 built-in functions — conversion (`number`, `text`,
  `type`), racks (`length`, `push`, `pop`, `laps`, `groom`, `flip`, `find`,
  `slice`, `join`, `sum`, `min`, `max`), text (`upper`, `lower`, `trim`,
  `split`, `replace`, `startsWith`, `endsWith`), lockers (`keys`, `values`,
  `has`, `drop`), math (`abs`, `round`, `basin`, `cornice`, `sqrt`,
  `snowflake`), plus plain-name aliases (`range`, `sort`, `floor`, ...).
- **REPL**: run `slope` with no arguments — multi-line blocks, expression
  echo, persistent session state, `apres` to exit.
- **Language features**: `whiteout` (null), compound assignment
  (`+= -= *= /=`), plain reassignment without `pack`, modulo `%`, power
  `**`, the `in` operator, multi-value `carve "a", b`, blank-line `carve`,
  string escapes (`\n`, `\t`, ...), single-quoted strings, negative rack
  indexing, index/member assignment, rack concatenation with `+`,
  text building with `+` across types.
- **Tooling**: `pip install .` with a `slope` console command, `slope run`,
  `--version`/`--help`, stdin execution, a 90-test suite, and GitHub
  Actions CI across Python 3.8–3.13.
- **Errors that teach**: every syntax and runtime error carries a line
  number and a hint (e.g. "'speed' is not packed — pack it first, like:
  pack speed = ...").

### Changed (breaking)
- Every block now ends with an explicit `runout` (or `nail` for tricks).
  v1 closed loops by repeating the loop keyword and closed conditionals
  implicitly, which made block boundaries ambiguous — code after a
  conditional silently landed inside its last branch. All examples are
  updated to the new syntax.
- Comparing a number with text (`3 < "5"`) is now an error instead of
  undefined behaviour; `==` never coerces types.
- Reassigning an unpacked variable is an error (declare with `pack` first).

### Fixed
- The shipped examples were wrapped in markdown fences and did not parse;
  all examples now run (and CI executes every one of them).
- Whole-number division no longer prints a trailing `.0`.
- Unterminated strings, unclosed comments, and unknown characters now
  produce clear syntax errors with line numbers instead of being silently
  skipped.
- End of input during `chairlift` cleanly stops the program (the lifts are
  closed) instead of looping forever on empty text.

## 1.0.0

Initial experiment: lexer, parser, and tree-walking interpreter with
variables, arithmetic, conditionals, loops, racks, and `chairlift` input.
