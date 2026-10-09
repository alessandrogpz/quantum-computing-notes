# Slides

A ~15 minute talk covering the fundamentals through to key distribution.
28 slides, written in [Marp](https://marp.app) markdown.

- `slides.md` — the deck
- `images/` — generated, do not edit by hand
- `deck.pdf` — the rendered deck, what you present from
- `deck.pptx` — PowerPoint, if you need it

## Rendering

```bash
uv run python slides/build_images.py                       # rebuild the figures
npx @marp-team/marp-cli slides.md -o deck.pdf --allow-local-files --no-stdin
```

Swap `-o deck.pdf` for `-o slides.html` to get a deck that runs in a browser,
`-o deck.pptx` for PowerPoint, or `--preview` to watch it live while editing.

The `.pptx` embeds one rendered image per slide, so it opens anywhere but the text
is not editable in PowerPoint. Editing happens in `slides.md`. (Marp can emit
editable shapes with `--pptx-editable`, but that needs LibreOffice installed.) `--no-stdin` matters: without it Marp
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
| 8 | **Gates** — section break | |
| 9–10 | $I$ and $Z$, $X$ and $Y$ | follows `02_Gates/Single_Qubit_Gates.md` |
| 11 | Why three Paulis, and why $2\times2$ | the Bloch sphere, in passing |
| 12 | Hadamard | |
| 13 | Why Hadamard specifically | |
| 14 | Involutions | follows `02_Gates/Involutions.md` |
| 15–16 | CNOT, and a measured Bell pair | |
| 17 | **Protocols** — section break | |
| 18–19 | Superdense coding | |
| 20–21 | Teleportation | |
| 22 | **Key distribution** — section break | |
| 23 | BB84 — reading the circuit, and why the order matters | |
| 24 | BB84 — eight rounds worked through | the one that makes it click |
| 25 | BB84 — what actually becomes key | |
| 26 | BB84 — what Eve costs | |
| 27 | E91 | |
| 28 | Recap | |

Three section breaks split the talk into acts: foundations, gates, then the
protocols — first moving information, then detecting an eavesdropper.

Slides 6 and 7 are the ones worth slowing down on — everything after them is an
application of the same test.
