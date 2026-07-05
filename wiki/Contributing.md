# Contributing 🤝

Stoked you're here. SlopeScript is deliberately small and readable — the whole
language (lexer, parser, interpreter, stdlib, REPL, CLI) lives in one file,
[`slopescript.py`](https://github.com/arnavj/SlopeScript/blob/main/slopescript.py),
and it should stay that way: a language you can read in one sitting.

This page summarises the repo's
[CONTRIBUTING.md](https://github.com/arnavj/SlopeScript/blob/main/CONTRIBUTING.md)
— that file is the source of truth.

## Getting set up

```bash
git clone https://github.com/arnavj/slopescript.git
cd slopescript
pip install -e .
python3 -m unittest discover tests   # everything should pass
```

No dependencies, no build step. Python 3.8+ only. For a map of how the code is
organised, read [Language Internals](Language-Internals).

## Ground rules

- **Zero runtime dependencies.** The standard library ships with Python; keep it
  that way.
- **Every feature needs tests.** Add cases to `tests/test_slopescript.py`. CI
  runs the suite on Python 3.8–3.13 and executes every example.
- **Errors must teach.** A SlopeScript error should say what went wrong, where
  (line number), and ideally how to fix it — in plain, friendly language.
  Compare: `⛑️ 'speed' is not packed — pack it first, like: pack speed = ...`
- **Stay on theme, stay clear.** New keywords and builtins should be real skiing
  terms whose meaning maps naturally onto the concept (`groom` → sort, `basin` →
  floor). If a themed name would be cryptic, give it a plain alias like the
  existing `sort` / `floor` / `range`.
- **Examples are documentation.** If you add a feature, consider a short example
  in `examples/` — it must run cleanly, and CI checks that.

## Good first contributions

- New example programs (games are great).
- New Base Lodge builtins (with tests + a spec-table row).
- Better error messages.
- Editor syntax highlighting (VS Code / TextMate grammar).
- Bug reports with a minimal `.slope` file that reproduces the issue.

## Pull-request checklist

1. Fork, branch, make your change.
2. `python3 -m unittest discover tests` — green.
3. Update
   [`LANGUAGE_SPEC.md`](https://github.com/arnavj/SlopeScript/blob/main/LANGUAGE_SPEC.md)
   / [`README.md`](https://github.com/arnavj/SlopeScript/blob/main/README.md) if
   behaviour changed.
4. Add a line to
   [`CHANGELOG.md`](https://github.com/arnavj/SlopeScript/blob/main/CHANGELOG.md).
5. Open the PR with a short description and a sample program if relevant.

## Where things live

| Concern | Location |
|---|---|
| The entire language | `slopescript.py` |
| Tests | `tests/test_slopescript.py` |
| Example programs | `examples/` (+ `examples/lib/`) |
| Browser playground | `playground/index.html` |
| Benchmarks | `benchmarks/` |
| Formal spec | `LANGUAGE_SPEC.md` |
| Packaging / entry points | `pyproject.toml` |

## Improving this wiki

The wiki pages are authored as Markdown under
[`wiki/`](https://github.com/arnavj/SlopeScript/tree/main/wiki) in the main repo
and published to the GitHub wiki. See
[`wiki/README.md`](https://github.com/arnavj/SlopeScript/blob/main/wiki/README.md)
for how to edit and publish them. Improvements — clearer explanations, more
examples, fixed typos — are just as welcome as code.

See you on the hill! ⛷️
