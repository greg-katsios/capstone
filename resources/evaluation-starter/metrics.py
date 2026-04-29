"""
Pure-Python statistical metrics for persona evaluation.

Implements inter-rater reliability and agreement metrics using only
the standard library (math, statistics). No numpy, scipy, or pandas.

Usage:
    from metrics import pearson_r, cohens_kappa, krippendorffs_alpha

    r = pearson_r([1, 2, 3, 4, 5], [1, 2, 3, 4, 5])  # 1.0
    k = cohens_kappa([1, 2, 3], [1, 2, 2])             # 0.4
"""

import math
import statistics
from collections import Counter
from typing import Sequence


# ── Pearson correlation ───────────────────────────────────────

def pearson_r(x: Sequence[float], y: Sequence[float]) -> float:
    """Pearson correlation coefficient between two sequences.

    r = Σ((xi - x̄)(yi - ȳ)) / √(Σ(xi - x̄)² · Σ(yi - ȳ)²)

    Returns 0.0 if either sequence has zero variance.
    """
    if len(x) != len(y) or len(x) < 2:
        return 0.0

    x_mean = statistics.mean(x)
    y_mean = statistics.mean(y)

    num = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, y))
    den_x = sum((xi - x_mean) ** 2 for xi in x)
    den_y = sum((yi - y_mean) ** 2 for yi in y)

    denom = math.sqrt(den_x * den_y)
    if denom == 0:
        return 0.0
    return num / denom


# ── Cohen's Kappa ─────────────────────────────────────────────

def cohens_kappa(rater1: Sequence[int], rater2: Sequence[int]) -> float:
    """Cohen's Kappa for inter-rater agreement between two raters.

    κ = (p_o - p_e) / (1 - p_e)

    where p_o = observed agreement, p_e = expected agreement by chance.
    Kappa > 0.6 is considered substantial agreement.
    """
    if len(rater1) != len(rater2) or len(rater1) == 0:
        return 0.0

    n = len(rater1)
    categories = sorted(set(rater1) | set(rater2))

    p_o = sum(1 for a, b in zip(rater1, rater2) if a == b) / n

    count1 = Counter(rater1)
    count2 = Counter(rater2)
    p_e = sum((count1[c] / n) * (count2[c] / n) for c in categories)

    if p_e == 1.0:
        return 1.0 if p_o == 1.0 else 0.0
    return (p_o - p_e) / (1 - p_e)


# ── Mean Absolute Error ──────────────────────────────────────

def mean_absolute_error(actual: Sequence[float], predicted: Sequence[float]) -> float:
    """Mean Absolute Error between two sequences.

    MAE = (1/n) · Σ|actual_i - predicted_i|
    """
    if len(actual) != len(predicted) or len(actual) == 0:
        return 0.0
    return sum(abs(a - p) for a, p in zip(actual, predicted)) / len(actual)


# ── Krippendorff's Alpha ─────────────────────────────────────

def krippendorffs_alpha(ratings_matrix: list[list[int | None]]) -> float:
    """Krippendorff's Alpha for multi-rater reliability.

    α = 1 - D_o / D_e

    where D_o = observed disagreement, D_e = expected disagreement.
    Alpha > 0.67 is the accepted threshold for reliable coding.

    Args:
        ratings_matrix: List of rater lists. ratings_matrix[r][i] is
            rater r's score for item i, or None if missing.
    """
    if not ratings_matrix or not ratings_matrix[0]:
        return 0.0

    n_raters = len(ratings_matrix)
    n_items = len(ratings_matrix[0])

    # Collect all non-None values per item
    item_values: list[list[int]] = []
    for i in range(n_items):
        vals = [ratings_matrix[r][i] for r in range(n_raters)
                if ratings_matrix[r][i] is not None]
        item_values.append(vals)

    # Observed disagreement: average squared difference within items
    d_o_num = 0.0
    d_o_pairs = 0
    for vals in item_values:
        m = len(vals)
        if m < 2:
            continue
        for a in range(m):
            for b in range(a + 1, m):
                d_o_num += (vals[a] - vals[b]) ** 2
                d_o_pairs += 1

    if d_o_pairs == 0:
        return 1.0

    d_o = d_o_num / d_o_pairs

    # Expected disagreement: average squared difference across all values
    all_values = [v for vals in item_values for v in vals]
    n_total = len(all_values)
    if n_total < 2:
        return 1.0

    d_e_num = 0.0
    d_e_pairs = 0
    for a in range(n_total):
        for b in range(a + 1, n_total):
            d_e_num += (all_values[a] - all_values[b]) ** 2
            d_e_pairs += 1

    d_e = d_e_num / d_e_pairs

    if d_e == 0:
        return 1.0
    return 1.0 - d_o / d_e


# ── Inter-rater reliability report ───────────────────────────

def inter_rater_report(ratings_matrix: list[list[int | None]]) -> dict:
    """Compute a full inter-rater reliability report.

    Args:
        ratings_matrix: List of rater lists. ratings_matrix[r][i] is
            rater r's score for item i, or None if missing.

    Returns:
        Dict with alpha, pairwise kappa, rater means, item means.
    """
    n_raters = len(ratings_matrix)
    n_items = len(ratings_matrix[0]) if ratings_matrix else 0

    alpha = krippendorffs_alpha(ratings_matrix)

    # Pairwise Cohen's Kappa (only for items both raters scored)
    pairwise_kappa = {}
    for a in range(n_raters):
        for b in range(a + 1, n_raters):
            shared = [(ratings_matrix[a][i], ratings_matrix[b][i])
                      for i in range(n_items)
                      if ratings_matrix[a][i] is not None
                      and ratings_matrix[b][i] is not None]
            if shared:
                r1, r2 = zip(*shared)
                pairwise_kappa[f"rater_{a}_vs_{b}"] = cohens_kappa(r1, r2)

    kappa_values = list(pairwise_kappa.values())
    mean_kappa = statistics.mean(kappa_values) if kappa_values else 0.0

    # Per-rater means
    rater_means = []
    for r in range(n_raters):
        vals = [v for v in ratings_matrix[r] if v is not None]
        rater_means.append(statistics.mean(vals) if vals else 0.0)

    # Per-item means
    item_means = []
    for i in range(n_items):
        vals = [ratings_matrix[r][i] for r in range(n_raters)
                if ratings_matrix[r][i] is not None]
        item_means.append(statistics.mean(vals) if vals else 0.0)

    return {
        "krippendorffs_alpha": round(alpha, 4),
        "pairwise_kappa": {k: round(v, 4) for k, v in pairwise_kappa.items()},
        "mean_kappa": round(mean_kappa, 4),
        "rater_means": [round(m, 2) for m in rater_means],
        "item_means": [round(m, 2) for m in item_means],
        "n_raters": n_raters,
        "n_items": n_items,
    }


# ── Summary statistics ────────────────────────────────────────

def summary_stats(values: Sequence[float]) -> dict:
    """Basic descriptive statistics for a sequence of values."""
    if not values:
        return {"mean": 0, "median": 0, "stdev": 0, "min": 0, "max": 0, "count": 0}
    vals = list(values)
    return {
        "mean": round(statistics.mean(vals), 2),
        "median": round(statistics.median(vals), 2),
        "stdev": round(statistics.stdev(vals), 2) if len(vals) > 1 else 0,
        "min": min(vals),
        "max": max(vals),
        "count": len(vals),
    }
