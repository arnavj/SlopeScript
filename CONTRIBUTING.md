# Contributing to SlopeScript 🎿

Stoked you're here. SlopeScript is deliberately small and readable — the
whole language (lexer, parser, interpreter, stdlib, REPL, CLI) lives in
[`slopescript.py`](slopescript.py), and it should stay that way: a language
you can read in one sitting.

## Getting set up

```bash
git clone https://github.com/arnavj/slopescript.git
cd slopescript
pip install -e .
python3 -m unittest discover tests   # everything should pass
```

No dependencies, no build step. Python 3.8+ only.

## Ground rules

- **Zero runtime dependencies.** The standard library ships with Python.
- **Every feature needs tests.** Add cases to `tests/test_slopescript.py`;
  CI runs the suite on Python 3.8–3.13 and executes every example.
- **Errors must teach.** A SlopeScript error should say what went wrong,
  where (line number), and ideally how to fix it — in plain, friendly
  language. Compare: `⛑️ 'speed' is not packed — pack it first, like:
  pack speed = ...`
- **Stay on theme, stay clear.** New keywords and builtins should be real
  skiing terms whose meaning maps naturally onto the concept (`groom` →
  sort, `basin` → floor). If a themed name would be cryptic, give it a
  plain alias like the existing `sort`/`floor`/`range`.
- **Examples are documentation.** If you add a feature, consider a short
  example in `examples/` — it must run cleanly, and CI will check that.

## Good first contributions

- New example programs (games are great)
- New Base Lodge builtins (with tests + spec table row)
- Better error messages
- Editor syntax highlighting (VS Code / TextMate grammar)
- Bug reports with a minimal `.slope` file that reproduces the issue

## Pull requests

1. Fork, branch, make your change.
2. `python3 -m unittest discover tests` — green.
3. Update `LANGUAGE_SPEC.md` / `README.md` if behaviour changed.
4. Add a line to `CHANGELOG.md`.
5. Open the PR with a short description and a sample program if relevant.

See you on the hill! ⛷️
