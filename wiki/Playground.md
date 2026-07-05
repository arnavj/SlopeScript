# Playground 🌐

The **SlopeScript Playground** runs the *real* interpreter in your browser — no
install, nothing sent to a server. It's the fastest way to try the language and
to share a program.

## What it is

The playground lives in [`playground/index.html`](https://github.com/arnavj/SlopeScript/blob/main/playground/index.html).
It's the actual `slopescript.py` interpreter compiled to **WebAssembly via
[Pyodide](https://pyodide.org/)**, so what runs in the browser is the same code
that runs on the CLI — not a re-implementation.

Features:

- An editor with a set of built-in examples.
- A **Run** button that executes entirely client-side.
- `chairlift` input handled through browser prompts.
- **Shareable program links** — your code is encoded in the URL, so you can send
  someone a program just by sending the link.

## Deploying it (GitHub Pages)

The repo ships a workflow at `.github/workflows/pages.yml` that publishes the
playground automatically. To turn it on for your fork:

1. Go to **Settings → Pages**.
2. Set **Source: GitHub Actions**.

Once enabled, every push deploys the playground to:

```
https://<your-user>.github.io/slopescript/
```

## What works in the browser vs. the CLI

Almost everything is identical. The differences are network-related, because the
browser sandbox routes HTTP through the browser itself:

| Feature | CLI | Playground |
|---|---|---|
| Full language (tricks, racks, lockers, patrol, …) | ✅ | ✅ |
| `chairlift` input | terminal | browser prompt |
| File I/O (`readFile`, `writeFile`, …) | ✅ | limited to the in-browser filesystem |
| `radioBase` / `radioJson` (HTTP GET) | ✅ | ✅ through the browser, **subject to CORS** |
| `radioPost` (HTTP POST) | ✅ | reports that it needs the CLI |

> **CORS:** browsers only allow cross-origin requests to servers that opt in.
> A GET that works from the CLI may be blocked in the playground if the target
> site doesn't send permissive CORS headers. That's a browser policy, not a
> SlopeScript limitation.

## When to use which

- **Playground** — trying the language, quick experiments, sharing a snippet,
  classroom demos on the lodge projector.
- **[The REPL](REPL)** — fast line-by-line iteration locally.
- **[Installed `slope`](Getting-Started)** — real programs, files, modules, and
  unrestricted HTTP.

---

Next: [Examples](Examples) — programs to open in the playground and read.
