"""Build unified evidence quality dataset from 4 source projects.

LEFT JOIN from FragilityAtlas base (403 reviews).
Missing components are null, not defaulted.
Scoring re-weights available components.
Output: data/reviews.json
"""

import csv
import json
from pathlib import Path


def load_csv(path):
    """Load CSV into dict keyed by review_id. Returns {} if file missing."""
    data = {}
    p = Path(path)
    if not p.exists():
        print(f"  WARNING: {path} not found, skipping")
        return data
    with open(p, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            data[row['review_id']] = row
    return data


def safe_float(val, default=None):
    """Parse float, return default if empty/invalid."""
    if val is None or val == '':
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def safe_int(val, default=None):
    """Parse int, return default if empty/invalid."""
    if val is None or val == '':
        return default
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return default


def compute_score(fragility, bias, prediction, orb):
    """Compute weighted quality score from available components.

    Base weights: Fragility 35%, Bias 25%, Prediction 25%, ORB 15%.
    Re-weights proportionally when a component is None.
    Returns (score, grade) or (None, 'Insufficient') if <2 components.
    """
    components = []
    weights = []

    if fragility is not None:
        components.append(fragility)
        weights.append(0.35)
    if bias is not None:
        components.append(bias)
        weights.append(0.25)
    if prediction is not None:
        components.append(prediction)
        weights.append(0.25)
    if orb is not None:
        components.append(orb)
        weights.append(0.15)

    if len(components) < 2:
        return None, 'Insufficient'

    total_w = sum(weights)
    score = sum(c * w / total_w for c, w in zip(components, weights))
    score = round(score, 1)

    if score >= 80:
        grade = 'A'
    elif score >= 60:
        grade = 'B'
    elif score >= 40:
        grade = 'C'
    else:
        grade = 'D'

    return score, grade


BIAS_MAP = {'Clean': 100, 'Suspected': 60, 'Confirmed': 20, 'Discordant': 40}
PRED_MAP = {'CONCORDANT_SIG': 100, 'CONCORDANT_NS': 60, 'FALSE_REASSURANCE': 20}


def main():
    print("Loading source datasets...")
    fragility = load_csv(r'C:\FragilityAtlas\data\output\fragility_atlas_results.csv')
    bias = load_csv(r'C:\BiasForensics\data\output\bias_forensics_results.csv')
    prediction = load_csv(r'C:\PredictionGap\data\output\prediction_gap_results.csv')
    orb = load_csv(r'C:\OutcomeReportingBias\data\output\orb_results.csv')

    print(f"  FragilityAtlas: {len(fragility)} reviews")
    print(f"  BiasForensics:  {len(bias)} reviews")
    print(f"  PredictionGap:  {len(prediction)} reviews")
    print(f"  ORB:            {len(orb)} reviews")

    # LEFT JOIN from FragilityAtlas base
    reviews = []
    for rid in sorted(fragility.keys()):
        fa = fragility[rid]
        bf = bias.get(rid)
        pg = prediction.get(rid)
        ob = orb.get(rid)

        # Count available sources
        completeness = 1  # FA always present
        if bf is not None:
            completeness += 1
        if pg is not None:
            completeness += 1
        if ob is not None:
            completeness += 1

        # Component scores (None if source missing)
        frag_score = safe_float(fa.get('robustness_score'))

        bias_score = None
        if bf is not None:
            bc = bf.get('bias_class', '')
            bias_score = BIAS_MAP.get(bc)

        pred_score = None
        if pg is not None:
            disc = pg.get('discordance', '')
            pred_score = PRED_MAP.get(disc)

        orb_raw = None
        orb_score_val = None
        if ob is not None:
            orb_raw = safe_float(ob.get('orb_score'))
            if orb_raw is not None:
                orb_score_val = round(100 - orb_raw, 1)

        quality_score, quality_grade = compute_score(
            frag_score, bias_score, pred_score, orb_score_val
        )

        # Build nested record
        record = {
            'review_id': rid,
            'analysis_name': fa.get('analysis_name', ''),
            'k': safe_int(fa.get('k')),
            'review_doi': fa.get('review_doi', ''),
            'completeness': completeness,
            'quality_score': quality_score,
            'quality_grade': quality_grade,
            'fragility': {
                'robustness_score': frag_score,
                'classification': fa.get('classification', ''),
                'top_dimension': fa.get('top_dimension', ''),
                'frac_significant': safe_float(fa.get('frac_significant')),
                'frac_reversed': safe_float(fa.get('frac_reversed')),
            },
            'bias': {
                'bias_class': bf.get('bias_class', ''),
                'n_detect': safe_int(bf.get('n_detect')),
                'egger_p': safe_float(bf.get('egger_p')),
                'egger_sig': safe_int(bf.get('egger_sig')),
                'tf_k0': safe_int(bf.get('tf_k0')),
                'petpeese_theta': safe_float(bf.get('petpeese_theta')),
                'petpeese_method': bf.get('petpeese_method', ''),
            } if bf is not None else None,
            'prediction': {
                'discordance': pg.get('discordance', ''),
                'pi_ci_ratio': safe_float(pg.get('pi_ci_ratio')),
                'tau2': safe_float(pg.get('tau2')),
                'I2': safe_float(pg.get('I2')),
                'ci_lo': safe_float(pg.get('ci_lo')),
                'ci_hi': safe_float(pg.get('ci_hi')),
                'pi_lo': safe_float(pg.get('pi_lo')),
                'pi_hi': safe_float(pg.get('pi_hi')),
            } if pg is not None else None,
            'orb': {
                'orb_class': ob.get('orb_class', ''),
                'orb_score': safe_float(ob.get('orb_score')),
                'excess_significance': safe_float(ob.get('excess_significance')),
                'outlier_ratio': safe_float(ob.get('outlier_ratio')),
            } if ob is not None else None,
        }
        reviews.append(record)

    # Output JSON
    out_path = Path(r'C:\EvidenceQuality\data\reviews.json')
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(reviews, f, indent=None)

    # Summary
    n = len(reviews)
    grades = {g: sum(1 for r in reviews if r['quality_grade'] == g) for g in ['A', 'B', 'C', 'D', 'Insufficient']}
    scored = [r['quality_score'] for r in reviews if r['quality_score'] is not None]
    comp4 = sum(1 for r in reviews if r['completeness'] == 4)
    comp3 = sum(1 for r in reviews if r['completeness'] == 3)

    print(f"\n{'='*50}")
    print("UNIFIED EVIDENCE QUALITY REPORT")
    print(f"{'='*50}")
    print(f"  {n} Cochrane reviews scored")
    print(f"  Completeness: {comp4} with 4/4, {comp3} with 3/4")
    if scored:
        print(f"  Mean quality: {sum(scored)/len(scored):.1f}/100")
        print(f"  Median quality: {sorted(scored)[len(scored)//2]:.1f}/100")
    print()
    for g in ['A', 'B', 'C', 'D']:
        c = grades.get(g, 0)
        print(f"  Grade {g}: {c:4d} ({c/n*100:5.1f}%)")
    print(f"\n  Output: {out_path}")
    print(f"  JSON size: {out_path.stat().st_size / 1024:.0f} KB")


if __name__ == '__main__':
    main()
