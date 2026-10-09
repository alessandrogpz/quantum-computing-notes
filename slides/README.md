# Slides

A ~15 minute talk covering the fundamentals through to key distribution.
27 slides, written in [Marp](https://marp.app) markdown.

- `slides.md` — the deck
- `images/` — generated, do not edit by hand
- `deck.pdf` — the rendered deck, what you present from
- `deck.pptx` — PowerPoint, one rendered image per slide

## Rendering

```bash
uv run python slides/build_images.py                       # rebuild the figures
npx @marp-team/marp-cli slides.md -o deck.pdf --allow-local-files --no-stdin
```

Swap `-o deck.pdf` for `-o slides.html` to get a deck that runs in a browser,
`-o deck.pptx` for PowerPoint, or `--preview` to watch it live while editing.

The `.pptx` holds one rendered image per slide, so it opens anywhere and looks
exactly like the PDF, but the text is not editable. Editing happens in `slides.md`.

Marp can emit real text shapes with `--pptx-editable` (needs LibreOffice), but the
maths suffers badly: subscripts collide with ket bars and matrix brackets flatten.
Not worth it for a deck this equation-heavy.

For presenting, `deck.pdf` beats both — no conversion, nothing to degrade.

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
