"""Merge all evidence quality audits into one unified dataset.

Sources:
1. Fragility Atlas: robustness score, classification, dimension attribution
2. Bias Forensics: bias fingerprint, 8 methods, classification
3. Prediction Gap: PI/CI discordance, false reassurance
4. ORB Detector: outcome reporting bias risk score

Output: unified CSV with one row per review (matched by review_id)
"""

import csv
import json
from pathlib import Path


def load_csv(path):
    """Load CSV into dict keyed by review_id."""
    data = {}
    with open(path, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            data[row['review_id']] = row
    return data


def main():
    # Load all 4 datasets
    fragility = load_csv(r'C:\FragilityAtlas\data\output\fragility_atlas_results.csv')
    bias = load_csv(r'C:\BiasForensics\data\output\bias_forensics_results.csv')
    prediction = load_csv(r'C:\PredictionGap\data\output\prediction_gap_results.csv')
    orb = load_csv(r'C:\OutcomeReportingBias\data\output\orb_results.csv')

    # Find common review IDs
    common = set(fragility.keys()) & set(prediction.keys())
    print(f"Reviews in Fragility Atlas: {len(fragility)}")
    print(f"Reviews in Bias Forensics: {len(bias)}")
    print(f"Reviews in Prediction Gap: {len(prediction)}")
    print(f"Reviews in ORB: {len(orb)}")
    print(f"Common (Fragility + Prediction): {len(common)}")

    # Build unified rows
    unified = []
    for rid in sorted(common):
        f = fragility.get(rid, {})
        b = bias.get(rid, {})
        p = prediction.get(rid, {})
        o = orb.get(rid, {})

        # Compute overall evidence quality score (0-100, higher = better)
        # Components:
        # 1. Robustness (from Fragility Atlas): 0-100 directly
        robustness = float(f.get('robustness_score', 50))

        # 2. Bias freedom: 100 if Clean, 70 if Suspected, 30 if Confirmed, 50 if Discordant
        bias_class = b.get('bias_class', 'Suspected')
        bias_score = {'Clean': 100, 'Suspected': 60, 'Confirmed': 20, 'Discordant': 40}.get(bias_class, 50)

        # 3. Prediction concordance: 100 if concordant sig, 50 if concordant NS, 20 if false reassurance
        disc = p.get('discordance', 'CONCORDANT_NS')
        pred_score = {'CONCORDANT_SIG': 100, 'CONCORDANT_NS': 60, 'FALSE_REASSURANCE': 20, 'HIDDEN_SIGNAL': 50}.get(disc, 50)

        # 4. ORB freedom: 100 if Low, 60 if Moderate, 20 if High
        orb_class = o.get('orb_class', 'Low_Risk')
        orb_score = {'Low_Risk': 100, 'Moderate_Risk': 60, 'High_Risk': 20}.get(orb_class, 50)

        # Overall: weighted average
        overall = (robustness * 0.35 + bias_score * 0.25 + pred_score * 0.25 + orb_score * 0.15)

        # Grade
        if overall >= 80:
            grade = 'A'
        elif overall >= 60:
            grade = 'B'
        elif overall >= 40:
            grade = 'C'
        else:
            grade = 'D'

        unified.append({
            'review_id': rid,
            'analysis_name': f.get('analysis_name', p.get('analysis_name', '')),
            'k': f.get('k', p.get('k', '')),
            # Fragility
            'robustness_score': robustness,
            'fragility_class': f.get('classification', ''),
            # Bias
            'bias_class': bias_class,
            'egger_sig': b.get('egger_sig', ''),
            'n_detect': b.get('n_detect', ''),
            # Prediction
            'pi_ci_ratio': p.get('pi_ci_ratio', ''),
            'discordance': disc,
            # ORB
            'orb_class': orb_class,
            'orb_score_raw': o.get('orb_score', ''),
            'excess_sig': o.get('excess_significance', ''),
            # Overall
            'quality_score': round(overall, 1),
            'quality_grade': grade,
        })

    # Export
    out_path = Path(r'C:\EvidenceQuality\data\unified_quality.csv')
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(unified[0].keys())
    with open(out_path, 'w', newline='', encoding='utf-8') as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fields)
        writer.writeheader()
        for row in unified:
            writer.writerow(row)

    # Summary
    n = len(unified)
    grades = {g: sum(1 for r in unified if r['quality_grade'] == g) for g in 'ABCD'}
    scores = [r['quality_score'] for r in unified]

    summary = {
        'n_reviews': n,
        'grades': grades,
        'mean_score': round(sum(scores) / n, 1),
        'median_score': round(sorted(scores)[n // 2], 1),
        'components': {
            'fragility_fragile_or_unstable': sum(1 for r in unified if r['fragility_class'] in ('Fragile', 'Unstable')),
            'bias_confirmed_or_discordant': sum(1 for r in unified if r['bias_class'] in ('Confirmed', 'Discordant')),
            'prediction_false_reassurance': sum(1 for r in unified if r['discordance'] == 'FALSE_REASSURANCE'),
            'orb_high_risk': sum(1 for r in unified if r['orb_class'] == 'High_Risk'),
        },
    }
    with open(r'C:\EvidenceQuality\data\unified_summary.json', 'w', encoding='utf-8') as f_out:
        json.dump(summary, f_out, indent=2)

    print()
    print("=" * 50)
    print("UNIFIED EVIDENCE QUALITY REPORT")
    print("=" * 50)
    print(f"  {n} Cochrane reviews scored")
    print(f"  Mean quality: {summary['mean_score']}/100")
    print(f"  Median quality: {summary['median_score']}/100")
    print()
    for g in 'ABCD':
        pct = grades[g] / n * 100
        print(f"  Grade {g}: {grades[g]:4d} ({pct:5.1f}%)")
    print()
    print(f"  Fragile/Unstable: {summary['components']['fragility_fragile_or_unstable']}")
    print(f"  Bias Confirmed/Discordant: {summary['components']['bias_confirmed_or_discordant']}")
    print(f"  Prediction False Reassurance: {summary['components']['prediction_false_reassurance']}")
    print(f"  ORB High Risk: {summary['components']['orb_high_risk']}")


if __name__ == '__main__':
    main()
