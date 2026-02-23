# =============================================================================
# ISI Paper 2 — Build System
# Zero-warning enforcement: build FAILS if any warning is detected
# =============================================================================

MAIN    := main
TEX     := pdflatex -interaction=nonstopmode
BIB     := bibtex
LOG     := $(MAIN).log

.PHONY: all clean distclean check audit

# ── Default target: full build with zero-warning gate ────────────────────────
all: $(MAIN).pdf check

# ── Full triple-pass build ───────────────────────────────────────────────────
$(MAIN).pdf: $(MAIN).tex $(wildcard sections/*.tex) $(wildcard tables/*.tex) \
             $(wildcard figures/*.tex) references.bib
	@echo "══ Pass 1/3 ═══════════════════════════════════════════════════"
	$(TEX) $(MAIN).tex > /dev/null 2>&1
	@echo "══ BibTeX ═════════════════════════════════════════════════════"
	$(BIB) $(MAIN) > /dev/null 2>&1 || true
	@echo "══ Pass 2/3 ═══════════════════════════════════════════════════"
	$(TEX) $(MAIN).tex > /dev/null 2>&1
	@echo "══ Pass 3/3 ═══════════════════════════════════════════════════"
	$(TEX) $(MAIN).tex > /dev/null 2>&1
	@echo "══ Build complete ══════════════════════════════════════════════"

# ── Zero-warning gate ───────────────────────────────────────────────────────
check: $(MAIN).pdf
	@echo "── Warning audit ─────────────────────────────────────────────"
	@OVF=$$(grep -c 'Overfull' $(LOG) || true); OVF=$${OVF:-0}; \
	 UNF=$$(grep -c 'Underfull' $(LOG) || true); UNF=$${UNF:-0}; \
	 LTX=$$(grep -c 'LaTeX Warning' $(LOG) || true); LTX=$${LTX:-0}; \
	 PKG=$$(grep -c 'Package.*Warning' $(LOG) || true); PKG=$${PKG:-0}; \
	 UND=$$(grep -ci 'undefined' $(LOG) || true); UND=$${UND:-0}; \
	 TOT=$$((OVF + UNF + LTX + PKG + UND)); \
	 echo "  Overfull:        $$OVF"; \
	 echo "  Underfull:       $$UNF"; \
	 echo "  LaTeX Warning:   $$LTX"; \
	 echo "  Package Warning: $$PKG"; \
	 echo "  Undefined refs:  $$UND"; \
	 echo "  ────────────────────"; \
	 echo "  TOTAL:           $$TOT"; \
	 if [ "$$TOT" -ne 0 ]; then \
	   echo ""; \
	   echo "✗ BUILD FAILED: $$TOT warning(s) detected."; \
	   echo "  Run 'make audit' for details."; \
	   exit 1; \
	 else \
	   echo ""; \
	   echo "✓ ZERO warnings — build is clean."; \
	 fi

# ── Detailed audit: print all warnings ──────────────────────────────────────
audit:
	@echo "── Overfull ──────────────────────────────────────────────────"
	@grep 'Overfull' $(LOG) 2>/dev/null || echo "  (none)"
	@echo "── Underfull ─────────────────────────────────────────────────"
	@grep 'Underfull' $(LOG) 2>/dev/null || echo "  (none)"
	@echo "── LaTeX Warnings ───────────────────────────────────────────"
	@grep 'LaTeX Warning' $(LOG) 2>/dev/null || echo "  (none)"
	@echo "── Package Warnings ─────────────────────────────────────────"
	@grep 'Package.*Warning' $(LOG) 2>/dev/null || echo "  (none)"
	@echo "── Undefined references ─────────────────────────────────────"
	@grep -i 'undefined' $(LOG) 2>/dev/null || echo "  (none)"

# ── Quick single-pass (development) ─────────────────────────────────────────
quick:
	$(TEX) $(MAIN).tex

# ── Clean auxiliary files ────────────────────────────────────────────────────
clean:
	rm -f $(MAIN).aux $(MAIN).bbl $(MAIN).blg $(MAIN).log $(MAIN).out \
	      $(MAIN).toc $(MAIN).lof $(MAIN).lot $(MAIN).fls $(MAIN).fdb_latexmk \
	      $(MAIN).synctex.gz

# ── Clean everything including PDF ──────────────────────────────────────────
distclean: clean
	rm -f $(MAIN).pdf
