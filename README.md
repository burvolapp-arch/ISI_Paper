# ISI Paper — LaTeX Publishing Repository

> Institutional-grade LaTeX scaffolding for the ISI project.
> Compiles with **XeLaTeX + latexmk + Biber** to produce a journal-ready PDF.

---

## Quick Start

### Prerequisites

| Tool | Version | Check |
|------|---------|-------|
| TeX Live | 2025+ | `xelatex --version` |
| latexmk | 4.80+ | `latexmk --version` |
| Biber | 2.17+ | `biber --version` |
| VS Code | latest | `code --version` |
| LaTeX Workshop | latest | Install: `James-Yu.latex-workshop` |

### Build

```bash
chmod +x scripts/*.sh      # first time only
./scripts/build.sh          # → output/main.pdf
```

### Clean

```bash
./scripts/clean.sh          # removes all build artefacts in output/
```

### Watch (continuous rebuild)

```bash
./scripts/watch.sh          # rebuilds on file change; Ctrl+C to stop
```

### Lint (advisory)

```bash
./scripts/lint.sh           # runs chktex; never blocks, always exits 0
```

### VS Code

1. Install the **LaTeX Workshop** extension: `James-Yu.latex-workshop`
2. Open this folder in VS Code
3. Save any `.tex` file → auto-build triggers
4. PDF appears in `output/main.pdf`

> **Forward/inverse search** is configured for [Skim](https://skim-app.sourceforge.io/).
> Install Skim, then enable "Check for file changes" in Skim → Preferences → Sync.

---

## Repository Structure

```
ISI_Paper/
├── main.tex                    # Top-level orchestrator
├── bibliography.bib            # BibLaTeX bibliography database
├── .latexmkrc                  # latexmk configuration
├── .gitignore
│
├── preamble/
│   ├── packages.tex            # All \usepackage declarations
│   ├── formatting.tex          # Page layout, fonts, headings, captions
│   ├── macros.tex              # Project commands, helpers, colours
│   └── metadata.tex            # Title, authors, date, PDF metadata
│
├── sections/
│   ├── 00_abstract.tex
│   ├── 01_introduction.tex
│   ├── 02_literature_review.tex
│   ├── 03_methodology.tex
│   ├── 04_results.tex
│   ├── 05_discussion.tex
│   ├── 06_conclusion.tex
│   └── 07_appendix.tex         # Uncomment in main.tex when needed
│
├── figures/                    # All images (PDF, PNG, JPG)
├── tables/                     # LaTeX table fragments (\input from sections)
│
├── scripts/
│   ├── build.sh                # Full build
│   ├── clean.sh                # Remove artefacts
│   ├── lint.sh                 # chktex lint (advisory)
│   └── watch.sh                # Continuous rebuild
│
├── output/                     # Build output (gitignored)
│   └── main.pdf
│
├── .vscode/
│   └── settings.json           # LaTeX Workshop configuration
│
└── .github/
    └── workflows/
        └── ci.yml              # GitHub Actions: build on push/PR
```

---

## How To…

### Add a New Section

1. Create `sections/08_newsection.tex`:
   ```latex
   % sections/08_newsection.tex
   \section{New Section Title}\label{sec:new-section}

   Your content here.
   ```
2. Add `\input{sections/08_newsection}` in `main.tex` at the desired position.

### Add a Figure

1. Place the image file in `figures/` (prefer PDF for vector, PNG for raster).
2. Use the helper macro:
   ```latex
   \insfig{my-image.pdf}{0.8}{Caption text here.}{my-label}
   % Reference: \cref{fig:my-label}
   ```
   Or manually:
   ```latex
   \begin{figure}[htbp]
     \centering
     \includegraphics[width=0.8\textwidth]{figures/my-image.pdf}
     \caption{Caption text here.}
     \label{fig:my-label}
   \end{figure}
   ```

### Add a Table

1. Create `tables/my-table.tex` with just the tabular content:
   ```latex
   \begin{tabular}{lcc}
     \toprule
     Header A & Header B & Header C \\
     \midrule
     Row 1    & Data     & Data     \\
     Row 2    & Data     & Data     \\
     \bottomrule
   \end{tabular}
   ```
2. Include in a section using the helper:
   ```latex
   \instab{My Table Caption}{my-table.tex}{my-label}
   % Reference: \cref{tab:my-label}
   ```

### Add a Bibliography Entry

1. Add entries to `bibliography.bib` in standard BibTeX format:
   ```bibtex
   @article{smith2024example,
     author  = {Smith, John and Doe, Jane},
     title   = {An Example Article},
     journal = {Journal of Examples},
     year    = {2024},
     volume  = {1},
     pages   = {1--10},
     doi     = {10.1234/example},
   }
   ```
2. Cite in text:
   ```latex
   Recent work \parencite{smith2024example} shows...
   \textcite{smith2024example} demonstrated that...
   ```
3. Biber processes citations automatically during build.

### Cross-Referencing

Use `cleveref` for automatic reference formatting:
```latex
\cref{sec:introduction}     % → Section 1
\cref{fig:my-label}         % → Figure 1
\cref{tab:my-label}         % → Table 1
\Cref{sec:introduction}     % → Section 1  (sentence start)
```

---

## Quality Gates

| Gate | What it checks | When |
|------|---------------|------|
| Undefined refs | `\ref`, `\cref` to missing labels | Build (latexmk + post-hook) |
| Undefined citations | `\cite` to missing bib entries | Build (latexmk + post-hook) |
| Halt on error | Compilation errors stop the build | `-halt-on-error` flag |
| chktex lint | Style/syntax advisories | `./scripts/lint.sh` or CI (never blocks) |
| CI build | Full build on every push/PR | GitHub Actions |

### chktex (optional linting)

If `chktex` is installed (`which chktex`), LaTeX Workshop runs it automatically.
To install on macOS: it ships with TeX Live (already available).
To bypass a specific warning, add to the line:
```latex
Some text  % chktex 1
```

---

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Engine | XeLaTeX | Unicode support, system fonts, modern typography |
| Bibliography | biblatex + Biber | Full Unicode, flexible styles, native XeLaTeX compat |
| Citation style | `authoryear-comp` | Standard academic format, compact |
| Cross-refs | cleveref | Auto-formats "Figure 1", "Section 2" consistently |
| Fonts | TeX Gyre (Termes/Heros/Cursor) | Ship with TeX Live, no external deps, professional |
| Output dir | `output/` | Keeps root clean, gitignored |
| Build tool | latexmk | Handles multi-pass, dependency tracking automatically |

---

## Troubleshooting

**"Font not found"**: Ensure TeX Live 2025 is installed (`tlmgr install tex-gyre`).

**"Biber error"**: Run `./scripts/clean.sh` then `./scripts/build.sh` — stale `.bcf` files cause this.

**"Undefined references" persist**: Ensure `latexmk` runs enough passes (configured for up to 5 in `.latexmkrc`).

**VS Code not building**: Check that LaTeX Workshop is installed and `output/` directory exists.
