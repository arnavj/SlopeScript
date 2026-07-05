# FAQ ❓

## Is SlopeScript a real programming language?

Yes. It has first-class functions with recursion and closures, arrays and
dictionaries, structured error handling, modules, string interpolation, an HTTP
+ JSON client, file I/O, a ~50-function standard library, a REPL, and a browser
playground. Every concept maps 1:1 onto Python or JavaScript. The skiing syntax
is a friendly surface over genuinely conventional semantics.

## What is it *for*?

Learning to code, and having fun doing it. It deliberately sits between toys
(which you outgrow in a week) and full languages (whose first error message
sends you to Stack Overflow). It's especially at home in ski towns, ski clubs,
and STEM programs — an on-theme way in where "guess the snow depth" beats
"guess the number." See the *Why SlopeScript?* section on [Home](Home).

## What do I need to run it?

**Python 3.8+** and nothing else — there are **zero runtime dependencies**. Or
run it with nothing installed at all in the **[Playground](Playground)**. See
[Getting Started](Getting-Started).

## Why does every block end with `runout`?

So block boundaries are unambiguous. Whitespace and indentation are **not**
significant in SlopeScript, so the interpreter needs an explicit end-of-block
marker — that's `runout` (or `nail` for tricks). In v1.0 conditionals closed
implicitly and code could silently land inside a branch; explicit `runout`
(v2.0) fixed that. See [Control Flow](Control-Flow).

## What's the difference between `nail` and `runout`?

Nothing functional — they're interchangeable for closing a trick. Convention is
to close **tricks** with `nail` (nail the landing) and **everything else** with
`runout` (the flat at the bottom of the run). Style only.

## `pack` vs `=` — when do I use which?

- **`pack name = value`** *declares* a new variable. Inside a trick it makes a
  **local**.
- **`name = value`** *reassigns* an existing variable. It walks outward to find
  the nearest packed `name`, so a trick can update an outer variable this way.

Reassigning a name that was never packed is an error (it catches typos). See
[Variables & Operators](Variables-and-Operators).

## Why did `3 < "5"` throw an error?

On purpose. Comparisons work between **two numbers or two texts**; comparing
across types is an error rather than a silent surprise. Likewise `==` never
coerces, so `1 == "1"` is `ice`. Strictness turns confusing bugs into clear
errors. See [Variables & Operators](Variables-and-Operators#comparisons-are-strict).

## How do I get a number from user input?

`chairlift` always returns **text**. Wrap it in `number(...)`:

```slopescript
pack age = number(chairlift("Age? "))
```

If the text won't tune into a number, that's a catchable error — guard it with
`patrol`. See [Error Handling](Error-Handling).

## How do I do a counting `for` loop?

There's no C-style `for`. Iterate over `laps(n)`:

```slopescript
liftline i in laps(10)   // 0..9
  carve i
runout
```

`laps(start, stop)` and `laps(start, stop, step)` also work. See
[Control Flow](Control-Flow#counting-with-lapsn).

## Can functions be passed around?

Yes — tricks (and builtins) are **first-class values**. Store them in variables,
racks, and lockers; pass them to `map`/`filter`/`reduce`; return them from other
tricks; write them anonymously (`trick(n) stomp n*n runout`). See
[Tricks (Functions)](Tricks-Functions#tricks-are-first-class-values).

## Does HTTP work in the browser playground?

GET (`radioBase` / `radioJson`) works through the browser's network stack,
**subject to the target site's CORS policy**. `radioPost` needs the CLI. See
[Playground](Playground) and [Files & the Radio](Files-and-the-Radio).

## Why is my recursion erroring with "Avalanche risk"?

Recursion deeper than **200 calls** trips a friendly depth-limit error instead of
crashing the Python interpreter. Check for a missing base case, or rewrite deep
recursion as a loop. See [Tricks (Functions)](Tricks-Functions#recursion).

## Is it fast?

It's a tree-walking interpreter — built for clarity, not number-crunching. It's
plenty fast for learning and scripting, not for heavy computation. See
[Language Internals](Language-Internals#performance).

## Where's the authoritative spec?

[`LANGUAGE_SPEC.md`](https://github.com/arnavj/SlopeScript/blob/main/LANGUAGE_SPEC.md)
in the repo is the formal reference. This wiki is the friendly, task-oriented
companion to it.

## How do I contribute?

See [Contributing](Contributing) and the repo's
[CONTRIBUTING.md](https://github.com/arnavj/SlopeScript/blob/main/CONTRIBUTING.md).
Good first contributions: new example programs, new themed builtins (with tests),
and better error messages.
