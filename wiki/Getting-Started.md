# Getting Started 🏔️

This page gets you from zero to a running SlopeScript program. There are three
ways in, in increasing order of "setup": the **browser playground** (nothing to
install), the **single-file interpreter** (just Python), and a **`pip install`**
(gives you the `slope` command everywhere).

## 0. No install: the playground

The fastest way to try SlopeScript is the **[Playground](Playground)** — the
real interpreter compiled to WebAssembly, running entirely in your browser.
Pick an example, hit Run, and share your program as a link. Nothing is sent to a
server.

## 1. Requirements

Everything else needs **Python 3.8 or newer** and nothing else — SlopeScript has
**zero runtime dependencies**. Check your Python:

```bash
python3 --version
```

## 2. Run the single file

The entire language lives in one file, [`slopescript.py`](https://github.com/arnavj/SlopeScript/blob/main/slopescript.py).
Clone the repo and run a program directly:

```bash
git clone https://github.com/arnavj/slopescript.git
cd slopescript
python3 slopescript.py examples/hello.slope
```

You should see:

```
🎿 Hello from the slopes!
Welcome to SlopeScript!
```

## 3. Install the `slope` command

To get the `slope` command available anywhere on your machine:

```bash
pip install .
```

Now you can run programs and start the REPL from anywhere:

```bash
slope examples/hello.slope   # run a program
slope                        # start the interactive REPL
slope --version              # print the version
slope --help                 # usage
```

`slope run program.slope` also works, and you can pipe a program in on stdin:

```bash
cat examples/hello.slope | slope
```

For development, install in editable mode so your changes take effect
immediately:

```bash
pip install -e .
```

## 4. Your first program

Create a file called `first.slope`:

```slopescript
summit
  pack name = "skier"
  carve "Welcome to the mountain, {name}!"

  pack laps = 3
  liftline i in laps(laps)
    carve "Lap {i + 1} — dropping in! 🎿"
  runout
lodge
```

Run it:

```bash
slope first.slope
```

```
Welcome to the mountain, skier!
Lap 1 — dropping in! 🎿
Lap 2 — dropping in! 🎿
Lap 3 — dropping in! 🎿
```

### What just happened?

- Every program is wrapped in **`summit` … `lodge`** — the start and end of your
  run.
- **`pack name = ...`** declares a variable (you "pack your gear").
- **`carve`** prints. Text can embed `{expressions}` — that's string
  interpolation.
- **`liftline i in laps(3)`** is a counting for-loop; `laps(n)` produces
  `0, 1, 2`.
- Every block ends at **`runout`** — the flat bit at the bottom of a slope.

## 5. Where to go next

- **[The Language Tour](The-Language-Tour)** — the whole language in 60 seconds.
- **[The REPL](REPL)** — experiment line by line.
- **[Examples](Examples)** — a guided tour of 15+ runnable sample programs.
- **[Cheat Sheet](Cheat-Sheet)** — every keyword on one page.

## 6. Running the tests

The project ships with a 126-test suite:

```bash
python3 -m unittest discover tests
```

CI runs this suite across Python 3.8–3.13 and executes every example program.
