# TODO

Parked material — read and understood well enough to file, but not yet worked
through. Sorted last on purpose; nothing here blocks the numbered sections.

| Note | Why it is parked |
| :--- | :--- |
| [Open_Questions](Open_Questions.md) | Book chapters skipped over, and points to verify against the source |
| [Real_vs_Complex_Amplitudes](Real_vs_Complex_Amplitudes.md) | Complex amplitudes are deliberately deferred — this records what that costs |

## When to pull each one out

**[Open_Questions](Open_Questions.md)** — the two book chapters (Alice/Bob/Eve encryption, and the
up-up-down-down problem) come *before* [Foundations](../01_Foundations/00_Foundations.md)
in the book, so the vault currently starts mid-way through. Worth closing whenever
something earlier feels like it is missing a foundation.

**[Real_vs_Complex_Amplitudes](Real_vs_Complex_Amplitudes.md)** — the trigger is concrete: the **Bloch sphere**,
or the $S$/$T$ gates, whichever comes first. [Shors_Algorithm](../04_Algorithms/Shors_Algorithm.md) has already
crossed it — its inverse QFT uses phases $e^{-i\pi/2^k}$ that have no real form, so
that note is the worked example of why this cannot be deferred forever. Until then real amplitudes are enough,
and the note explains why that is a legitimate simplification rather than a gap.

> [!tip] Cheap insurance
> The four habits at the end of [Real_vs_Complex_Amplitudes](Real_vs_Complex_Amplitudes.md) cost nothing today
> and make the eventual switch free. The main one: write
> $|a_0|^2 + |a_1|^2 = 1$, never $a_0^2 + a_1^2 = 1$.
