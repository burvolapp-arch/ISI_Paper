#!/usr/bin/env python3
"""
ISI Paper Series -- Paper 3: Computation Engine
================================================
Generates all derived tables and figure data for Paper 3.

Paper 3 thesis: EU-27 sovereignty-risk dispersion is structurally
dominated by TWO axes (Defence + Logistics).  Everything else is
second-order for cross-country differentiation.

Outputs:
  tables/T01_key_summary.tex
  tables/T02_variance_decomposition.tex
  tables/T03_axis_dominance_counts.tex
  tables/T04_loo_rank_disruption.tex
  tables/T05_dirichlet_volatility_top.tex
  tables/TA1_full_variance_detail.tex
  tables/TA2_dominance_per_country.tex
  tables/TA3_loo_rank_diffs.tex
  tables/F01_variance_bar.dat
  tables/F02_dominance_share.dat
  tables/F03_loo_rho.dat

Usage:
    python isi_results_paper3.py

No external dependencies beyond numpy.
"""

import numpy as np
import os

# ============================================================================
# EMBEDDED DATA -- ISI v1.0, EU-27, Vintage 2024
# Identical to Paper 2.  Single authoritative source.
# Columns: ISO, Name, Rank, Composite, Tier,
#           Financial, Energy, Technology, Defence, Critical Inputs, Logistics
# ============================================================================

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
AXES  = np.array([[d[5 + j] for j in range(6)] for d in DATA])

TABLE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tables")
os.makedirs(TABLE_DIR, exist_ok=True)


# -- Helper functions --------------------------------------------------------

def write_file(filename, content):
    path = os.path.join(TABLE_DIR, filename)
    with open(path, "w") as f:
        f.write(content)
    print(f"  Written: {path}")


def rankdata(x):
    """Rank from 1 (highest value) to n (lowest value)."""
    n = len(x)
    order = np.argsort(-x)
    ranks = np.empty(n, dtype=float)
    ranks[order] = np.arange(1, n + 1, dtype=float)
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
        for j in range(i + 1, n):
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
    den = np.sqrt(np.sum((x - mx) ** 2) * np.sum((y - my) ** 2))
    return num / den if den > 0 else 0.0


baseline_ranks = rankdata(COMP)

# ============================================================================
#  COMPUTATIONS
# ============================================================================

# -- Composite descriptive statistics ----------------------------------------
comp_mean = np.mean(COMP)
comp_std = np.std(COMP, ddof=0)
comp_min = np.min(COMP)
comp_max = np.max(COMP)
comp_range = comp_max - comp_min
comp_cv = comp_std / comp_mean
comp_q1 = np.percentile(COMP, 25)
comp_q3 = np.percentile(COMP, 75)
comp_iqr = comp_q3 - comp_q1
comp_median = np.median(COMP)

# Gini
sorted_comp = np.sort(COMP)
cum_share = np.cumsum(sorted_comp) / np.sum(sorted_comp)
pop_share = np.arange(1, N + 1) / N
gini = 1.0 - 2.0 * np.trapezoid(cum_share, pop_share)

# Tier counts
n_high = sum(1 for c in CLASS if c == "highly_concentrated")
n_mod = sum(1 for c in CLASS if c == "moderately_concentrated")
n_mild = sum(1 for c in CLASS if c == "mildly_concentrated")

print("\n" + "=" * 72)
print("COMPOSITE DESCRIPTIVE STATISTICS")
print("=" * 72)
print(f"  Range: {NAMES[np.argmin(COMP)]} ({comp_min:.8f}) to "
      f"{NAMES[np.argmax(COMP)]} ({comp_max:.8f})")
print(f"  Mean: {comp_mean:.8f}  Std: {comp_std:.8f}  CV: {comp_cv:.4f}")
print(f"  Median: {comp_median:.8f}  IQR: {comp_iqr:.8f}")
print(f"  Gini: {gini:.6f}")
print(f"  Tiers: high={n_high}, moderate={n_mod}, mild={n_mild}")


# -- Variance decomposition -------------------------------------------------
axis_vars = np.var(AXES, axis=0, ddof=0)
cov_matrix = np.cov(AXES.T, ddof=0)
total_composite_var = np.sum(cov_matrix) / 36.0

marginal_contrib = np.sum(cov_matrix, axis=1) / 36.0
pct_contrib = marginal_contrib / total_composite_var * 100.0

own_var_share = np.array([cov_matrix[j, j] / 36.0 for j in range(6)])
cov_share = np.array([
    sum(cov_matrix[j, k] / 36.0 for k in range(6) if k != j)
    for j in range(6)
])

total_own = sum(cov_matrix[j, j] for j in range(6)) / 36.0
total_cross = sum(
    cov_matrix[j, k] for j in range(6) for k in range(6) if j != k
) / 36.0

pct_own_total = total_own / total_composite_var * 100.0
pct_cross_total = total_cross / total_composite_var * 100.0

# Defence + Logistics combined
pct_def_log = pct_contrib[3] + pct_contrib[5]
# Remaining four
pct_remaining = sum(pct_contrib[j] for j in [0, 1, 2, 4])

print("\n" + "=" * 72)
print("VARIANCE DECOMPOSITION")
print("=" * 72)
for j in range(6):
    print(f"  {AXIS_NAMES[j]:20s}: {pct_contrib[j]:.2f}%")
print(f"  Defence + Logistics: {pct_def_log:.2f}%")
print(f"  Remaining four:     {pct_remaining:.2f}%")
print(f"  Own-variance share: {pct_own_total:.2f}%")
print(f"  Cross-covariance:   {pct_cross_total:.2f}%")


# -- Axis dominance ----------------------------------------------------------
max_axis_idx = np.argmax(AXES, axis=1)
axis_dom_counts = np.zeros(6, dtype=int)
for i in range(N):
    axis_dom_counts[max_axis_idx[i]] += 1

# Mean dominance gap for defence-dominant countries
def_dom_gaps = []
log_dom_gaps = []
for i in range(N):
    sorted_vals = np.sort(AXES[i])[::-1]
    gap = sorted_vals[0] - sorted_vals[1]
    if max_axis_idx[i] == 3:
        def_dom_gaps.append(gap)
    elif max_axis_idx[i] == 5:
        log_dom_gaps.append(gap)

mean_def_gap = np.mean(def_dom_gaps) if def_dom_gaps else 0.0
mean_log_gap = np.mean(log_dom_gaps) if log_dom_gaps else 0.0

print("\n" + "=" * 72)
print("AXIS DOMINANCE COUNTS")
print("=" * 72)
for j in range(6):
    print(f"  {AXIS_NAMES[j]:20s}: {axis_dom_counts[j]}")
print(f"  Mean gap (def-dom): {mean_def_gap:.8f}")
print(f"  Mean gap (log-dom): {mean_log_gap:.8f}")


# -- Leave-one-axis-out ------------------------------------------------------
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

rank_displacement = np.zeros((N, 6), dtype=int)
for i in range(N):
    for j in range(6):
        rank_displacement[i, j] = int(baseline_ranks[i] - loo_ranks[i, j])

mean_abs_disp = np.mean(np.abs(rank_displacement), axis=0)
max_abs_disp = np.max(np.abs(rank_displacement), axis=0)

print("\n" + "=" * 72)
print("LEAVE-ONE-AXIS-OUT")
print("=" * 72)
for j in range(6):
    print(f"  Drop {AXIS_NAMES[j]:20s}: rho={loo_spearman[j]:.6f} "
          f"tau={loo_kendall[j]:.6f}  "
          f"mean|d|={mean_abs_disp[j]:.2f}  max|d|={int(max_abs_disp[j])}")


# -- Dirichlet weight perturbation ------------------------------------------
np.random.seed(42)
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

mc_spearmans = np.array([
    spearman_corr(baseline_ranks, mc_ranks[:, t]) for t in range(N_MC)
])
mean_mc_rho = np.mean(mc_spearmans)

print("\n" + "=" * 72)
print("DIRICHLET WEIGHT PERTURBATION")
print("=" * 72)
print(f"  Mean Spearman rho: {mean_mc_rho:.6f}")
vol_order = np.argsort(-std_rank)
for idx in vol_order[:5]:
    print(f"    {NAMES[idx]:15s}: sigma={std_rank[idx]:.2f}  "
          f"band=[{p5_rank[idx]:.0f}, {p95_rank[idx]:.0f}]")


# -- Correlation t-statistics ------------------------------------------------
pearson_matrix = np.corrcoef(AXES.T)
t_matrix = np.zeros((6, 6))
for j in range(6):
    for k in range(6):
        if j == k:
            t_matrix[j, k] = np.inf
        else:
            r = pearson_matrix[j, k]
            denom = 1 - r**2
            t_matrix[j, k] = (
                r * np.sqrt((N - 2) / denom) if denom > 0 else np.inf
            )

# Bonferroni: 15 pairs, alpha=0.05 => critical |t| approx 2.787
# (t_{0.05/(2*15), 25} = t_{0.001667, 25})
# Simpler: just check which pairs have |t| > 2.787
n_sig_bonf = 0
for j in range(6):
    for k in range(j + 1, 6):
        if abs(t_matrix[j, k]) > 2.787:
            n_sig_bonf += 1

# Financial axis: max |t|
fin_max_t = max(abs(t_matrix[0, k]) for k in range(1, 6))

print("\n" + "=" * 72)
print("CORRELATION STRUCTURE")
print("=" * 72)
print(f"  Significant after Bonferroni: {n_sig_bonf}/15")
print(f"  Financial max |t|: {fin_max_t:.4f}")
for j in range(6):
    for k in range(j + 1, 6):
        sig = "*" if abs(t_matrix[j, k]) > 2.787 else ""
        print(f"    {AXIS_NAMES[j]:15s} vs {AXIS_NAMES[k]:15s}: "
              f"r={pearson_matrix[j,k]:+.4f} t={t_matrix[j,k]:+.4f} {sig}")


# ============================================================================
#  TABLE GENERATION
# ============================================================================

print("\n" + "=" * 72)
print("GENERATING TABLES")
print("=" * 72)

# -- T01: Key summary statistics --------------------------------------------
lines = []
lines.append("% Table T01: Key summary statistics -- ISI composite, EU-27, 2024")
lines.append("\\begin{table}[htbp]")
lines.append("\\centering")
lines.append("\\caption{Key summary statistics of the \\ISI composite distribution, EU-27, "
             "vintage~2024, methodology~v1.0.}")
lines.append("\\label{tab:key-summary}")
lines.append("\\begin{tabular}{@{}lr@{}}")
lines.append("\\toprule")
lines.append("{\\textbf{Statistic}} & {\\textbf{Value}} \\\\")
lines.append("\\midrule")
lines.append(f"  Minimum (France, rank~27) & {comp_min:.8f} \\\\")
lines.append(f"  Maximum (Malta, rank~1) & {comp_max:.8f} \\\\")
lines.append(f"  Range & {comp_range:.8f} \\\\")
lines.append(f"  Mean (population) & {comp_mean:.8f} \\\\")
lines.append(f"  Median & {comp_median:.8f} \\\\")
lines.append(f"  Standard deviation (population) & {comp_std:.8f} \\\\")
lines.append(f"  Coefficient of variation & {comp_cv:.4f} \\\\")
lines.append(f"  IQR (P75 $-$ P25) & {comp_iqr:.8f} \\\\")
lines.append(f"  P25 & {comp_q1:.8f} \\\\")
lines.append(f"  P75 & {comp_q3:.8f} \\\\")
lines.append(f"  Gini coefficient & {gini:.6f} \\\\")
lines.append("\\addlinespace")
lines.append(f"  Highly concentrated ($\\geq 0.50$) & {n_high} \\\\")
lines.append(f"  Moderately concentrated ($[0.25, 0.50)$) & {n_mod} \\\\")
lines.append(f"  Mildly concentrated ($[0.15, 0.25)$) & {n_mild} \\\\")
lines.append("\\bottomrule")
lines.append("\\end{tabular}")
lines.append("\\end{table}")
write_file("T01_key_summary.tex", "\n".join(lines))


# -- T02: Variance decomposition --------------------------------------------
lines = []
lines.append("% Table T02: Variance decomposition of the ISI composite")
lines.append("\\begin{table}[htbp]")
lines.append("\\centering")
lines.append("\\caption{Variance contribution decomposition of the \\ISI composite.  "
             "Each axis's marginal contribution equals "
             "$(1/K^2)\\sum_{k=1}^{K}\\operatorname{Cov}(A_j, A_k)$, where $K=6$.  "
             "Own-variance and cross-covariance components are shown separately.}")
lines.append("\\label{tab:variance-decomp}")
lines.append("\\small")
lines.append("\\begin{tabular}{@{}l rrrr@{}}")
lines.append("\\toprule")
lines.append("\\textbf{Axis}"
             " & \\textbf{Own Var}"
             " & \\textbf{Cross Cov}"
             " & \\textbf{Marginal}"
             " & \\textbf{\\% Total} \\\\")
lines.append("\\midrule")
for j in range(6):
    lines.append(
        f"  {AXIS_NAMES[j]}"
        f" & {own_var_share[j]:.6f}"
        f" & {cov_share[j]:+.6f}"
        f" & {marginal_contrib[j]:.6f}"
        f" & {pct_contrib[j]:.2f} \\\\"
    )
lines.append("\\midrule")
lines.append(
    f"  Defence + Logistics"
    f" & {own_var_share[3]+own_var_share[5]:.6f}"
    f" & {cov_share[3]+cov_share[5]:+.6f}"
    f" & {marginal_contrib[3]+marginal_contrib[5]:.6f}"
    f" & {pct_def_log:.2f} \\\\"
)
lines.append(
    f"  Remaining four axes"
    f" & {sum(own_var_share[j] for j in [0,1,2,4]):.6f}"
    f" & {sum(cov_share[j] for j in [0,1,2,4]):+.6f}"
    f" & {sum(marginal_contrib[j] for j in [0,1,2,4]):.6f}"
    f" & {pct_remaining:.2f} \\\\"
)
lines.append("\\addlinespace")
lines.append(
    f"  Total"
    f" & {total_own:.6f}"
    f" & {total_cross:+.6f}"
    f" & {total_composite_var:.6f}"
    f" & 100.00 \\\\"
)
lines.append("\\addlinespace")
lines.append(
    f"  Own-var share of total"
    f" & \\multicolumn{{3}}{{r}}{{}}"
    f" & {pct_own_total:.2f} \\\\"
)
lines.append(
    f"  Cross-cov share of total"
    f" & \\multicolumn{{3}}{{r}}{{}}"
    f" & {pct_cross_total:.2f} \\\\"
)
lines.append("\\bottomrule")
lines.append("\\end{tabular}")
lines.append("\\end{table}")
write_file("T02_variance_decomposition.tex", "\n".join(lines))


# -- T03: Axis dominance counts ---------------------------------------------
lines = []
lines.append("% Table T03: Axis dominance counts")
lines.append("\\begin{table}[htbp]")
lines.append("\\centering")
lines.append("\\caption{Number of countries for which each axis is the highest-scoring axis.  "
             "Mean dominance gap: average difference between the highest and second-highest "
             "axis score among countries dominated by that axis.}")
lines.append("\\label{tab:dominance-counts}")
lines.append("\\begin{tabular}{@{}l r r l@{}}")
lines.append("\\toprule")
lines.append("\\textbf{Axis}"
             " & \\textbf{Countries}"
             " & \\textbf{Mean Gap}"
             " & \\textbf{Share} \\\\")
lines.append("\\midrule")
for j in range(6):
    # Compute mean gap for this axis's dominated countries
    gaps_j = []
    for i in range(N):
        if max_axis_idx[i] == j:
            sv = np.sort(AXES[i])[::-1]
            gaps_j.append(sv[0] - sv[1])
    mg = np.mean(gaps_j) if gaps_j else 0.0
    share_str = f"{axis_dom_counts[j]}/27 ({axis_dom_counts[j]/N*100:.1f}\\%)"
    lines.append(
        f"  {AXIS_NAMES[j]}"
        f" & {axis_dom_counts[j]}"
        f" & {mg:.8f}"
        f" & {share_str} \\\\"
    )
lines.append("\\midrule")
lines.append(
    f"  Defence + Logistics"
    f" & {axis_dom_counts[3]+axis_dom_counts[5]}"
    f" & {{--}}"
    f" & {(axis_dom_counts[3]+axis_dom_counts[5])/N*100:.1f}\\% \\\\"
)
lines.append("\\bottomrule")
lines.append("\\end{tabular}")
lines.append("\\end{table}")
write_file("T03_axis_dominance_counts.tex", "\n".join(lines))


# -- T04: LOO rank disruption -----------------------------------------------
lines = []
lines.append("% Table T04: Leave-one-axis-out rank disruption")
lines.append("\\begin{table}[htbp]")
lines.append("\\centering")
lines.append("\\caption{Leave-one-axis-out (LOO) rank disruption.  "
             "Spearman~$\\rho$ and Kendall~$\\tau$ measure rank-order "
             "agreement between the baseline and each LOO composite.  "
             "Lower values indicate greater rank disruption when the "
             "axis is removed.}")
lines.append("\\label{tab:loo-disruption}")
lines.append("\\begin{tabular}{@{}l rrrr@{}}")
lines.append("\\toprule")
lines.append("\\textbf{Excluded Axis}"
             " & $\\boldsymbol{\\rho}$"
             " & $\\boldsymbol{\\tau}$"
             " & \\textbf{Mean} $|\\Delta|$"
             " & \\textbf{Max} $|\\Delta|$ \\\\")
lines.append("\\midrule")
for j in range(6):
    lines.append(
        f"  {AXIS_NAMES[j]}"
        f" & {loo_spearman[j]:.6f}"
        f" & {loo_kendall[j]:.6f}"
        f" & {mean_abs_disp[j]:.2f}"
        f" & {int(max_abs_disp[j])} \\\\"
    )
lines.append("\\bottomrule")
lines.append("\\end{tabular}")
lines.append("\\end{table}")
write_file("T04_loo_rank_disruption.tex", "\n".join(lines))


# -- T05: Dirichlet volatility (top countries) ------------------------------
# Show top-8 by rank volatility
vol_order = np.argsort(-std_rank)
top_vol = vol_order[:8]

lines = []
lines.append("% Table T05: Dirichlet weight perturbation -- highest volatility countries")
lines.append("\\begin{table}[htbp]")
lines.append("\\centering")
lines.append("\\caption{Dirichlet weight perturbation ($\\alpha_j=10$, "
             "$N_{\\text{MC}}=10{,}000$, seed~42): eight highest-volatility "
             "countries by rank standard deviation.  "
             f"Aggregate mean Spearman~$\\rho = {mean_mc_rho:.3f}$.}}")
lines.append("\\label{tab:dirichlet-top}")
lines.append("\\begin{tabular}{@{}r l rrrr@{}}")
lines.append("\\toprule")
lines.append("\\textbf{Base Rk}"
             " & \\textbf{Country}"
             " & \\textbf{Mean Rk}"
             " & $\\boldsymbol{\\sigma}$"
             " & \\textbf{P5}"
             " & \\textbf{P95} \\\\")
lines.append("\\midrule")
for idx in top_vol:
    lines.append(
        f"  {int(baseline_ranks[idx])}"
        f" & {NAMES[idx]}"
        f" & {mean_rank[idx]:.2f}"
        f" & {std_rank[idx]:.2f}"
        f" & {p5_rank[idx]:.1f}"
        f" & {p95_rank[idx]:.1f} \\\\"
    )
lines.append("\\bottomrule")
lines.append("\\end{tabular}")
lines.append("\\end{table}")
write_file("T05_dirichlet_volatility_top.tex", "\n".join(lines))


# ============================================================================
#  APPENDIX TABLES
# ============================================================================

print("\n" + "=" * 72)
print("GENERATING APPENDIX TABLES")
print("=" * 72)

# -- TA1: Full variance detail (own vs cross per axis) ----------------------
lines = []
lines.append("% Table TA1: Full variance decomposition detail")
lines.append("\\begin{table}[htbp]")
lines.append("\\centering")
lines.append("\\caption{Detailed variance decomposition: own-variance and "
             "cross-covariance components per axis.  "
             "Own: $(1/36)\\operatorname{Var}(A_j)$.  "
             "Cross: $(1/36)\\sum_{k \\neq j}\\operatorname{Cov}(A_j, A_k)$.}")
lines.append("\\label{tab:full-variance-detail}")
lines.append("\\small")
lines.append("\\begin{tabular}{@{}l rrr rrr@{}}")
lines.append("\\toprule")
lines.append("\\textbf{Axis}"
             " & \\textbf{Own Var}"
             " & \\textbf{Cross Cov}"
             " & \\textbf{Marginal}"
             " & \\textbf{\\% Own}"
             " & \\textbf{\\% Cross}"
             " & \\textbf{\\% Total} \\\\")
lines.append("\\midrule")
for j in range(6):
    pct_own_j = own_var_share[j] / total_composite_var * 100
    pct_cross_j = cov_share[j] / total_composite_var * 100
    lines.append(
        f"  {AXIS_NAMES[j]}"
        f" & {own_var_share[j]:.6f}"
        f" & {cov_share[j]:+.6f}"
        f" & {marginal_contrib[j]:.6f}"
        f" & {pct_own_j:.2f}"
        f" & {pct_cross_j:+.2f}"
        f" & {pct_contrib[j]:.2f} \\\\"
    )
lines.append("\\midrule")
lines.append(
    f"  Total"
    f" & {total_own:.6f}"
    f" & {total_cross:+.6f}"
    f" & {total_composite_var:.6f}"
    f" & {pct_own_total:.2f}"
    f" & {pct_cross_total:+.2f}"
    f" & 100.00 \\\\"
)
lines.append("\\bottomrule")
lines.append("\\end{tabular}")
lines.append("\\end{table}")
write_file("TA1_full_variance_detail.tex", "\n".join(lines))


# -- TA2: Dominance per country ---------------------------------------------
second_max_idx = np.zeros(N, dtype=int)
for i in range(N):
    sorted_idx = np.argsort(-AXES[i])
    second_max_idx[i] = sorted_idx[1]

lines = []
lines.append("% Table TA2: Axis dominance per country")
lines.append("\\begin{longtable}{@{}rl r l r l r@{}}")
lines.append("\\caption{Axis dominance per country: highest- and "
             "second-highest-scoring axes, with dominance gap.}")
lines.append("\\label{tab:dominance-per-country}\\\\")
lines.append("\\toprule")
lines.append("{\\textbf{Rk}}"
             " & {\\textbf{Country}}"
             " & {\\textbf{Max Score}}"
             " & {\\textbf{Max Axis}}"
             " & {\\textbf{2nd Score}}"
             " & {\\textbf{2nd Axis}}"
             " & {\\textbf{Gap}} \\\\")
lines.append("\\midrule")
lines.append("\\endfirsthead")
lines.append("\\caption[]{Axis dominance per country (continued).}\\\\")
lines.append("\\toprule")
lines.append("{\\textbf{Rk}}"
             " & {\\textbf{Country}}"
             " & {\\textbf{Max Score}}"
             " & {\\textbf{Max Axis}}"
             " & {\\textbf{2nd Score}}"
             " & {\\textbf{2nd Axis}}"
             " & {\\textbf{Gap}} \\\\")
lines.append("\\midrule")
lines.append("\\endhead")
lines.append("\\bottomrule")
lines.append("\\endlastfoot")
for i in range(N):
    mi = max_axis_idx[i]
    si = second_max_idx[i]
    gap = AXES[i, mi] - AXES[i, si]
    lines.append(
        f"  {RANKS[i]:.0f}"
        f" & {NAMES[i]}"
        f" & {AXES[i, mi]:.8f}"
        f" & {AXIS_NAMES[mi]}"
        f" & {AXES[i, si]:.8f}"
        f" & {AXIS_NAMES[si]}"
        f" & {gap:.8f} \\\\"
    )
lines.append("\\end{longtable}")
write_file("TA2_dominance_per_country.tex", "\n".join(lines))


# -- TA3: Selected rank differences under LOO defence ----------------------
# Show the countries with largest displacement when defence is dropped
j_def = 3
disp_def = np.abs(rank_displacement[:, j_def])
disp_order = np.argsort(-disp_def)

lines = []
lines.append("% Table TA3: Rank displacement under LOO-defence")
lines.append("\\begin{table}[htbp]")
lines.append("\\centering")
lines.append("\\caption{Rank displacement when the defence axis is "
             "excluded (LOO-defence).  Countries ordered by absolute "
             f"displacement.  Spearman~$\\rho = {loo_spearman[j_def]:.6f}$, "
             f"Kendall~$\\tau = {loo_kendall[j_def]:.6f}$.}}")
lines.append("\\label{tab:loo-defence-ranks}")
lines.append("\\begin{tabular}{@{}r l r r r@{}}")
lines.append("\\toprule")
lines.append("{\\textbf{Base Rk}}"
             " & {\\textbf{Country}}"
             " & {\\textbf{LOO Rk}}"
             " & {$\\boldsymbol{\\Delta}$}"
             " & {$|\\boldsymbol{\\Delta}|$} \\\\")
lines.append("\\midrule")
for idx in disp_order:
    d = rank_displacement[idx, j_def]
    lines.append(
        f"  {int(baseline_ranks[idx])}"
        f" & {NAMES[idx]}"
        f" & {int(loo_ranks[idx, j_def])}"
        f" & {d:+d}"
        f" & {abs(d)} \\\\"
    )
lines.append("\\bottomrule")
lines.append("\\end{tabular}")
lines.append("\\end{table}")
write_file("TA3_loo_rank_diffs.tex", "\n".join(lines))


# ============================================================================
#  FIGURE DATA FILES
# ============================================================================

print("\n" + "=" * 72)
print("GENERATING FIGURE DATA")
print("=" * 72)

# -- F01: Variance bar chart data -------------------------------------------
lines = []
lines.append("% F01: Axis variance contribution (%) -- bar chart data")
lines.append("% axis_index axis_name pct_contribution")
for j in range(6):
    lines.append(f"{j} {AXIS_SLUGS[j]} {pct_contrib[j]:.4f}")
write_file("F01_variance_bar.dat", "\n".join(lines))


# -- F02: Dominance share data ---------------------------------------------
lines = []
lines.append("% F02: Axis dominance counts -- bar/pie data")
lines.append("% axis_index axis_name count")
for j in range(6):
    lines.append(f"{j} {AXIS_SLUGS[j]} {axis_dom_counts[j]}")
write_file("F02_dominance_share.dat", "\n".join(lines))


# -- F03: LOO Spearman rho data --------------------------------------------
lines = []
lines.append("% F03: LOO Spearman rho by excluded axis")
lines.append("% axis_index axis_name spearman_rho kendall_tau")
for j in range(6):
    lines.append(f"{j} {AXIS_SLUGS[j]} {loo_spearman[j]:.6f} {loo_kendall[j]:.6f}")
write_file("F03_loo_rho.dat", "\n".join(lines))


# ============================================================================
print("\n" + "=" * 72)
print("ALL COMPUTATIONS COMPLETE")
print(f"Tables written to: {TABLE_DIR}")
print("=" * 72)
