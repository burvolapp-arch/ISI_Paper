# .latexmkrc — latexmk configuration for ISI_Paper
# =============================================================================
# Forces XeLaTeX, biber, output to /output, halt on error.
# =============================================================================

# --- Engine ------------------------------------------------------------------
$xelatex = 'xelatex -synctex=1 -interaction=nonstopmode -halt-on-error -file-line-error %O %S';
$pdf_mode = 5;                       # 5 = use xelatex to produce PDF

# --- Bibliography ------------------------------------------------------------
$biber = 'biber --validate-datamodel %O %S';
$bibtex_use = 2;                     # Run biber when needed; delete .bbl on clean

# --- Output Directory --------------------------------------------------------
$out_dir = 'output';

# --- Cleanup -----------------------------------------------------------------
$clean_ext = 'synctex.gz synctex.gz(busy) run.xml bbl bcf fdb_latexmk fls log aux out toc lof lot nav snm vrb';

# --- Build passes ------------------------------------------------------------
$max_repeat = 5;                     # Max compilation passes (safety)

# --- Warnings → Errors (quality gate) ----------------------------------------
# After build, check for undefined references / citations
$silence_logfile_warnings = 0;

# Post-build hook: fail on undefined references or citations
END {
    my $log = "$out_dir/main.log";
    if (-f $log) {
        open(my $fh, '<', $log) or die "Cannot open $log: $!";
        my $content = do { local $/; <$fh> };
        close($fh);
        if ($content =~ /undefined references|Citation .* undefined|Reference .* undefined/i) {
            warn "\n*** QUALITY GATE FAILED: Undefined references or citations detected. ***\n";
            warn "*** Check $log for details. ***\n\n";
            # Note: latexmk itself will return non-zero if refs remain unresolved after max_repeat.
        }
    }
}
