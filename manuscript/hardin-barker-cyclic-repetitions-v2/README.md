# Barker and Hardin's cyclic-repetition formulas and an extension of Fried's enumeration

Haobo Ma (ChronoAI Pte Ltd, Singapore), followed by Wenlin Zhang (National University of Singapore; ChronoAI Pte Ltd, Singapore). CC BY 4.0 (`cc-by-4.0`).

## Statements and sources

`note.tex` proves Colin Barker's rational generating function and radical formula in OEIS A268943, revision 8, FORMULA, 17 January 2019, and R. H. Hardin's empirical recurrence. Its alphabet-size theorem proves all column recurrences and the seven row polynomials in A268944, revision 4, FORMULA, 16 February 2016.

Equality events are adjacent equal pairs, including overlapping pairs. Their labels must advance by one modulo the alphabet size. Words are linear labeled arrays, not necklaces. The count of the empty word is one; the source generating function starts at length one and has constant term zero.

The note extends the enumeration to every loopless relation on a `q`-letter alphabet having constant indegree `d`. Its counts depend only on `q` and `d`. It also gives the generating function for words with each fixed number of equality events. These extensions are not conjectures posed in the two primary entries.

At `d=q-1` the relation is inequality, giving a new three-state derivation of Fried's known enumeration and all seven displayed row and column formulas in A269467. The earliest located version of that theorem is Sela Fried, *Proofs of some Conjectures from the OEIS*, arXiv:2410.07237v3, 26 October 2024, Section 2.8, Theorem 10, equation (18). The journal version is *Proofs of Several Conjectures From the OEIS*, Journal of Integer Sequences 28 (2025), Article 25.4.3, Section 3.2, Theorem 4, equation (2), published 2 August 2025. The two word conditions coincide only for two letters. Fried's displayed rational function includes the empty-word constant term.

The binary corollary recovers A027383's parity formulas, finite-sum formula and elementary recurrences, and proves that its balanced-substring condition is equivalent to alternating equality-event labels. The identities with A000027, A000290 and A007531 are included. Other tree, necklace, folding and arithmetic-sequence interpretations are outside the note's coverage. No claim of priority is made.

## Build

Use Tectonic 0.17.0:

```sh
tectonic --untrusted note.tex
```

Alternatively, use a LaTeX installation with `amsmath`, `amssymb`, `amsthm`, `booktabs`, `array`, `geometry` and `hyperref`:

```sh
pdflatex -interaction=nonstopmode -halt-on-error note.tex
pdflatex -interaction=nonstopmode -halt-on-error note.tex
```

The bibliography is in the main source. External figures and BibTeX are unnecessary.

## Exact finite checks

Python 3.10 or later, standard library only:

```sh
python3 verify.py --output checks.json
python3 verify_siblings.py --output sibling-checks.json
```

`verify.py` enumerates all 519,049 words for alphabet sizes 2 through 8 and lengths 0 through 6. It compares an independent forward automaton, the three-state enumeration and the scalar recurrence at 891 parameter pairs; checks the eight-letter radical formula in exact integer quadratic arithmetic through length 210; and checks seven polynomial identities and 32 source examples.

`verify_siblings.py` enumerates every loopless constant-indegree relation on alphabets of sizes 2 through 4: 176 relations and 227,626 words through length 5. It compares both total counts and counts by event number. It separately checks cyclic event histograms for 519,049 words, the binary balanced-substring equivalence for 2,047 words through length 10, the binary sum and recurrences through length 120, Fried's rational function against an independent last-letter/last-event automaton at 891 parameter pairs, and all seven A269467 row polynomials as exact coefficient identities. Finite checks have the scope recorded in their JSON outputs; the universal statements have written proofs in the note.

For the full OEIS tables:

```sh
mkdir -p oeis-data
curl -fLsS https://oeis.org/A268943/b268943.txt -o oeis-data/b268943.txt
curl -fLsS https://oeis.org/A268944/b268944.txt -o oeis-data/b268944.txt
python3 verify.py --oeis-dir oeis-data --output source-table-checks.json
```

`source-table-checks.json` records the SHA-256 of both numerical sources and comparison of all 210 and 9,999 terms, respectively. `source-fixtures.json` attributes its finite numerical fixtures to the relevant OEIS entries. External sources retain their own terms.

## Lean declaration scope

The scientific source is pinned to:

https://github.com/the-omega-institute/trureturing/blob/8a9173761a0a8ce40a4238793b5c18e452f76446/D5/S1/Words/Patterns/BarkerCyclicRepetitionCounting.lean

`D5.S1.Words.Patterns.BarkerCyclicRepetitionCounting.result` proves `claim`: for the literal eight-letter predicate, the zero-constant-term coefficient series exists uniquely, equals Barker's rational expression, and has the stated positive-index radical coefficients. In the same file, the auxiliary lemmas `count_recurrence` and `radical_count` cover positive indices at alphabet size eight. The empty-word extension, arbitrary-alphabet result, table identities, binary equivalence, regular-relation theorem and event-number formula have written proofs in `note.tex`.

## File integrity

`verification-scope.json` maps the pinned declarations, written proofs and finite checks. `manifest.json` gives the size and SHA-256 of each other source-archive member. The scientific archive contains the LaTeX, this README, metadata, the scope mapping, both checkers, attributed fixtures and their exact check outputs.
