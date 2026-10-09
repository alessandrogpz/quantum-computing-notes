# Slides

A ~15 minute talk covering the fundamentals through to key distribution.
27 slides, written in [Marp](https://marp.app) markdown.

- `slides.md` — the deck
- `images/` — generated, do not edit by hand
- `deck.pdf` — the rendered deck, what you present from
- `deck.pptx` — PowerPoint, one rendered image per slide
- `deck-editable.pptx` — PowerPoint with real text, for Google Slides

## Rendering

```bash
uv run python slides/build_images.py                       # rebuild the figures
npx @marp-team/marp-cli slides.md -o deck.pdf --allow-local-files --no-stdin
```

Swap `-o deck.pdf` for `-o slides.html` to get a deck that runs in a browser,
`-o deck.pptx` for PowerPoint, or `--preview` to watch it live while editing.

### Which PowerPoint file

Two exist, and they trade off against each other:

| | `deck.pptx` | `deck-editable.pptx` |
| :--- | :--- | :--- |
| contents | one image per slide | real text shapes |
| maths | pixel-perfect | subscripts collide with ket bars, loose spacing |
| in Google Slides | soft — Slides resamples the bitmap | crisp, and editable |
| size | 4.8 MB | 0.5 MB |

Use the image version to present from, and the editable one only if the deck has
to live inside Google Slides or PowerPoint. The editable build needs LibreOffice:

```bash
npx @marp-team/marp-cli slides.md -o deck-editable.pptx --allow-local-files --no-stdin --pptx-editable
```

For presenting, `deck.pdf` beats both — no conversion, nothing to degrade. `--no-stdin` matters: without it Marp
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
| 9–11 | $I$ and $Z$, $X$ and $Y$, Hadamard | follows `02_Gates/Single_Qubit_Gates.md` |
| 12 | Why Hadamard specifically | |
| 13 | Involutions | follows `02_Gates/Involutions.md` |
| 14–15 | CNOT, and a measured Bell pair | |
| 16 | **Protocols** — section break | |
| 17–18 | Superdense coding | |
| 19–20 | Teleportation | |
| 21 | **Key distribution** — section break | |
| 22 | BB84 — reading the circuit, and why the order matters | |
| 23 | BB84 — eight rounds worked through | the one that makes it click |
| 24 | BB84 — what actually becomes key | |
| 25 | BB84 — what Eve costs | |
| 26 | E91 | |
| 27 | Recap | |

Three section breaks split the talk into acts: foundations, gates, then the
protocols — first moving information, then detecting an eavesdropper.

Slides 6 and 7 are the ones worth slowing down on — everything after them is an
application of the same test.
