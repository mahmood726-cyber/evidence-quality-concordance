"""The Cochrane Quality Concordance: merging 6 quality dimensions across 403 reviews.

Produces:
  - unified_concordance.csv: one row per review, all quality metrics
  - concordance_matrix.json: Spearman correlation matrix + p-values
  - concordance_summary.json: headline stats
"""

import csv
import json
import math
import sys
from pathlib import Path
from collections import Counter

# ═══════════════════════════════════════════════════
# 1. LOAD ALL 6 DATASETS
# ═══════════════════════════════════════════════════

def load_csv(path, key='review_id'):
    data = {}
    with open(path, encoding='utf-8', errors='replace') as f:
        for row in csv.DictReader(f):
            data[row[key]] = row
    return data


def load_reproducer(path):
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    out = {}
    for r in data:
        rid = r['cert']['review_id']
        sl = r.get('study_level', {})
        out[rid] = {
            'repro_class': r['cert']['classification'],
            'repro_total_k': sl.get('total_k', 0),
            'repro_n_pdf': sl.get('n_with_pdf', 0),
            'repro_rate_strict': sl.get('rate_strict', 0),
            'repro_rate_moderate': sl.get('rate_moderate', 0),
            'repro_primary_error': r.get('errors', {}).get('primary_error_source', 'unknown'),
        }
    return out


def load_overlap(pairs_path, studies_path):
    """Per-review: max overlap with any other review, number of shared studies."""
    review_max_overlap = {}

    with open(pairs_path, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            r1, r2 = row['review_1'], row['review_2']
            n = int(row['n_shared'])
            j = float(row['jaccard'])
            for rid in [r1, r2]:
                if rid not in review_max_overlap or j > review_max_overlap[rid]['max_jaccard']:
                    review_max_overlap[rid] = {
                        'max_jaccard': j,
                        'max_shared': n,
                        'overlap_partner': r2 if rid == r1 else r1,
                    }

    return review_max_overlap


def main():
    print("The Cochrane Quality Concordance")
    print("=" * 40)

    # Load sources
    fragility = load_csv(r'C:\FragilityAtlas\data\output\fragility_atlas_results.csv')
    bias = load_csv(r'C:\BiasForensics\data\output\bias_forensics_results.csv')
    prediction = load_csv(r'C:\PredictionGap\data\output\prediction_gap_results.csv')
    orb = load_csv(r'C:\OutcomeReportingBias\data\output\orb_results.csv')
    reproducer = load_reproducer(r'C:\Models\MetaReproducer\data\results\summary.json')
    overlap = load_overlap(
        r'C:\OverlapDetector\data\output\overlap_pairs.csv',
        r'C:\OverlapDetector\data\output\overlap_top_studies.csv',
    )

    print(f"  Fragility Atlas: {len(fragility)} reviews")
    print(f"  Bias Forensics:  {len(bias)} reviews")
    print(f"  Prediction Gap:  {len(prediction)} reviews")
    print(f"  ORB Detector:    {len(orb)} reviews")
    print(f"  MetaReproducer:  {len(reproducer)} reviews")
    print(f"  Overlap (pairs): {len(overlap)} reviews with any overlap")

    # Common IDs (Fragility + Prediction + ORB = 403 reviews with k>=3)
    common = set(fragility.keys()) & set(prediction.keys()) & set(orb.keys())
    print(f"\n  Common reviews (Frag + Pred + ORB): {len(common)}")

    # ═══════════════════════════════════════════════════
    # 2. BUILD UNIFIED TABLE
    # ═══════════════════════════════════════════════════

    rows = []
    for rid in sorted(common):
        f = fragility[rid]
        p = prediction[rid]
        o = orb[rid]
        b = bias.get(rid, {})
        r = reproducer.get(rid, {})
        ov = overlap.get(rid, {})

        row = {
            'review_id': rid,
            'k': int(f.get('k', 0)),
            'scale': f.get('scale', ''),

            # Dimension 1: Fragility (0-100, higher = more robust)
            'fragility_score': float(f.get('robustness_score', 0)),
            'fragility_class': f.get('classification', ''),
            'fragility_frac_sig': float(f.get('frac_significant', 0)),
            'fragility_top_dim': f.get('top_dimension', ''),

            # Dimension 2: Publication Bias (concordance 0-8, higher = more methods agree on bias)
            'bias_n_detect': int(float(b.get('n_detect', 0))),
            'bias_concordance': int(float(b.get('concordance', 0))),
            'bias_class': b.get('bias_class', 'unknown'),
            'bias_egger_p': float(b.get('egger_p', 1)),
            'bias_tf_k0': int(float(b.get('tf_k0', 0))),

            # Dimension 3: Prediction Gap (PI/CI ratio, higher = more prediction uncertainty)
            'pred_pi_ci_ratio': float(p.get('pi_ci_ratio', 1)),
            'pred_discordance': p.get('discordance', ''),
            'pred_I2': float(p.get('I2', 0)),
            'pred_tau2': float(p.get('tau2', 0)),

            # Dimension 4: ORB (score 0-100, higher = more ORB risk)
            'orb_score': float(o.get('orb_score', 0)),
            'orb_class': o.get('orb_class', ''),
            'orb_excess_sig': float(o.get('excess_significance', 0)),

            # Dimension 5: Reproducibility (OA coverage, 0-1)
            'repro_class': r.get('repro_class', 'unknown'),
            'repro_oa_coverage': (int(r.get('repro_n_pdf', 0)) / max(1, int(r.get('repro_total_k', 1)))),
            'repro_rate_strict': float(r.get('repro_rate_strict', 0)),

            # Dimension 6: Overlap (max Jaccard with any other review)
            'overlap_max_jaccard': ov.get('max_jaccard', 0),
            'overlap_max_shared': ov.get('max_shared', 0),
        }

        # Composite quality score (0-100, higher = better quality)
        # Fragility: robustness_score directly (0-100)
        # Bias: invert (fewer detections = better), scale 0-100
        # Prediction: invert PI/CI ratio, scale
        # ORB: invert score
        # Reproducibility: OA coverage * 100
        # Overlap: invert Jaccard (lower = better)

        d1 = row['fragility_score']
        d2 = max(0, 100 - row['bias_n_detect'] * 12.5)  # 0 detections = 100, 8 = 0
        d3 = max(0, 100 - (row['pred_pi_ci_ratio'] - 1) * 20)  # ratio=1 → 100, ratio=6 → 0
        d4 = max(0, 100 - row['orb_score'])
        d5 = row['repro_oa_coverage'] * 100
        d6 = max(0, 100 - row['overlap_max_jaccard'] * 200)  # jaccard=0 → 100, jaccard=0.5 → 0

        row['composite_score'] = round((d1 + d2 + d3 + d4 + d5 + d6) / 6, 1)
        row['d1_fragility_norm'] = round(d1, 1)
        row['d2_bias_norm'] = round(d2, 1)
        row['d3_prediction_norm'] = round(d3, 1)
        row['d4_orb_norm'] = round(d4, 1)
        row['d5_repro_norm'] = round(d5, 1)
        row['d6_overlap_norm'] = round(d6, 1)

        # Grade: A (>=80), B (60-79), C (40-59), D (<40)
        cs = row['composite_score']
        row['grade'] = 'A' if cs >= 80 else 'B' if cs >= 60 else 'C' if cs >= 40 else 'D'

        rows.append(row)

    print(f"\n  Unified rows: {len(rows)}")

    # ═══════════════════════════════════════════════════
    # 3. CORRELATION MATRIX (Spearman)
    # ═══════════════════════════════════════════════════

    dims = ['d1_fragility_norm', 'd2_bias_norm', 'd3_prediction_norm',
            'd4_orb_norm', 'd5_repro_norm', 'd6_overlap_norm']
    dim_labels = ['Fragility', 'Pub Bias', 'Prediction Gap', 'ORB', 'Reproducibility', 'Overlap']

    def spearman(x, y):
        """Spearman rank correlation."""
        n = len(x)
        if n < 3:
            return 0, 1
        rx = rank_data(x)
        ry = rank_data(y)
        d2 = sum((a - b) ** 2 for a, b in zip(rx, ry))
        rho = 1 - 6 * d2 / (n * (n * n - 1))
        # t-test for significance
        if abs(rho) >= 1:
            return rho, 0
        t = rho * math.sqrt((n - 2) / (1 - rho * rho))
        # Approximate p-value using normal for large n
        p = 2 * (1 - normal_cdf(abs(t) / math.sqrt(1 + t * t / n)))
        return rho, p

    def rank_data(values):
        indexed = sorted(enumerate(values), key=lambda x: x[1])
        ranks = [0.0] * len(values)
        i = 0
        while i < len(indexed):
            j = i
            while j < len(indexed) - 1 and indexed[j + 1][1] == indexed[j][1]:
                j += 1
            avg_rank = (i + j) / 2 + 1
            for k in range(i, j + 1):
                ranks[indexed[k][0]] = avg_rank
            i = j + 1
        return ranks

    def normal_cdf(x):
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))

    corr_matrix = {}
    p_matrix = {}
    for i, di in enumerate(dims):
        for j, dj in enumerate(dims):
            xi = [r[di] for r in rows]
            xj = [r[dj] for r in rows]
            rho, p = spearman(xi, xj)
            key = f"{dim_labels[i]} vs {dim_labels[j]}"
            corr_matrix[key] = round(rho, 3)
            p_matrix[key] = round(p, 4)

    # Print correlation matrix
    print("\n" + "=" * 60)
    print("SPEARMAN CORRELATION MATRIX")
    print("=" * 60)
    print(f"{'':>18s}", end='')
    for l in dim_labels:
        print(f"{l:>14s}", end='')
    print()

    for i, li in enumerate(dim_labels):
        print(f"{li:>18s}", end='')
        for j, lj in enumerate(dim_labels):
            key = f"{li} vs {lj}"
            rho = corr_matrix[key]
            star = '*' if p_matrix[key] < 0.05 else ' '
            print(f"  {rho:>6.3f}{star:>1s}    ", end='')
        print()

    # ═══════════════════════════════════════════════════
    # 4. HEADLINE FINDINGS
    # ═══════════════════════════════════════════════════

    grades = Counter(r['grade'] for r in rows)
    scores = [r['composite_score'] for r in rows]
    mean_score = sum(scores) / len(scores)
    median_score = sorted(scores)[len(scores) // 2]

    # Key cross-dimension stats
    fragile_and_biased = sum(1 for r in rows
                            if r['fragility_class'] in ('Fragile', 'Unstable')
                            and r['bias_class'] in ('Confirmed', 'Discordant'))
    fragile_total = sum(1 for r in rows if r['fragility_class'] in ('Fragile', 'Unstable'))
    biased_total = sum(1 for r in rows if r['bias_class'] in ('Confirmed', 'Discordant'))

    false_reassurance_and_orb = sum(1 for r in rows
                                    if r['pred_discordance'] == 'FALSE_REASSURANCE'
                                    and r['orb_class'] == 'High_Risk')
    false_reassurance_total = sum(1 for r in rows if r['pred_discordance'] == 'FALSE_REASSURANCE')
    orb_high_total = sum(1 for r in rows if r['orb_class'] == 'High_Risk')

    print("\n" + "=" * 60)
    print("HEADLINE FINDINGS")
    print("=" * 60)
    print(f"  Reviews analyzed: {len(rows)}")
    print(f"  Composite score: mean={mean_score:.1f}, median={median_score:.1f}")
    print(f"  Grades: A={grades['A']}, B={grades['B']}, C={grades['C']}, D={grades['D']}")
    print(f"  Fragile+Biased: {fragile_and_biased}/{len(rows)} ({100*fragile_and_biased/len(rows):.1f}%)")
    print(f"  False reassurance+High ORB: {false_reassurance_and_orb}/{len(rows)} ({100*false_reassurance_and_orb/len(rows):.1f}%)")
    print(f"  Fragile total: {fragile_total} | Biased total: {biased_total}")
    print(f"  False reassurance total: {false_reassurance_total} | High ORB total: {orb_high_total}")

    # Find the strongest and weakest correlations (off-diagonal)
    off_diag = {}
    for i, li in enumerate(dim_labels):
        for j, lj in enumerate(dim_labels):
            if i < j:
                key = f"{li} vs {lj}"
                off_diag[key] = corr_matrix[key]

    strongest = max(off_diag, key=lambda k: abs(off_diag[k]))
    weakest = min(off_diag, key=lambda k: abs(off_diag[k]))
    print(f"\n  Strongest correlation: {strongest} (rho={off_diag[strongest]:.3f})")
    print(f"  Weakest correlation:  {weakest} (rho={off_diag[weakest]:.3f})")

    # Mean absolute off-diagonal correlation
    mean_abs_rho = sum(abs(v) for v in off_diag.values()) / len(off_diag)
    print(f"  Mean |rho| off-diagonal: {mean_abs_rho:.3f}")
    if mean_abs_rho < 0.3:
        print("  >> QUALITY DIMENSIONS ARE LARGELY ORTHOGONAL")
    else:
        print("  >> QUALITY DIMENSIONS SHOW MODERATE CORRELATION")

    # ═══════════════════════════════════════════════════
    # 5. EXPORT
    # ═══════════════════════════════════════════════════

    output_dir = Path('C:/EvidenceQuality/data')
    output_dir.mkdir(parents=True, exist_ok=True)

    # CSV
    fields = list(rows[0].keys())
    with open(output_dir / 'unified_concordance.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    # Summary JSON
    summary = {
        'n_reviews': len(rows),
        'grades': dict(grades),
        'mean_composite': round(mean_score, 1),
        'median_composite': round(median_score, 1),
        'dimension_means': {
            dl: round(sum(r[d] for r in rows) / len(rows), 1)
            for d, dl in zip(dims, dim_labels)
        },
        'cross_dimension': {
            'fragile_and_biased': fragile_and_biased,
            'false_reassurance_and_high_orb': false_reassurance_and_orb,
            'fragile_total': fragile_total,
            'biased_total': biased_total,
        },
        'correlation_matrix': {k: v for k, v in corr_matrix.items()
                               if dim_labels.index(k.split(' vs ')[0]) < dim_labels.index(k.split(' vs ')[1])},
        'p_values': {k: v for k, v in p_matrix.items()
                     if dim_labels.index(k.split(' vs ')[0]) < dim_labels.index(k.split(' vs ')[1])},
        'mean_abs_rho': round(mean_abs_rho, 3),
        'strongest_pair': strongest,
        'weakest_pair': weakest,
    }

    with open(output_dir / 'concordance_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

    # Correlation matrix as flat JSON
    with open(output_dir / 'concordance_matrix.json', 'w', encoding='utf-8') as f:
        json.dump({
            'labels': dim_labels,
            'rho': [[corr_matrix[f"{li} vs {lj}"] for lj in dim_labels] for li in dim_labels],
            'p': [[p_matrix[f"{li} vs {lj}"] for lj in dim_labels] for li in dim_labels],
        }, f, indent=2)

    print(f"\n  Saved to {output_dir}/")
    print("  - unified_concordance.csv")
    print("  - concordance_summary.json")
    print("  - concordance_matrix.json")


if __name__ == '__main__':
    main()
