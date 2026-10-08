# Slides

A ~15 minute talk covering the fundamentals through to key distribution.
21 slides, written in [Marp](https://marp.app) markdown.

- `slides.md` — the deck
- `images/` — generated, do not edit by hand
- `deck.pdf` — the rendered deck, what you present from

## Rendering

```bash
uv run python slides/build_images.py                       # rebuild the figures
npx @marp-team/marp-cli slides.md -o deck.pdf --allow-local-files --no-stdin
```

Swap `-o deck.pdf` for `-o slides.html` to get a deck that runs in a browser, or
`--preview` to watch it live while editing. `--no-stdin` matters: without it Marp
reads stdin instead of the file when run non-interactively.

Figures come from the protocol scripts in `03_Protocols` and `04_Algorithms`, so a
circuit on a slide cannot drift from the code that runs it.

## Running order

| # | Slide | |
| :-: | :--- | :--- |
| 1 | Title | |
| 2–3 | Kets, bras, normalisation, orthonormal basis | the 2D picture |
| 4–5 | Tensor product, the $ru$ vs $st$ test | |
| 6–7 | Worked examples: separable, then entangled | the core of the talk |
| 8–10 | $I$ and $Z$, $X$ and $Y$, Hadamard | follows `02_Gates/Single_Qubit_Gates.md` |
| 11 | Involutions | follows `02_Gates/Involutions.md` |
| 12–13 | CNOT, and a measured Bell pair | |
| 14–15 | Superdense coding | |
| 16–17 | Teleportation | |
| 18–19 | BB84 | |
| 20 | E91 | |
| 21 | Recap | |

Slides 6 and 7 are the ones worth slowing down on — everything after them is an
application of the same test.
