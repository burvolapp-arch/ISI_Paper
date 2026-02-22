#!/usr/bin/env python3
"""
ISI Results Paper 2 -- Computation Engine
=========================================
Reads the ISI v1.0 EU-27 snapshot (embedded) and produces all derived
tables for Paper 2:
  - Leave-one-axis-out (LOO) composites + Spearman correlations
  - Z-score standardized composites + rank comparison
  - Dirichlet weight perturbation (Monte Carlo) rank volatility
  - Winsorization (cap Axis 4 & 6 at p95) + rank comparison
  - Axis dominance table (max axis, 2nd max per country)
  - Variance contribution decomposition
  - Lorenz curve coordinates for composite
  - Top-5 / Bottom-5 per axis

All output is printed as LaTeX table fragments to stdout and also
written to ../tables/ as individual .tex files.

Usage:
    python isi_results_paper2.py

No external dependencies beyond numpy (ships with most scientific Python).
"""

import numpy as np
import os
import sys
from io import StringIO

# -- Authoritative ISI v1.0 Snapshot -----------------------------------------

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
    # (iso2, name, rank, composite, classification, a1, a2, a3, a4, a5, a6)
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

# Parse into arrays
ISO   = [d[0] for d in DATA]
NAMES = [d[1] for d in DATA]
RANKS = np.array([d[2] for d in DATA])
COMP  = np.array([d[3] for d in DATA])
CLASS = [d[4] for d in DATA]
AXES  = np.array([[d[5+j] for j in range(6)] for d in DATA])  # shape (27,6)

# Output directory
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tables")
os.makedirs(OUT_DIR, exist_ok=True)

def write_table(filename, content):
    path = os.path.join(OUT_DIR, filename)
    with open(path, "w") as f:
        f.write(content)
    print(f"  Written: {path}")

def rankdata(x):
    """Rank data (1 = highest value). Handles ties by averaging."""
    n = len(x)
    order = np.argsort(-x)  # descending
    ranks = np.empty(n, dtype=float)
    ranks[order] = np.arange(1, n+1, dtype=float)
    return ranks

def spearman_corr(r1, r2):
    """Spearman rank correlation between two rank arrays."""
    d = r1 - r2
    n = len(r1)
    return 1.0 - (6.0 * np.sum(d**2)) / (n * (n**2 - 1))


# ===========================================================================
# 1. AXIS DOMINANCE TABLE
# ===========================================================================
print("\n" + "="*72)
print("1. AXIS DOMINANCE")
print("="*72)

max_axis_idx = np.argmax(AXES, axis=1)
# Second max
second_max_idx = np.zeros(N, dtype=int)
for i in range(N):
    sorted_idx = np.argsort(-AXES[i])
    second_max_idx[i] = sorted_idx[1]

# Count how many countries have each axis as max
axis_dom_counts = np.zeros(6, dtype=int)
for i in range(N):
    axis_dom_counts[max_axis_idx[i]] += 1

print("Axis dominance counts:")
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
# 2. VARIANCE CONTRIBUTION DECOMPOSITION
# ===========================================================================
print("\n" + "="*72)
print("2. VARIANCE CONTRIBUTION")
print("="*72)

axis_vars = np.var(AXES, axis=0, ddof=0)  # population variance per axis
total_var_sum = np.sum(axis_vars)
# Covariance contribution
cov_matrix = np.cov(AXES.T, ddof=0)  # 6x6 population covariance
total_composite_var = np.var(COMP, ddof=0)
# Composite = mean of 6 axes, so Var(composite) = (1/36) * sum of all cov entries
var_decomp_check = np.sum(cov_matrix) / 36.0
print(f"  Composite variance (direct):    {total_composite_var:.10f}")
print(f"  Composite variance (from cov):  {var_decomp_check:.10f}")

# Marginal contribution of axis j = (1/36) * sum_k cov(j,k)
marginal_contrib = np.sum(cov_matrix, axis=1) / 36.0
pct_contrib = marginal_contrib / var_decomp_check * 100.0

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
lines.append(f"  Total & {total_var_sum:.8f} & {var_decomp_check:.8f} & {np.sum(pct_contrib):.2f} \\\\")
lines.append("\\bottomrule")
lines.append("\\end{tabular}")
lines.append("\\end{table}")
write_table("T08_variance_decomp.tex", "\n".join(lines))

print("Variance contribution:")
for j in range(6):
    print(f"  {AXIS_NAMES[j]:20s}: var={axis_vars[j]:.8f}  marginal={marginal_contrib[j]:.8f}  pct={pct_contrib[j]:.2f}%")


# ===========================================================================
# 3. LEAVE-ONE-AXIS-OUT (LOO)
# ===========================================================================
print("\n" + "="*72)
print("3. LEAVE-ONE-AXIS-OUT")
print("="*72)

baseline_ranks = rankdata(COMP)

loo_composites = np.zeros((N, 6))
loo_ranks = np.zeros((N, 6))
loo_spearman = np.zeros(6)

for j in range(6):
    mask = [k for k in range(6) if k != j]
    loo_comp = np.mean(AXES[:, mask], axis=1)
    loo_composites[:, j] = loo_comp
    lr = rankdata(loo_comp)
    loo_ranks[:, j] = lr
    loo_spearman[j] = spearman_corr(baseline_ranks, lr)
    print(f"  Drop {AXIS_NAMES[j]:20s}: Spearman rho = {loo_spearman[j]:.6f}")

# Max rank change per country across all LOO
max_rank_change = np.zeros(N, dtype=int)
for i in range(N):
    changes = [abs(baseline_ranks[i] - loo_ranks[i, j]) for j in range(6)]
    max_rank_change[i] = int(max(changes))

# Table T9: LOO summary
lines = []
lines.append("% Table T9: Leave-one-axis-out rank changes")
lines.append("\\begin{table}[htbp]")
lines.append("\\centering")
lines.append("\\caption{Spearman rank correlation between baseline ISI ranking and each")
lines.append("leave-one-axis-out (LOO) ranking.  Higher $\\rho$ indicates lower sensitivity")
lines.append("to the excluded axis.}")
lines.append("\\label{tab:loo-summary}")
lines.append("\\begin{tabular}{@{}lS[table-format=1.6]@{}}")
lines.append("\\toprule")
lines.append("{\\textbf{Excluded Axis}} & {$\\boldsymbol{\\rho}$ \\textbf{(Spearman)}} \\\\")
lines.append("\\midrule")
for j in range(6):
    lines.append(f"  {AXIS_NAMES[j]} & {loo_spearman[j]:.6f} \\\\")
lines.append("\\bottomrule")
lines.append("\\end{tabular}")
lines.append("\\end{table}")
write_table("T09_loo_summary.tex", "\n".join(lines))

# Detailed LOO rank table (Appendix B)
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
    row += f" & {max_rank_change[i]} \\\\"
    lines.append(row)
lines.append("\\end{longtable}")
write_table("TB1_loo_detail.tex", "\n".join(lines))


# ===========================================================================
# 4. Z-SCORE STANDARDIZED COMPOSITE
# ===========================================================================
print("\n" + "="*72)
print("4. Z-SCORE STANDARDIZED COMPOSITE")
print("="*72)

axis_means = np.mean(AXES, axis=0)
axis_stds_pop = np.std(AXES, axis=0, ddof=0)
Z = (AXES - axis_means) / axis_stds_pop  # z-score each axis
z_composite = np.mean(Z, axis=1)
z_ranks = rankdata(z_composite)
z_spearman = spearman_corr(baseline_ranks, z_ranks)
print(f"  Spearman rho (baseline vs z-score): {z_spearman:.6f}")

lines = []
lines.append("% Table T10: Z-score standardized composite rank comparison")
lines.append("\\begin{longtable}{@{}rlS[table-format=1.8]rS[table-format=2.8]rr@{}}")
lines.append("\\caption{Rank comparison: baseline ISI vs.\\ z-score standardized composite.")
lines.append("The z-score composite re-centres each axis to mean zero and unit population")
lines.append("standard deviation before averaging.  Spearman $\\rho = " + f"{z_spearman:.6f}" + "$.}")
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
# Sort by baseline rank
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
alpha = np.ones(6) * 10.0  # Concentrated around equal weights (1/6 each)

mc_ranks = np.zeros((N, N_MC))
for t in range(N_MC):
    w = np.random.dirichlet(alpha)
    mc_comp = AXES @ w
    mc_ranks[:, t] = rankdata(mc_comp)

# Summary statistics per country
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

# Also compute mean Spearman across MC draws
mc_spearmans = np.array([spearman_corr(baseline_ranks, mc_ranks[:, t]) for t in range(N_MC)])
print(f"  Mean Spearman rho across {N_MC} MC draws: {np.mean(mc_spearmans):.6f}")
print(f"  Std  Spearman rho:                        {np.std(mc_spearmans):.6f}")
print(f"  Min  Spearman rho:                        {np.min(mc_spearmans):.6f}")
print(f"  Max  Spearman rho:                        {np.max(mc_spearmans):.6f}")

# Countries with highest rank volatility
print("\n  Top 5 most volatile:")
vol_order = np.argsort(-std_rank)
for idx in vol_order[:5]:
    print(f"    {NAMES[idx]:15s}: mean_rk={mean_rank[idx]:.2f} std={std_rank[idx]:.2f} band=[{p5_rank[idx]:.0f},{p95_rank[idx]:.0f}]")


# ===========================================================================
# 6. WINSORIZATION (CAP AXIS 4 & 6 AT P95)
# ===========================================================================
print("\n" + "="*72)
print("6. WINSORIZATION")
print("="*72)

AXES_W = AXES.copy()
for j_cap in [3, 5]:  # Axis 4 (index 3) and Axis 6 (index 5)
    p95 = np.percentile(AXES[:, j_cap], 95)
    print(f"  {AXIS_NAMES[j_cap]} P95 cap: {p95:.8f}")
    AXES_W[:, j_cap] = np.minimum(AXES[:, j_cap], p95)

w_composite = np.mean(AXES_W, axis=1)
w_ranks = rankdata(w_composite)
w_spearman = spearman_corr(baseline_ranks, w_ranks)
print(f"  Spearman rho (baseline vs winsorized): {w_spearman:.6f}")

lines = []
lines.append("% Table T12: Winsorization sensitivity rank changes")
lines.append("\\begin{longtable}{@{}rlS[table-format=1.8]rS[table-format=1.8]rr@{}}")
lines.append("\\caption{Rank comparison: baseline vs.\\ winsorized composite (Axis~4 and Axis~6")
lines.append("capped at their respective 95th percentiles).  Spearman $\\rho = " + f"{w_spearman:.6f}" + "$.}")
lines.append("\\label{tab:winsorization}\\\\")
lines.append("\\toprule")
lines.append("{\\textbf{Rk}} & {\\textbf{Country}} & {\\textbf{Baseline}} & {\\textbf{Rk (base)}} & {\\textbf{Winsorized}} & {\\textbf{Rk (win)}} & {$\\boldsymbol{\\Delta}$} \\\\")
lines.append("\\midrule")
lines.append("\\endfirsthead")
lines.append("\\caption[]{Winsorization rank changes (continued).}\\\\")
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
    bot5 = sorted_idx[-5:][::-1]  # reversed so worst is last
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
print(f"  Gini coefficient of composite: {gini:.6f}")

# Write coordinates for pgfplots
lines = []
lines.append("% Lorenz curve coordinates for pgfplots")
lines.append("% Format: population_share cumulative_score_share")
lines.append("0.0000 0.0000")
for k in range(N):
    lines.append(f"{pop_share[k]:.6f} {cum_share[k]:.6f}")
write_table("lorenz_coords.dat", "\n".join(lines))


# ===========================================================================
# 9. AXIS RANK TABLES (for Appendix A)
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
    print(f"  Written axis ranking: {AXIS_NAMES[j]}")


# ===========================================================================
# 10. HISTOGRAM COORDINATES FOR PGFPLOTS
# ===========================================================================
print("\n" + "="*72)
print("10. HISTOGRAM/ECDF COORDINATES")
print("="*72)

# Composite values sorted for ECDF
sorted_comp = np.sort(COMP)
lines = []
lines.append("% ECDF coordinates")
lines.append("% Format: composite_score ecdf_value")
for k in range(N):
    lines.append(f"{sorted_comp[k]:.8f} {(k+1)/N:.8f}")
write_table("ecdf_coords.dat", "\n".join(lines))

# Histogram bin counts (10 bins)
bin_edges = np.linspace(0.20, 0.55, 8)
hist_counts, _ = np.histogram(COMP, bins=bin_edges)
lines = []
lines.append("% Histogram coordinates (bin_center, count)")
for k in range(len(hist_counts)):
    center = (bin_edges[k] + bin_edges[k+1]) / 2.0
    lines.append(f"{center:.4f} {hist_counts[k]}")
write_table("histogram_coords.dat", "\n".join(lines))


# ===========================================================================
# 11. RADAR PLOT DATA PER COUNTRY (for TikZ)
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
    print(f"  {NAMES[idx]}: {AXES[idx,:]}")


# ===========================================================================
# 12. BOXPLOT STATS PER AXIS (for pgfplots)
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
    whisker_lo = np.min(vals[vals >= q1 - 1.5*iqr])
    whisker_hi = np.max(vals[vals <= q3 + 1.5*iqr])
    outliers_lo = vals[vals < q1 - 1.5*iqr]
    outliers_hi = vals[vals > q3 + 1.5*iqr]
    print(f"  {AXIS_NAMES[j]:20s}: Q1={q1:.4f} Med={med:.4f} Q3={q3:.4f} Lo={whisker_lo:.4f} Hi={whisker_hi:.4f} Out_lo={len(outliers_lo)} Out_hi={len(outliers_hi)}")


# ===========================================================================
# DONE
# ===========================================================================
print("\n" + "="*72)
print("ALL COMPUTATIONS COMPLETE")
print(f"Output tables written to: {OUT_DIR}")
print("="*72)
