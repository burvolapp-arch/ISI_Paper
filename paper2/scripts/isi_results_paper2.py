#!/usr/bin/env python3
"""
ISI Results Paper 2 -- Computation Engine (Expanded)
=====================================================
Reads the ISI v1.0 EU-27 snapshot (embedded) and produces all derived
tables for Paper 2.

Computations:
  1.  Axis dominance table
  2.  Variance contribution decomposition (full, with own vs cross)
  3.  Leave-one-axis-out (LOO) with Spearman and Kendall tau
  4.  Z-score standardized composite
  5.  Dirichlet weight perturbation (Monte Carlo)
  6.  Winsorization (cap Axis 4 & 6 at P95)
  7.  Top-5 / Bottom-5 per axis
  8.  Lorenz curve coordinates
  9.  Axis rank tables (Appendix A)
  10. Histogram / ECDF coordinates
  11. Radar plot data per country
  12. Boxplot statistics
  13. Rank elasticity to axis perturbation
  14. Axis contribution to rank differentiation (R-squared, partial corr)
  15. Classification compression diagnostics
  16. Defence axis structural analysis
  17. Compensability analysis
  18. Geographic / structural correlates
  19. Correlation t-statistics
  20. Spearman correlation matrix
  21. LOO individual axis tables (6 tables for appendix)
  22. Multiple regression diagnostics

Usage:
    python isi_results_paper2.py

No external dependencies beyond numpy.
"""

import numpy as np
import os

AXIS_NAMES = [
    "Financial", "Energy", "Technology",
    "Defence", "Critical Inputs", "Logistics"
]
AXIS_SLUGS = [
    "financial", "energy", "technology",
    "defence", "critical_inputs", "logistics"
]

# fmt: off
DATA = [
    ("MT", "Malta",        1,  0.51748148, "highly_concentrated",     0.13998786, 0.35068126, 0.20546991, 1.00000000, 0.40874987, 1.00000000),
    ("CY", "Cyprus",       2,  0.46821264, "moderately_concentrated", 0.12407171, 0.34768252, 0.22438354, 0.74847998, 0.42359750, 0.94106062),
    ("IE", "Ireland",      3,  0.42802519, "moderately_concentrated", 0.14666620, 0.46472525, 0.58695939, 0.44887460, 0.30719544, 0.61373023),
    ("DK", "Denmark",      4,  0.42442738, "moderately_concentrated", 0.12401663, 0.47029821, 0.14995928, 0.72368274, 0.43629935, 0.64230809),
    ("HR", "Croatia",      5,  0.40434768, "moderately_concentrated", 0.27299265, 0.35125471, 0.17343982, 0.74648317, 0.52392772, 0.35798800),
    ("FI", "Finland",      6,  0.40205136, "moderately_concentrated", 0.11775073, 0.36268783, 0.19789321, 0.38964518, 0.54699996, 0.79733123),
    ("SE", "Sweden",       7,  0.39871532, "moderately_concentrated", 0.11646504, 0.32721403, 0.11982797, 0.88107943, 0.19257891, 0.75512656),
    ("AT", "Austria",      8,  0.38249806, "moderately_concentrated", 0.14903467, 0.45581191, 0.26057910, 0.58506379, 0.31857781, 0.52592111),
    ("IT", "Italy",        9,  0.37386086, "moderately_concentrated", 0.18753526, 0.30781423, 0.14103384, 0.92057651, 0.20839534, 0.47781001),
    ("SI", "Slovenia",     10, 0.36979186, "moderately_concentrated", 0.11917574, 0.40540014, 0.35739912, 0.66661871, 0.22301125, 0.44714621),
    ("EL", "Greece",       11, 0.36537350, "moderately_concentrated", 0.20078311, 0.33541623, 0.16272142, 0.55148593, 0.22200621, 0.71982808),
    ("LU", "Luxembourg",   12, 0.36016893, "moderately_concentrated", 0.11462818, 0.35980871, 0.20019721, 0.64483831, 0.22295831, 0.61858285),
    ("EE", "Estonia",      13, 0.34332177, "moderately_concentrated", 0.18172493, 0.43935251, 0.22713142, 0.35561474, 0.38622776, 0.46987927),
    ("BG", "Bulgaria",     14, 0.34027984, "moderately_concentrated", 0.16052965, 0.35711773, 0.15204272, 0.86064518, 0.14843767, 0.36290606),
    ("NL", "Netherlands",  15, 0.33515702, "moderately_concentrated", 0.12107826, 0.31992851, 0.12527375, 0.95955396, 0.13018835, 0.35491930),
    ("HU", "Hungary",      16, 0.32966227, "moderately_concentrated", 0.12222969, 0.38580312, 0.22538122, 0.54471981, 0.23405214, 0.46578765),
    ("PT", "Portugal",     17, 0.32173430, "moderately_concentrated", 0.18303606, 0.34860414, 0.19766062, 0.43376254, 0.25955617, 0.50778629),
    ("RO", "Romania",      18, 0.31864192, "moderately_concentrated", 0.20033340, 0.40546401, 0.29691153, 0.56353195, 0.15814280, 0.28746783),
    ("CZ", "Czechia",      19, 0.31796630, "moderately_concentrated", 0.16116762, 0.38082003, 0.18242269, 0.48413737, 0.16976911, 0.52948100),
    ("PL", "Poland",       20, 0.29561321, "moderately_concentrated", 0.13314812, 0.33487780, 0.20845359, 0.44326493, 0.16532767, 0.48860717),
    ("BE", "Belgium",      21, 0.28796781, "moderately_concentrated", 0.15348744, 0.30789144, 0.29454573, 0.44734854, 0.17248330, 0.35205038),
    ("DE", "Germany",      22, 0.26788694, "moderately_concentrated", 0.10186464, 0.32908790, 0.09762824, 0.58266751, 0.22312039, 0.27295297),
    ("LT", "Lithuania",    23, 0.26540520, "moderately_concentrated", 0.13349636, 0.33747627, 0.24172279, 0.40227798, 0.13056067, 0.34689716),
    ("ES", "Spain",        24, 0.26093977, "moderately_concentrated", 0.14554195, 0.30187479, 0.19263249, 0.38088569, 0.11235234, 0.43235135),
    ("LV", "Latvia",       25, 0.24695137, "mildly_concentrated",     0.12316988, 0.36522282, 0.13309607, 0.34079636, 0.15120012, 0.36822299),
    ("SK", "Slovakia",     26, 0.23641567, "mildly_concentrated",     0.16163673, 0.39995460, 0.21649186, 0.00000000, 0.15490434, 0.48550648),
    ("FR", "France",       27, 0.23567126, "mildly_concentrated",     0.10039135, 0.30911838, 0.12001059, 0.37034617, 0.16122463, 0.35293643),
]
# fmt: on

N = len(DATA)
assert N == 27

ISO   = [d[0] for d in DATA]
NAMES = [d[1] for d in DATA]
RANKS = np.array([d[2] for d in DATA])
COMP  = np.array([d[3] for d in DATA])
CLASS = [d[4] for d in DATA]
AXES  = np.array([[d[5+j] for j in range(6)] for d in DATA])

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tables")
os.makedirs(OUT_DIR, exist_ok=True)

def write_table(filename, content):
    path = os.path.join(OUT_DIR, filename)
    with open(path, "w") as f:
        f.write(content)
    print(f"  Written: {path}")

def rankdata(x):
    n = len(x)
    order = np.argsort(-x)
    ranks = np.empty(n, dtype=float)
    ranks[order] = np.arange(1, n+1, dtype=float)
    return ranks

def spearman_corr(r1, r2):
    d = r1 - r2
    n = len(r1)
    return 1.0 - (6.0 * np.sum(d**2)) / (n * (n**2 - 1))

def kendall_tau(r1, r2):
    n = len(r1)
    concordant = 0
    discordant = 0
    for i in range(n):
        for j in range(i+1, n):
            s1 = np.sign(r1[i] - r1[j])
            s2 = np.sign(r2[i] - r2[j])
            prod = s1 * s2
            if prod > 0:
                concordant += 1
            elif prod < 0:
                discordant += 1
    pairs = 0.5 * n * (n - 1)
    return (concordant - discordant) / pairs if pairs > 0 else 0.0

def pearson_corr(x, y):
    mx, my = np.mean(x), np.mean(y)
    num = np.sum((x - mx) * (y - my))
    den = np.sqrt(np.sum((x - mx)**2) * np.sum((y - my)**2))
    return num / den if den > 0 else 0.0


# ===========================================================================
# 1. AXIS DOMINANCE TABLE
# ===========================================================================
print("\n" + "="*72)
print("1. AXIS DOMINANCE")
print("="*72)

max_axis_idx = np.argmax(AXES, axis=1)
second_max_idx = np.zeros(N, dtype=int)
for i in range(N):
    sorted_idx = np.argsort(-AXES[i])
    second_max_idx[i] = sorted_idx[1]

axis_dom_counts = np.zeros(6, dtype=int)
for i in range(N):
    axis_dom_counts[max_axis_idx[i]] += 1

for j in range(6):
    print(f"  {AXIS_NAMES[j]:20s}: {axis_dom_counts[j]}")

lines = []
lines.append("% Table T7: Axis dominance per country")
lines.append("\\begin{longtable}{@{}rlS[table-format=1.8]lS[table-format=1.8]l@{}}")
lines.append("\\caption{Axis dominance per country: highest- and second-highest-scoring axes.}")
lines.append("\\label{tab:axis-dominance}\\\\")
lines.append("\\toprule")
lines.append("{\\textbf{Rk}} & {\\textbf{Country}} & {\\textbf{Max Score}} & {\\textbf{Max Axis}} & {\\textbf{2nd Score}} & {\\textbf{2nd Axis}} \\\\")
lines.append("\\midrule")
lines.append("\\endfirsthead")
lines.append("\\caption[]{Axis dominance per country (continued).}\\\\")
lines.append("\\toprule")
lines.append("{\\textbf{Rk}} & {\\textbf{Country}} & {\\textbf{Max Score}} & {\\textbf{Max Axis}} & {\\textbf{2nd Score}} & {\\textbf{2nd Axis}} \\\\")
lines.append("\\midrule")
lines.append("\\endhead")
lines.append("\\bottomrule")
lines.append("\\endlastfoot")
for i in range(N):
    mi = max_axis_idx[i]
    si = second_max_idx[i]
    lines.append(f"  {RANKS[i]:.0f} & {NAMES[i]} & {AXES[i,mi]:.8f} & {AXIS_NAMES[mi]} & {AXES[i,si]:.8f} & {AXIS_NAMES[si]} \\\\")
lines.append("\\end{longtable}")
write_table("T07_axis_dominance.tex", "\n".join(lines))


# ===========================================================================
# 2. VARIANCE CONTRIBUTION DECOMPOSITION (FULL)
# ===========================================================================
print("\n" + "="*72)
print("2. VARIANCE CONTRIBUTION (FULL)")
print("="*72)

axis_vars = np.var(AXES, axis=0, ddof=0)
cov_matrix = np.cov(AXES.T, ddof=0)
total_composite_var = np.var(COMP, ddof=0)
var_decomp_check = np.sum(cov_matrix) / 36.0

print(f"  Composite variance (direct):    {total_composite_var:.10f}")
print(f"  Composite variance (from cov):  {var_decomp_check:.10f}")

marginal_contrib = np.sum(cov_matrix, axis=1) / 36.0
pct_contrib = marginal_contrib / var_decomp_check * 100.0

own_var_share = np.array([cov_matrix[j, j] / 36.0 for j in range(6)])
cov_share = np.array([sum(cov_matrix[j, k] / 36.0 for k in range(6) if k != j) for j in range(6)])

total_own = sum(cov_matrix[j, j] for j in range(6)) / 36.0
total_cross = sum(cov_matrix[j, k] for j in range(6) for k in range(6) if j != k) / 36.0
print(f"  Total own-variance:   {total_own:.10f} ({total_own/var_decomp_check*100:.2f}%)")
print(f"  Total cross-covar:    {total_cross:.10f} ({total_cross/var_decomp_check*100:.2f}%)")

for j in range(6):
    print(f"  {AXIS_NAMES[j]:20s}: var={axis_vars[j]:.8f}  marginal={marginal_contrib[j]:.8f}  pct={pct_contrib[j]:.2f}%")
print(f"  Defence+Logistics:    {pct_contrib[3]+pct_contrib[5]:.2f}%")

# T08: summary
lines = []
lines.append("% Table T8: Variance contribution decomposition")
lines.append("\\begin{table}[htbp]")
lines.append("\\centering")
lines.append("\\caption{Variance contribution decomposition of the ISI composite.  Each axis's")
lines.append("marginal contribution equals $(1/36)\\sum_{k=1}^{6}\\operatorname{Cov}(A_j, A_k)$,")
lines.append("reflecting both own-variance and covariance with other axes.}")
lines.append("\\label{tab:variance-decomp}")
lines.append("\\begin{tabular}{@{}lS[table-format=1.8]S[table-format=1.8]S[table-format=2.2]@{}}")
lines.append("\\toprule")
lines.append("{\\textbf{Axis}} & {\\textbf{Var (pop.)}} & {\\textbf{Marginal Contrib.}} & {\\textbf{\\% of Composite Var}} \\\\")
lines.append("\\midrule")
for j in range(6):
    lines.append(f"  {AXIS_NAMES[j]} & {axis_vars[j]:.8f} & {marginal_contrib[j]:.8f} & {pct_contrib[j]:.2f} \\\\")
lines.append("\\midrule")
lines.append(f"  Total & {np.sum(axis_vars):.8f} & {var_decomp_check:.8f} & {np.sum(pct_contrib):.2f} \\\\")
lines.append("\\bottomrule")
lines.append("\\end{tabular}")
lines.append("\\end{table}")
write_table("T08_variance_decomp.tex", "\n".join(lines))

# T08b: detailed own vs cross
lines = []
lines.append("% Table T8b: Detailed own-variance vs covariance decomposition")
lines.append("\\begin{table}[htbp]")
lines.append("\\centering")
lines.append("\\caption{Decomposition of each axis's marginal contribution into own-variance and")
lines.append("cross-covariance components.  Own: $(1/36)\\operatorname{Var}(A_j)$.")
lines.append("Cross: $(1/36)\\sum_{k \\neq j}\\operatorname{Cov}(A_j, A_k)$.}")
lines.append("\\label{tab:variance-decomp-detail}")
lines.append("\\small")
lines.append("\\begin{tabular}{@{}l S[table-format=1.8] S[table-format=+1.8] S[table-format=1.8] S[table-format=2.2] S[table-format=+2.2] S[table-format=2.2]@{}}")
lines.append("\\toprule")
lines.append("{\\textbf{Axis}} & {\\textbf{Own Var}} & {\\textbf{Cross Cov}} & {\\textbf{Marginal}} & {\\textbf{\\% Own}} & {\\textbf{\\% Cross}} & {\\textbf{\\% Total}} \\\\")
lines.append("\\midrule")
for j in range(6):
    pct_own = own_var_share[j] / var_decomp_check * 100
    pct_cross = cov_share[j] / var_decomp_check * 100
    lines.append(f"  {AXIS_NAMES[j]} & {own_var_share[j]:.8f} & {cov_share[j]:+.8f} & {marginal_contrib[j]:.8f} & {pct_own:.2f} & {pct_cross:+.2f} & {pct_contrib[j]:.2f} \\\\")
lines.append("\\midrule")
lines.append(f"  Total & {total_own:.8f} & {total_cross:+.8f} & {var_decomp_check:.8f} & {total_own/var_decomp_check*100:.2f} & {total_cross/var_decomp_check*100:.2f} & 100.00 \\\\")
lines.append("\\bottomrule")
lines.append("\\end{tabular}")
lines.append("\\end{table}")
write_table("T08b_variance_decomp_detail.tex", "\n".join(lines))

# TE1: Full covariance matrix
lines = []
lines.append("% Table TE1: Full 6x6 population covariance matrix")
lines.append("\\begin{table}[htbp]")
lines.append("\\centering")
lines.append("\\caption{Population covariance matrix of the six ISI axes, EU-27, 2024.}")
lines.append("\\label{tab:cov-matrix}")
lines.append("\\small")
lines.append("\\sisetup{table-format=+1.6}")
lines.append("\\begin{tabular}{@{}l S S S S S S@{}}")
lines.append("\\toprule")
lines.append(" & {\\textbf{Fin.}} & {\\textbf{Ene.}} & {\\textbf{Tec.}} & {\\textbf{Def.}} & {\\textbf{Crit.}} & {\\textbf{Log.}} \\\\")
lines.append("\\midrule")
for j in range(6):
    row = f"  {AXIS_NAMES[j]}"
    for k in range(6):
        row += f" & {cov_matrix[j,k]:+.6f}"
    row += " \\\\"
    lines.append(row)
lines.append("\\bottomrule")
lines.append("\\end{tabular}")
lines.append("\\end{table}")
write_table("TE1_cov_matrix.tex", "\n".join(lines))


# ===========================================================================
# 3. LEAVE-ONE-AXIS-OUT (LOO)
# ===========================================================================
print("\n" + "="*72)
print("3. LEAVE-ONE-AXIS-OUT (LOO)")
print("="*72)

baseline_ranks = rankdata(COMP)

loo_composites = np.zeros((N, 6))
loo_ranks = np.zeros((N, 6))
loo_spearman = np.zeros(6)
loo_kendall = np.zeros(6)

for j in range(6):
    mask = [k for k in range(6) if k != j]
    loo_comp = np.mean(AXES[:, mask], axis=1)
    loo_composites[:, j] = loo_comp
    lr = rankdata(loo_comp)
    loo_ranks[:, j] = lr
    loo_spearman[j] = spearman_corr(baseline_ranks, lr)
    loo_kendall[j] = kendall_tau(baseline_ranks, lr)
    print(f"  Drop {AXIS_NAMES[j]:20s}: Spearman={loo_spearman[j]:.6f}  Kendall={loo_kendall[j]:.6f}")

rank_displacement = np.zeros((N, 6), dtype=int)
for i in range(N):
    for j in range(6):
        rank_displacement[i, j] = int(baseline_ranks[i] - loo_ranks[i, j])

max_rank_change = np.max(np.abs(rank_displacement), axis=1)
mean_abs_disp = np.mean(np.abs(rank_displacement), axis=0)
max_abs_disp = np.max(np.abs(rank_displacement), axis=0)

# T09: LOO summary with Kendall
lines = []
lines.append("% Table T9: LOO sensitivity summary")
lines.append("\\begin{table}[htbp]")
lines.append("\\centering")
lines.append("\\caption{Leave-one-axis-out (LOO) rank sensitivity.  Spearman $\\rho$ and Kendall")
lines.append("$\\tau$ measure rank-order agreement between the baseline and each LOO ranking.")
lines.append("Mean $|\\Delta|$ and Max $|\\Delta|$ report the average and maximum absolute rank")
lines.append("displacement across the 27 countries.}")
lines.append("\\label{tab:loo-summary}")
lines.append("\\begin{tabular}{@{}l S[table-format=1.6] S[table-format=1.6] S[table-format=1.2] r@{}}")
lines.append("\\toprule")
lines.append("{\\textbf{Excluded Axis}} & {$\\boldsymbol{\\rho}$ \\textbf{(Spearman)}} & {$\\boldsymbol{\\tau}$ \\textbf{(Kendall)}} & {\\textbf{Mean} $|\\Delta|$} & {\\textbf{Max} $|\\Delta|$} \\\\")
lines.append("\\midrule")
for j in range(6):
    lines.append(f"  {AXIS_NAMES[j]} & {loo_spearman[j]:.6f} & {loo_kendall[j]:.6f} & {mean_abs_disp[j]:.2f} & {int(max_abs_disp[j])} \\\\")
lines.append("\\bottomrule")
lines.append("\\end{tabular}")
lines.append("\\end{table}")
write_table("T09_loo_summary.tex", "\n".join(lines))

# TE2: Full rank displacement matrix
lines = []
lines.append("% Table TE2: Full rank displacement matrix (signed)")
lines.append("\\begin{landscape}")
lines.append("\\begin{longtable}{@{}rl rrrrrr r@{}}")
lines.append("\\caption{Signed rank displacement matrix: baseline rank minus LOO rank for each axis.")
lines.append("Positive values indicate the country ranks higher (more concentrated) when the axis is removed;")
lines.append("negative values indicate it ranks lower.}")
lines.append("\\label{tab:rank-displacement}\\\\")
lines.append("\\toprule")
hdr = "{\\textbf{Rk}} & {\\textbf{Country}}"
for j in range(6):
    short = AXIS_NAMES[j][:4]
    hdr += f" & {{$\\Delta(-${short})}}"
hdr += " & {$|\\Delta|_{\\max}$} \\\\"
lines.append(hdr)
lines.append("\\midrule")
lines.append("\\endfirsthead")
lines.append("\\caption[]{Rank displacement matrix (continued).}\\\\")
lines.append("\\toprule")
lines.append(hdr)
lines.append("\\midrule")
lines.append("\\endhead")
lines.append("\\bottomrule")
lines.append("\\endlastfoot")
order = np.argsort(baseline_ranks)
for i in order:
    row = f"  {int(baseline_ranks[i])} & {NAMES[i]}"
    for j in range(6):
        row += f" & {rank_displacement[i,j]:+d}"
    row += f" & {int(max_rank_change[i])} \\\\"
    lines.append(row)
lines.append("\\end{longtable}")
lines.append("\\end{landscape}")
write_table("TE2_rank_displacement.tex", "\n".join(lines))

# TB1: LOO detailed ranks
lines = []
lines.append("% Appendix Table: LOO detailed ranks")
lines.append("\\begin{longtable}{@{}rl" + "r"*6 + "r@{}}")
lines.append("\\caption{Detailed rank comparison: baseline vs.\\ each leave-one-axis-out variant.")
lines.append("Columns show the rank under each LOO composite.  $\\Delta_{\\max}$ is the")
lines.append("maximum absolute rank change across all six LOO variants.}")
lines.append("\\label{tab:loo-detail}\\\\")
lines.append("\\toprule")
hdr = "{\\textbf{Rk}} & {\\textbf{Country}}"
for j in range(6):
    short = AXIS_SLUGS[j][:4].capitalize()
    hdr += f" & {{\\textbf{{$-${short}}}}}"
hdr += " & {$\\boldsymbol{\\Delta_{\\max}}$} \\\\"
lines.append(hdr)
lines.append("\\midrule")
lines.append("\\endfirsthead")
lines.append("\\caption[]{LOO detailed ranks (continued).}\\\\")
lines.append("\\toprule")
lines.append(hdr)
lines.append("\\midrule")
lines.append("\\endhead")
lines.append("\\bottomrule")
lines.append("\\endlastfoot")
for i in range(N):
    row = f"  {int(baseline_ranks[i])} & {NAMES[i]}"
    for j in range(6):
        row += f" & {int(loo_ranks[i,j])}"
    row += f" & {int(max_rank_change[i])} \\\\"
    lines.append(row)
lines.append("\\end{longtable}")
write_table("TB1_loo_detail.tex", "\n".join(lines))

print("  Most axis-sensitive countries:")
sens_order = np.argsort(-max_rank_change)
for idx in sens_order[:10]:
    print(f"    {NAMES[idx]:15s}: max_displacement={int(max_rank_change[idx])}")


# ===========================================================================
# 4. Z-SCORE STANDARDIZED COMPOSITE
# ===========================================================================
print("\n" + "="*72)
print("4. Z-SCORE STANDARDIZED COMPOSITE")
print("="*72)

axis_means = np.mean(AXES, axis=0)
axis_stds_pop = np.std(AXES, axis=0, ddof=0)
Z = (AXES - axis_means) / axis_stds_pop
z_composite = np.mean(Z, axis=1)
z_ranks = rankdata(z_composite)
z_spearman = spearman_corr(baseline_ranks, z_ranks)
z_kendall = kendall_tau(baseline_ranks, z_ranks)
print(f"  Spearman rho: {z_spearman:.6f}")
print(f"  Kendall tau:  {z_kendall:.6f}")

lines = []
lines.append("% Table T10: Z-score standardized composite rank comparison")
lines.append("\\begin{longtable}{@{}rlS[table-format=1.8]rS[table-format=2.8]rr@{}}")
lines.append("\\caption{Rank comparison: baseline ISI vs.\\ z-score standardized composite.")
lines.append("The z-score composite re-centres each axis to mean zero and unit population")
lines.append("standard deviation before averaging.  Spearman $\\rho = " + f"{z_spearman:.6f}" + "$,")
lines.append("Kendall $\\tau = " + f"{z_kendall:.6f}" + "$.}")
lines.append("\\label{tab:zscore-ranks}\\\\")
lines.append("\\toprule")
lines.append("{\\textbf{Rk}} & {\\textbf{Country}} & {\\textbf{Baseline}} & {\\textbf{Rk (base)}} & {\\textbf{Z-Composite}} & {\\textbf{Rk (z)}} & {$\\boldsymbol{\\Delta}$} \\\\")
lines.append("\\midrule")
lines.append("\\endfirsthead")
lines.append("\\caption[]{Z-score rank comparison (continued).}\\\\")
lines.append("\\toprule")
lines.append("{\\textbf{Rk}} & {\\textbf{Country}} & {\\textbf{Baseline}} & {\\textbf{Rk (base)}} & {\\textbf{Z-Composite}} & {\\textbf{Rk (z)}} & {$\\boldsymbol{\\Delta}$} \\\\")
lines.append("\\midrule")
lines.append("\\endhead")
lines.append("\\bottomrule")
lines.append("\\endlastfoot")
order = np.argsort(baseline_ranks)
for i in order:
    delta = int(abs(baseline_ranks[i] - z_ranks[i]))
    lines.append(f"  {int(baseline_ranks[i])} & {NAMES[i]} & {COMP[i]:.8f} & {int(baseline_ranks[i])} & {z_composite[i]:.8f} & {int(z_ranks[i])} & {delta} \\\\")
lines.append("\\end{longtable}")
write_table("T10_zscore_ranks.tex", "\n".join(lines))


# ===========================================================================
# 5. DIRICHLET WEIGHT PERTURBATION (MONTE CARLO)
# ===========================================================================
print("\n" + "="*72)
print("5. DIRICHLET WEIGHT PERTURBATION")
print("="*72)

np.random.seed(20240222)
N_MC = 10000
alpha = np.ones(6) * 10.0

mc_ranks = np.zeros((N, N_MC))
for t in range(N_MC):
    w = np.random.dirichlet(alpha)
    mc_comp = AXES @ w
    mc_ranks[:, t] = rankdata(mc_comp)

mean_rank = np.mean(mc_ranks, axis=1)
std_rank = np.std(mc_ranks, axis=1, ddof=0)
p5_rank = np.percentile(mc_ranks, 5, axis=1)
p95_rank = np.percentile(mc_ranks, 95, axis=1)
prob_top5 = np.mean(mc_ranks <= 5, axis=1) * 100.0
prob_top10 = np.mean(mc_ranks <= 10, axis=1) * 100.0

lines = []
lines.append("% Table T11: Dirichlet weight perturbation rank volatility")
lines.append("\\begin{longtable}{@{}rl S[table-format=2.2] S[table-format=1.2] S[table-format=2.1] S[table-format=2.1] S[table-format=3.1] S[table-format=3.1]@{}}")
lines.append("\\caption{Rank volatility under Dirichlet weight perturbation ($\\alpha_j=10$, $N_{\\text{MC}}=" + str(N_MC) + "$).")
lines.append("Mean rank, standard deviation, 5th--95th percentile band, and probability of")
lines.append("falling in the top~5 or top~10 are reported for each country.}")
lines.append("\\label{tab:dirichlet-volatility}\\\\")
lines.append("\\toprule")
lines.append("{\\textbf{Rk}} & {\\textbf{Country}} & {\\textbf{Mean Rk}} & {$\\boldsymbol{\\sigma}$} & {\\textbf{P5}} & {\\textbf{P95}} & {\\textbf{\\%Top5}} & {\\textbf{\\%Top10}} \\\\")
lines.append("\\midrule")
lines.append("\\endfirsthead")
lines.append("\\caption[]{Dirichlet rank volatility (continued).}\\\\")
lines.append("\\toprule")
lines.append("{\\textbf{Rk}} & {\\textbf{Country}} & {\\textbf{Mean Rk}} & {$\\boldsymbol{\\sigma}$} & {\\textbf{P5}} & {\\textbf{P95}} & {\\textbf{\\%Top5}} & {\\textbf{\\%Top10}} \\\\")
lines.append("\\midrule")
lines.append("\\endhead")
lines.append("\\bottomrule")
lines.append("\\endlastfoot")
order = np.argsort(baseline_ranks)
for i in order:
    lines.append(f"  {int(baseline_ranks[i])} & {NAMES[i]} & {mean_rank[i]:.2f} & {std_rank[i]:.2f} & {p5_rank[i]:.1f} & {p95_rank[i]:.1f} & {prob_top5[i]:.1f} & {prob_top10[i]:.1f} \\\\")
lines.append("\\end{longtable}")
write_table("T11_dirichlet_volatility.tex", "\n".join(lines))

mc_spearmans = np.array([spearman_corr(baseline_ranks, mc_ranks[:, t]) for t in range(N_MC)])
print(f"  Mean Spearman: {np.mean(mc_spearmans):.6f} (std={np.std(mc_spearmans):.6f})")
print(f"  Min: {np.min(mc_spearmans):.6f}  Max: {np.max(mc_spearmans):.6f}")

vol_order = np.argsort(-std_rank)
for idx in vol_order[:5]:
    print(f"    {NAMES[idx]:15s}: std={std_rank[idx]:.2f} band=[{p5_rank[idx]:.0f},{p95_rank[idx]:.0f}]")


# ===========================================================================
# 6. WINSORIZATION
# ===========================================================================
print("\n" + "="*72)
print("6. WINSORIZATION")
print("="*72)

AXES_W = AXES.copy()
for j_cap in [3, 5]:
    p95 = np.percentile(AXES[:, j_cap], 95)
    print(f"  {AXIS_NAMES[j_cap]} P95 cap: {p95:.8f}")
    AXES_W[:, j_cap] = np.minimum(AXES[:, j_cap], p95)

w_composite = np.mean(AXES_W, axis=1)
w_ranks = rankdata(w_composite)
w_spearman = spearman_corr(baseline_ranks, w_ranks)
print(f"  Spearman rho: {w_spearman:.6f}")

lines = []
lines.append("% Table T12: Winsorization sensitivity")
lines.append("\\begin{longtable}{@{}rlS[table-format=1.8]rS[table-format=1.8]rr@{}}")
lines.append("\\caption{Rank comparison: baseline vs.\\ winsorized composite (Axis~4 and Axis~6")
lines.append("capped at their respective 95th percentiles).  Spearman $\\rho = " + f"{w_spearman:.6f}" + "$.}")
lines.append("\\label{tab:winsorization}\\\\")
lines.append("\\toprule")
lines.append("{\\textbf{Rk}} & {\\textbf{Country}} & {\\textbf{Baseline}} & {\\textbf{Rk (base)}} & {\\textbf{Winsorized}} & {\\textbf{Rk (win)}} & {$\\boldsymbol{\\Delta}$} \\\\")
lines.append("\\midrule")
lines.append("\\endfirsthead")
lines.append("\\caption[]{Winsorization (continued).}\\\\")
lines.append("\\toprule")
lines.append("{\\textbf{Rk}} & {\\textbf{Country}} & {\\textbf{Baseline}} & {\\textbf{Rk (base)}} & {\\textbf{Winsorized}} & {\\textbf{Rk (win)}} & {$\\boldsymbol{\\Delta}$} \\\\")
lines.append("\\midrule")
lines.append("\\endhead")
lines.append("\\bottomrule")
lines.append("\\endlastfoot")
order = np.argsort(baseline_ranks)
for i in order:
    delta = int(abs(baseline_ranks[i] - w_ranks[i]))
    lines.append(f"  {int(baseline_ranks[i])} & {NAMES[i]} & {COMP[i]:.8f} & {int(baseline_ranks[i])} & {w_composite[i]:.8f} & {int(w_ranks[i])} & {delta} \\\\")
lines.append("\\end{longtable}")
write_table("T12_winsorization.tex", "\n".join(lines))


# ===========================================================================
# 7. TOP-5 / BOTTOM-5 PER AXIS
# ===========================================================================
print("\n" + "="*72)
print("7. TOP-5 / BOTTOM-5 PER AXIS")
print("="*72)

lines = []
lines.append("% Table T6: Top-5 and Bottom-5 per axis")
lines.append("\\begin{table}[htbp]")
lines.append("\\centering")
lines.append("\\caption{Top-5 (most concentrated) and Bottom-5 (least concentrated) countries per axis.}")
lines.append("\\label{tab:axis-top-bottom}")
lines.append("\\footnotesize")
lines.append("\\begin{tabular}{@{}lllll@{}}")
lines.append("\\toprule")
lines.append("{\\textbf{Axis}} & {\\textbf{Top-5 (most conc.)}} & {\\textbf{Score}} & {\\textbf{Bottom-5 (least conc.)}} & {\\textbf{Score}} \\\\")
lines.append("\\midrule")
for j in range(6):
    sorted_idx = np.argsort(-AXES[:, j])
    top5 = sorted_idx[:5]
    bot5 = sorted_idx[-5:][::-1]
    for k in range(5):
        prefix = AXIS_NAMES[j] if k == 0 else ""
        ti = top5[k]
        bi = bot5[k]
        lines.append(f"  {prefix} & {NAMES[ti]} & {AXES[ti,j]:.8f} & {NAMES[bi]} & {AXES[bi,j]:.8f} \\\\")
    if j < 5:
        lines.append("\\addlinespace")
lines.append("\\bottomrule")
lines.append("\\end{tabular}")
lines.append("\\end{table}")
write_table("T06_axis_top_bottom.tex", "\n".join(lines))


# ===========================================================================
# 8. LORENZ CURVE COORDINATES
# ===========================================================================
print("\n" + "="*72)
print("8. LORENZ CURVE")
print("="*72)

sorted_comp = np.sort(COMP)
cum_share = np.cumsum(sorted_comp) / np.sum(sorted_comp)
pop_share = np.arange(1, N+1) / N
gini = 1.0 - 2.0 * np.trapezoid(cum_share, pop_share)
print(f"  Gini: {gini:.6f}")

lines = []
lines.append("% Lorenz curve coordinates")
lines.append("% population_share cumulative_score_share")
lines.append("0.0000 0.0000")
for k in range(N):
    lines.append(f"{pop_share[k]:.6f} {cum_share[k]:.6f}")
write_table("lorenz_coords.dat", "\n".join(lines))


# ===========================================================================
# 9. AXIS RANK TABLES
# ===========================================================================
print("\n" + "="*72)
print("9. AXIS RANK TABLES")
print("="*72)

for j in range(6):
    ax_ranks = rankdata(AXES[:, j])
    sorted_idx = np.argsort(ax_ranks)
    lines = []
    lines.append(f"% Appendix: {AXIS_NAMES[j]} axis ranking")
    lines.append("\\begin{longtable}{@{}rlS[table-format=1.8]@{}}")
    lines.append(f"\\caption{{{AXIS_NAMES[j]} axis ranking, EU-27, 2024.}}")
    lines.append(f"\\label{{tab:axis-rank-{AXIS_SLUGS[j]}}}\\\\")
    lines.append("\\toprule")
    lines.append("{\\textbf{Rk}} & {\\textbf{Country}} & {\\textbf{Score}} \\\\")
    lines.append("\\midrule")
    lines.append("\\endfirsthead")
    lines.append(f"\\caption[]{{{AXIS_NAMES[j]} axis ranking (continued).}}\\\\")
    lines.append("\\toprule")
    lines.append("{\\textbf{Rk}} & {\\textbf{Country}} & {\\textbf{Score}} \\\\")
    lines.append("\\midrule")
    lines.append("\\endhead")
    lines.append("\\bottomrule")
    lines.append("\\endlastfoot")
    for i in sorted_idx:
        lines.append(f"  {int(ax_ranks[i])} & {NAMES[i]} & {AXES[i,j]:.8f} \\\\")
    lines.append("\\end{longtable}")
    write_table(f"TA_{AXIS_SLUGS[j]}_ranking.tex", "\n".join(lines))
    print(f"  Written: {AXIS_NAMES[j]}")


# ===========================================================================
# 10. HISTOGRAM / ECDF COORDINATES
# ===========================================================================
print("\n" + "="*72)
print("10. HISTOGRAM/ECDF")
print("="*72)

sorted_comp_ecdf = np.sort(COMP)
lines = []
lines.append("% ECDF coordinates")
lines.append("% composite_score ecdf_value")
for k in range(N):
    lines.append(f"{sorted_comp_ecdf[k]:.8f} {(k+1)/N:.8f}")
write_table("ecdf_coords.dat", "\n".join(lines))

bin_edges = np.linspace(0.20, 0.55, 8)
hist_counts, _ = np.histogram(COMP, bins=bin_edges)
lines = []
lines.append("% Histogram coordinates (bin_center, count)")
for k in range(len(hist_counts)):
    center = (bin_edges[k] + bin_edges[k+1]) / 2.0
    lines.append(f"{center:.4f} {hist_counts[k]}")
write_table("histogram_coords.dat", "\n".join(lines))


# ===========================================================================
# 11. RADAR PLOT DATA
# ===========================================================================
print("\n" + "="*72)
print("11. RADAR PLOT DATA")
print("="*72)

selected = ["MT", "CY", "IE", "NL", "DE", "SK", "FI", "FR"]
for iso in selected:
    idx = ISO.index(iso)
    lines = []
    lines.append(f"% Radar data for {NAMES[idx]} ({iso})")
    lines.append("% axis_index axis_name score")
    for j in range(6):
        lines.append(f"{j} {AXIS_SLUGS[j]} {AXES[idx,j]:.8f}")
    write_table(f"radar_{iso}.dat", "\n".join(lines))
    print(f"  {NAMES[idx]}")


# ===========================================================================
# 12. BOXPLOT STATS
# ===========================================================================
print("\n" + "="*72)
print("12. BOXPLOT STATISTICS")
print("="*72)

for j in range(6):
    vals = AXES[:, j]
    q1 = np.percentile(vals, 25)
    med = np.median(vals)
    q3 = np.percentile(vals, 75)
    iqr = q3 - q1
    wlo = np.min(vals[vals >= q1 - 1.5*iqr])
    whi = np.max(vals[vals <= q3 + 1.5*iqr])
    print(f"  {AXIS_NAMES[j]:20s}: Q1={q1:.4f} Med={med:.4f} Q3={q3:.4f} Lo={wlo:.4f} Hi={whi:.4f}")


# ===========================================================================
# 13. RANK ELASTICITY TO AXIS PERTURBATION
# ===========================================================================
print("\n" + "="*72)
print("13. RANK ELASTICITY")
print("="*72)

epsilons = [0.05, 0.10, 0.20]  # 5%, 10%, 20% shocks
rank_sens_by_eps = {}

for epsilon in epsilons:
    rank_sens_pos = np.zeros((N, 6))
    for j in range(6):
        Ap = AXES.copy()
        Ap[:, j] = np.clip(AXES[:, j] * (1 + epsilon), 0.0, 1.0)
        rp = rankdata(np.mean(Ap, axis=1))
        rank_sens_pos[:, j] = baseline_ranks - rp
    rank_sens_by_eps[epsilon] = rank_sens_pos

# Use 10% shock for the main table
rank_sens_pos = rank_sens_by_eps[0.10]
total_sens = np.sum(np.abs(rank_sens_pos), axis=1)
fragile_order = np.argsort(-total_sens)

print("  Top 10 rank-fragile (sum |delta| from +1%):")
for idx in fragile_order[:10]:
    print(f"    {NAMES[idx]:15s}: total={total_sens[idx]:.0f}  per_axis={rank_sens_pos[idx,:]}")

locked = np.sum(total_sens == 0)
print(f"  Structurally locked-in countries: {locked}")
for idx in range(N):
    if total_sens[idx] == 0:
        print(f"    {NAMES[idx]}")

# T13: Rank elasticity table
lines = []
lines.append("% Table T13: Rank sensitivity to +10% axis perturbation")
lines.append("\\begin{landscape}")
lines.append("\\begin{longtable}{@{}rl rrrrrr r@{}}")
lines.append("\\caption{Rank change per country under a $+10\\%$ multiplicative perturbation to each axis.")
lines.append("Positive values indicate rank improvement (toward rank 1);")
lines.append("negative values indicate deterioration.  $\\Sigma|\\Delta|$ is the total absolute displacement.}")
lines.append("\\label{tab:rank-elasticity}\\\\")
lines.append("\\toprule")
hdr = "{\\textbf{Rk}} & {\\textbf{Country}}"
for j in range(6):
    hdr += f" & {{\\textbf{{{AXIS_NAMES[j][:4]}}}}}"
hdr += " & {$\\Sigma|\\Delta|$} \\\\"
lines.append(hdr)
lines.append("\\midrule")
lines.append("\\endfirsthead")
lines.append("\\caption[]{Rank elasticity (continued).}\\\\")
lines.append("\\toprule")
lines.append(hdr)
lines.append("\\midrule")
lines.append("\\endhead")
lines.append("\\bottomrule")
lines.append("\\endlastfoot")
order = np.argsort(baseline_ranks)
for i in order:
    row = f"  {int(baseline_ranks[i])} & {NAMES[i]}"
    for j in range(6):
        row += f" & {int(rank_sens_pos[i,j]):+d}"
    row += f" & {int(total_sens[i])} \\\\"
    lines.append(row)
lines.append("\\end{longtable}")
lines.append("\\end{landscape}")
write_table("T13_rank_elasticity.tex", "\n".join(lines))


# ===========================================================================
# 14. AXIS CONTRIBUTION TO RANK DIFFERENTIATION
# ===========================================================================
print("\n" + "="*72)
print("14. AXIS-RANK CONTRIBUTION")
print("="*72)

axis_rank_corr = np.zeros(6)
axis_rank_r2 = np.zeros(6)
for j in range(6):
    r = pearson_corr(AXES[:, j], -baseline_ranks)
    axis_rank_corr[j] = r
    axis_rank_r2[j] = r**2
    print(f"  {AXIS_NAMES[j]:20s}: r={r:.6f}  R2={r**2:.6f}")

partial_corr = np.zeros(6)
for j in range(6):
    other = [k for k in range(6) if k != j]
    X_o = np.column_stack([np.ones(N), AXES[:, other]])
    y = -baseline_ranks.astype(float)
    x_t = AXES[:, j]
    beta_y = np.linalg.lstsq(X_o, y, rcond=None)[0]
    beta_x = np.linalg.lstsq(X_o, x_t, rcond=None)[0]
    resid_y = y - X_o @ beta_y
    resid_x = x_t - X_o @ beta_x
    partial_corr[j] = pearson_corr(resid_x, resid_y)
    print(f"  {AXIS_NAMES[j]:20s}: partial_r={partial_corr[j]:.6f}")

lines = []
lines.append("% Table T14: Axis contribution to rank differentiation")
lines.append("\\begin{table}[htbp]")
lines.append("\\centering")
lines.append("\\caption{Axis contribution to composite rank differentiation.  Bivariate $R^2$:")
lines.append("share of rank variance explained by each axis alone.  Partial $r$: association with")
lines.append("rank after controlling for all other axes.}")
lines.append("\\label{tab:axis-rank-contrib}")
lines.append("\\begin{tabular}{@{}l S[table-format=+1.4] S[table-format=1.4] S[table-format=+1.4]@{}}")
lines.append("\\toprule")
lines.append("{\\textbf{Axis}} & {\\textbf{Pearson $r$}} & {$\\boldsymbol{R^2}$} & {\\textbf{Partial $r$}} \\\\")
lines.append("\\midrule")
for j in range(6):
    lines.append(f"  {AXIS_NAMES[j]} & {axis_rank_corr[j]:+.4f} & {axis_rank_r2[j]:.4f} & {partial_corr[j]:+.4f} \\\\")
lines.append("\\bottomrule")
lines.append("\\end{tabular}")
lines.append("\\end{table}")
write_table("T14_axis_rank_contrib.tex", "\n".join(lines))


# ===========================================================================
# 15. CLASSIFICATION COMPRESSION DIAGNOSTICS
# ===========================================================================
print("\n" + "="*72)
print("15. COMPRESSION DIAGNOSTICS")
print("="*72)

tiers = {
    "Highly concentrated": (0.50, 1.01),
    "Moderately concentrated": (0.25, 0.50),
    "Mildly concentrated": (0.15, 0.25),
    "Unconcentrated": (0.00, 0.15),
}

grand_mean = np.mean(COMP)
ssw = 0.0
ssb = 0.0
tier_info = {}

for tname, (lo, hi) in tiers.items():
    mask = (COMP >= lo) & (COMP < hi)
    if np.sum(mask) == 0:
        continue
    vals = COMP[mask]
    tmean = np.mean(vals)
    tvar = np.var(vals, ddof=0) if len(vals) > 1 else 0.0
    tier_info[tname] = (len(vals), tmean, tvar)
    ssw += np.sum((vals - tmean)**2)
    ssb += len(vals) * (tmean - grand_mean)**2

total_ss = np.sum((COMP - grand_mean)**2)
eta_sq = ssb / total_ss if total_ss > 0 else 0.0

print(f"  Grand mean: {grand_mean:.8f}")
print(f"  SS_within={ssw:.10f}  SS_between={ssb:.10f}  SS_total={total_ss:.10f}")
print(f"  Eta-squared: {eta_sq:.6f}")
print(f"  Gini: {gini:.6f}")

for tname, (n, m, v) in tier_info.items():
    print(f"  {tname:30s}: n={n}  mean={m:.8f}  var={v:.10f}")

# Tercile and quartile alternatives
tercile_edges = np.percentile(COMP, [33.33, 66.67])
quartile_edges = np.percentile(COMP, [25, 50, 75])
print(f"  Terciles: {tercile_edges}")
print(f"  Quartiles: {quartile_edges}")

# T15: Compression diagnostics
lines = []
lines.append("% Table T15: Classification compression diagnostics")
lines.append("\\begin{table}[htbp]")
lines.append("\\centering")
lines.append("\\caption{Classification compression diagnostics.  The official four-tier scheme")
lines.append("is compared with data-driven tercile and quartile alternatives.  $\\eta^2 = SS_B / SS_T$")
lines.append("measures between-tier variance share.}")
lines.append("\\label{tab:compression-diagnostics}")
lines.append("\\small")
lines.append("\\begin{tabular}{@{}l r S[table-format=1.8] S[table-format=1.10] l@{}}")
lines.append("\\toprule")
lines.append("{\\textbf{Tier}} & {$n$} & {\\textbf{Mean}} & {\\textbf{Var (within)}} & {\\textbf{Scheme}} \\\\")
lines.append("\\midrule")
for tname in ["Highly concentrated", "Moderately concentrated", "Mildly concentrated"]:
    if tname in tier_info:
        n, m, v = tier_info[tname]
        lines.append(f"  {tname} & {n} & {m:.8f} & {v:.10f} & Official \\\\")
lines.append("\\addlinespace")

# Terciles
trc_bounds = [(0, tercile_edges[0]), (tercile_edges[0], tercile_edges[1]), (tercile_edges[1], 1.0)]
trc_labels = ["T1 (low)", "T2 (mid)", "T3 (high)"]
for idx, (lo, hi) in enumerate(trc_bounds):
    mask = (COMP >= lo) & (COMP < hi) if idx < 2 else (COMP >= lo)
    vals = COMP[mask]
    lines.append(f"  {trc_labels[idx]} & {len(vals)} & {np.mean(vals):.8f} & {np.var(vals, ddof=0):.10f} & Tercile \\\\")
lines.append("\\addlinespace")

# Quartiles
qrt_bounds = [(0, quartile_edges[0]), (quartile_edges[0], quartile_edges[1]),
              (quartile_edges[1], quartile_edges[2]), (quartile_edges[2], 1.0)]
qrt_labels = ["Q1 (low)", "Q2", "Q3", "Q4 (high)"]
for idx, (lo, hi) in enumerate(qrt_bounds):
    mask = (COMP >= lo) & (COMP < hi) if idx < 3 else (COMP >= lo)
    vals = COMP[mask]
    lines.append(f"  {qrt_labels[idx]} & {len(vals)} & {np.mean(vals):.8f} & {np.var(vals, ddof=0):.10f} & Quartile \\\\")
lines.append("\\midrule")
lines.append(f"  \\multicolumn{{5}}{{@{{}}l@{{}}}}{{$\\eta^2$ (official) $= {eta_sq:.6f}$; Gini $= {gini:.6f}$}} \\\\")
lines.append("\\bottomrule")
lines.append("\\end{tabular}")
lines.append("\\end{table}")
write_table("T15_compression_diagnostics.tex", "\n".join(lines))


# ===========================================================================
# 16. DEFENCE AXIS STRUCTURAL ANALYSIS
# ===========================================================================
print("\n" + "="*72)
print("16. DEFENCE STRUCTURAL ANALYSIS")
print("="*72)

defence = AXES[:, 3]
defence_is_max = int(np.sum(max_axis_idx == 3))
near_monopoly = int(np.sum(defence > 0.80))
sk_idx = ISO.index("SK")

# Gap: defence minus second-highest (for defence-max countries)
# or defence minus max (for logistics-max countries)
defence_gap = np.zeros(N)
for i in range(N):
    sorted_vals = np.sort(AXES[i])[::-1]
    if max_axis_idx[i] == 3:
        defence_gap[i] = defence[i] - sorted_vals[1]
    else:
        defence_gap[i] = defence[i] - AXES[i, max_axis_idx[i]]

print(f"  Defence is max axis: {defence_is_max}/27 ({defence_is_max/N*100:.1f}%)")
print(f"  Score > 0.80: {near_monopoly}")
print(f"  Score = 0.00: {int(np.sum(defence == 0))}")
print(f"  Mean gap (def-max countries): {np.mean(defence_gap[max_axis_idx==3]):.6f}")

# Skewness and kurtosis
def_mean = np.mean(defence)
def_std = np.std(defence, ddof=0)
def_skew = float(np.mean(((defence - def_mean)/def_std)**3))
def_kurt = float(np.mean(((defence - def_mean)/def_std)**4) - 3)

# T16: Defence structural
lines = []
lines.append("% Table T16: Defence axis structural analysis")
lines.append("\\begin{table}[htbp]")
lines.append("\\centering")
lines.append("\\caption{Structural properties of the defence axis distribution, EU-27, 2024.}")
lines.append("\\label{tab:defence-structural}")
lines.append("\\begin{tabular}{@{}lr@{}}")
lines.append("\\toprule")
lines.append("{\\textbf{Statistic}} & {\\textbf{Value}} \\\\")
lines.append("\\midrule")
lines.append(f"  Countries where defence is max axis & {defence_is_max} of 27 ({defence_is_max/N*100:.1f}\\%) \\\\")
lines.append(f"  Countries with score $> 0.80$ & {near_monopoly} ({near_monopoly/N*100:.1f}\\%) \\\\")
lines.append(f"  Countries with score $= 0.00$ & {int(np.sum(defence==0))} \\\\")
lines.append(f"  Mean (pop.) & {def_mean:.8f} \\\\")
lines.append(f"  Median & {np.median(defence):.8f} \\\\")
lines.append(f"  Std.\\ dev.\\ (pop.) & {def_std:.8f} \\\\")
lines.append(f"  Range & {np.max(defence) - np.min(defence):.8f} \\\\")
lines.append(f"  IQR & {np.percentile(defence, 75) - np.percentile(defence, 25):.8f} \\\\")
lines.append(f"  Skewness & {def_skew:.4f} \\\\")
lines.append(f"  Excess kurtosis & {def_kurt:.4f} \\\\")
lines.append(f"  Mean def--2nd gap (def-max) & {np.mean(defence_gap[max_axis_idx==3]):.8f} \\\\")
lines.append(f"  Median def--2nd gap (def-max) & {np.median(defence_gap[max_axis_idx==3]):.8f} \\\\")
lines.append("\\bottomrule")
lines.append("\\end{tabular}")
lines.append("\\end{table}")
write_table("T16_defence_structural.tex", "\n".join(lines))

# T16b: Defence gap per country
lines = []
lines.append("% Table T16b: Defence gap per country")
lines.append("\\begin{longtable}{@{}rl S[table-format=1.8] l S[table-format=+1.8]@{}}")
lines.append("\\caption{Defence axis score, max axis identity, and defence-to-max gap per country.}")
lines.append("\\label{tab:defence-gap}\\\\")
lines.append("\\toprule")
lines.append("{\\textbf{Rk}} & {\\textbf{Country}} & {\\textbf{Def.\\ Score}} & {\\textbf{Max Axis}} & {\\textbf{Gap}} \\\\")
lines.append("\\midrule")
lines.append("\\endfirsthead")
lines.append("\\caption[]{Defence gap (continued).}\\\\")
lines.append("\\toprule")
lines.append("{\\textbf{Rk}} & {\\textbf{Country}} & {\\textbf{Def.\\ Score}} & {\\textbf{Max Axis}} & {\\textbf{Gap}} \\\\")
lines.append("\\midrule")
lines.append("\\endhead")
lines.append("\\bottomrule")
lines.append("\\endlastfoot")
order = np.argsort(baseline_ranks)
for i in order:
    lines.append(f"  {int(baseline_ranks[i])} & {NAMES[i]} & {defence[i]:.8f} & {AXIS_NAMES[max_axis_idx[i]]} & {defence_gap[i]:+.8f} \\\\")
lines.append("\\end{longtable}")
write_table("T16b_defence_gap.tex", "\n".join(lines))


# ===========================================================================
# 17. COMPENSABILITY ANALYSIS
# ===========================================================================
print("\n" + "="*72)
print("17. COMPENSABILITY ANALYSIS")
print("="*72)

max_scores = np.max(AXES, axis=1)
min_scores = np.min(AXES, axis=1)
axis_range = max_scores - min_scores
compensation_gap = max_scores - COMP

country_cv = np.zeros(N)
for i in range(N):
    m = np.mean(AXES[i])
    s = np.std(AXES[i], ddof=0)
    country_cv[i] = s / m if m > 0 else 0

comp_order = np.argsort(-compensation_gap)
print("  Most compensated (largest max-composite gap):")
for idx in comp_order[:5]:
    print(f"    {NAMES[idx]:15s}: max={max_scores[idx]:.4f} comp={COMP[idx]:.4f} gap={compensation_gap[idx]:.4f} CV={country_cv[idx]:.4f}")

# T17: Compensability
lines = []
lines.append("% Table T17: Compensability analysis")
lines.append("\\begin{longtable}{@{}rl S[table-format=1.8] S[table-format=1.8] S[table-format=1.8] S[table-format=1.8] S[table-format=1.4]@{}}")
lines.append("\\caption{Compensability analysis.  Gap $=$ Max $-$ Composite.  CV: coefficient of")
lines.append("variation of the six axis scores per country.  High Gap and CV indicate strong")
lines.append("internal compensation where low axes offset high axes.}")
lines.append("\\label{tab:compensability}\\\\")
lines.append("\\toprule")
lines.append("{\\textbf{Rk}} & {\\textbf{Country}} & {\\textbf{Max}} & {\\textbf{Min}} & {\\textbf{Range}} & {\\textbf{Gap}} & {\\textbf{CV}} \\\\")
lines.append("\\midrule")
lines.append("\\endfirsthead")
lines.append("\\caption[]{Compensability (continued).}\\\\")
lines.append("\\toprule")
lines.append("{\\textbf{Rk}} & {\\textbf{Country}} & {\\textbf{Max}} & {\\textbf{Min}} & {\\textbf{Range}} & {\\textbf{Gap}} & {\\textbf{CV}} \\\\")
lines.append("\\midrule")
lines.append("\\endhead")
lines.append("\\bottomrule")
lines.append("\\endlastfoot")
order = np.argsort(baseline_ranks)
for i in order:
    lines.append(f"  {int(baseline_ranks[i])} & {NAMES[i]} & {max_scores[i]:.8f} & {min_scores[i]:.8f} & {axis_range[i]:.8f} & {compensation_gap[i]:.8f} & {country_cv[i]:.4f} \\\\")
lines.append("\\end{longtable}")
write_table("T17_compensability.tex", "\n".join(lines))


# ===========================================================================
# 18. GEOGRAPHIC / STRUCTURAL CORRELATES
# ===========================================================================
print("\n" + "="*72)
print("18. GEOGRAPHIC CORRELATES")
print("="*72)

ISLAND = {"MT", "CY", "IE"}
SMALL_POP = {"MT", "CY", "LU", "EE", "LV", "LT", "SI", "HR"}
LARGE_POP = {"DE", "FR", "ES", "IT", "PL", "RO", "NL"}
CORE = {"DE", "FR", "BE", "NL", "LU", "AT"}
PERIPHERY = {"MT", "CY", "EL", "PT", "FI", "EE", "LV", "LT", "BG", "RO", "HR", "IE"}

non_island = set(ISO) - ISLAND
mid_pop = set(ISO) - SMALL_POP - LARGE_POP

groups = [
    ("Island/near-island", ISLAND),
    ("Continental", non_island),
    ("Small ($<$5M pop.)", SMALL_POP),
    ("Medium (5--20M)", mid_pop),
    ("Large ($>$20M pop.)", LARGE_POP),
    ("Core EU-6", CORE),
    ("Periphery", PERIPHERY),
]

lines = []
lines.append("% Table T18: Geographic and structural correlates")
lines.append("\\begin{table}[htbp]")
lines.append("\\centering")
lines.append("\\caption{ISI composite by geographic and structural category.}")
lines.append("\\label{tab:geo-correlates}")
lines.append("\\begin{tabular}{@{}l r S[table-format=1.6] S[table-format=1.6] S[table-format=1.6]@{}}")
lines.append("\\toprule")
lines.append("{\\textbf{Category}} & {$n$} & {\\textbf{Mean}} & {\\textbf{Std (pop.)}} & {\\textbf{Median}} \\\\")
lines.append("\\midrule")
for glabel, gset in groups:
    mask = np.array([ISO[i] in gset for i in range(N)])
    vals = COMP[mask]
    n = len(vals)
    m = np.mean(vals)
    s = np.std(vals, ddof=0)
    med = np.median(vals)
    lines.append(f"  {glabel} & {n} & {m:.6f} & {s:.6f} & {med:.6f} \\\\")
    print(f"  {glabel:25s}: n={n} mean={m:.6f} std={s:.6f}")
lines.append("\\midrule")
lines.append(f"  EU-27 (all) & 27 & {np.mean(COMP):.6f} & {np.std(COMP, ddof=0):.6f} & {np.median(COMP):.6f} \\\\")
lines.append("\\bottomrule")
lines.append("\\end{tabular}")
lines.append("\\end{table}")
write_table("T18_geo_correlates.tex", "\n".join(lines))


# ===========================================================================
# 19. CORRELATION T-STATISTICS
# ===========================================================================
print("\n" + "="*72)
print("19. CORRELATION T-STATISTICS")
print("="*72)

pearson_matrix = np.corrcoef(AXES.T)
t_matrix = np.zeros((6, 6))
for j in range(6):
    for k in range(6):
        if j == k:
            t_matrix[j, k] = np.inf
        else:
            r = pearson_matrix[j, k]
            denom = 1 - r**2
            t_matrix[j, k] = r * np.sqrt((N - 2) / denom) if denom > 0 else np.inf

for j in range(6):
    for k in range(j+1, 6):
        r = pearson_matrix[j, k]
        t = t_matrix[j, k]
        sig = "*" if abs(t) > 2.060 else ""
        print(f"    {AXIS_NAMES[j]:15s} vs {AXIS_NAMES[k]:15s}: r={r:+.4f} t={t:+.4f} {sig}")

# TE3: Correlation t-statistics
lines = []
lines.append("% Table TE3: Correlation t-statistics")
lines.append("\\begin{table}[htbp]")
lines.append("\\centering")
lines.append("\\caption{Pearson correlations (below diagonal) and $t$-statistics (above diagonal).")
lines.append("$t = r\\sqrt{(N-2)/(1-r^2)}$, $N=27$, df$=25$. Critical value: $t_{0.025,25} = 2.060$;")
lines.append("* indicates significance at 5\\%.}")
lines.append("\\label{tab:corr-tstat}")
lines.append("\\small")
lines.append("\\sisetup{table-format=+1.3}")
lines.append("\\begin{tabular}{@{}l S S S S S S@{}}")
lines.append("\\toprule")
lines.append(" & {\\textbf{Fin.}} & {\\textbf{Ene.}} & {\\textbf{Tec.}} & {\\textbf{Def.}} & {\\textbf{Crit.}} & {\\textbf{Log.}} \\\\")
lines.append("\\midrule")
for j in range(6):
    row = f"  {AXIS_NAMES[j]}"
    for k in range(6):
        if j == k:
            row += " & {--}"
        elif j > k:
            r = pearson_matrix[j, k]
            sig = "*" if abs(t_matrix[j, k]) > 2.060 else ""
            row += f" & {{{r:+.3f}{sig}}}"
        else:
            t = t_matrix[j, k]
            row += f" & {{{t:+.3f}}}"
    row += " \\\\"
    lines.append(row)
lines.append("\\bottomrule")
lines.append("\\end{tabular}")
lines.append("\\end{table}")
write_table("TE3_corr_tstat.tex", "\n".join(lines))


# ===========================================================================
# 20. LOO INDIVIDUAL AXIS TABLES
# ===========================================================================
print("\n" + "="*72)
print("20. LOO INDIVIDUAL TABLES")
print("="*72)

for j in range(6):
    order = np.argsort(loo_ranks[:, j])
    lines = []
    lines.append(f"% LOO excluding {AXIS_NAMES[j]}")
    lines.append("\\begin{longtable}{@{}rl S[table-format=1.8] r r@{}}")
    lines.append(f"\\caption{{LOO ranking excluding {AXIS_NAMES[j]}.  Spearman $\\rho = {loo_spearman[j]:.6f}$, Kendall $\\tau = {loo_kendall[j]:.6f}$.}}")
    lines.append(f"\\label{{tab:loo-{AXIS_SLUGS[j]}}}\\\\")
    lines.append("\\toprule")
    lines.append("{\\textbf{LOO Rk}} & {\\textbf{Country}} & {\\textbf{LOO Comp.}} & {\\textbf{Base Rk}} & {$\\boldsymbol{\\Delta}$} \\\\")
    lines.append("\\midrule")
    lines.append("\\endfirsthead")
    lines.append(f"\\caption[]{{LOO excl.\\ {AXIS_NAMES[j]} (cont.).}}\\\\")
    lines.append("\\toprule")
    lines.append("{\\textbf{LOO Rk}} & {\\textbf{Country}} & {\\textbf{LOO Comp.}} & {\\textbf{Base Rk}} & {$\\boldsymbol{\\Delta}$} \\\\")
    lines.append("\\midrule")
    lines.append("\\endhead")
    lines.append("\\bottomrule")
    lines.append("\\endlastfoot")
    for i in order:
        delta = int(baseline_ranks[i] - loo_ranks[i, j])
        lines.append(f"  {int(loo_ranks[i,j])} & {NAMES[i]} & {loo_composites[i,j]:.8f} & {int(baseline_ranks[i])} & {delta:+d} \\\\")
    lines.append("\\end{longtable}")
    write_table(f"TC_loo_{AXIS_SLUGS[j]}.tex", "\n".join(lines))
    print(f"  Written: LOO excl {AXIS_NAMES[j]}")


# ===========================================================================
# 21. MULTIPLE REGRESSION
# ===========================================================================
print("\n" + "="*72)
print("21. MULTIPLE REGRESSION")
print("="*72)

y = -baseline_ranks.astype(float)
X = np.column_stack([np.ones(N), AXES])
beta = np.linalg.lstsq(X, y, rcond=None)[0]
y_hat = X @ beta
ss_res = np.sum((y - y_hat)**2)
ss_tot = np.sum((y - np.mean(y))**2)
r2_full = 1 - ss_res / ss_tot
adj_r2 = 1 - (1 - r2_full) * (N - 1) / (N - 7)
print(f"  R2={r2_full:.6f}  adj_R2={adj_r2:.6f}")
print(f"  Coefficients: intercept={beta[0]:.4f}, " + ", ".join(f"{AXIS_NAMES[j]}={beta[j+1]:.4f}" for j in range(6)))


# ===========================================================================
print("\n" + "="*72)
print("ALL COMPUTATIONS COMPLETE")
print(f"Output written to: {OUT_DIR}")
print("="*72)
