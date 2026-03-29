"""Build unified evidence quality dataset from 4 source projects.

LEFT JOIN from FragilityAtlas base (403 reviews).
Missing components are null, not defaulted.
Scoring re-weights available components.
Output: data/reviews.json
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_SOURCE_ROOT = PROJECT_ROOT.parent
DEFAULT_OUT_PATH = PROJECT_ROOT / "data" / "reviews.json"


def load_csv(path, required=True):
    """Load CSV into dict keyed by review_id."""
    data = {}
    p = Path(path)
    if not p.exists():
        if required:
            raise FileNotFoundError(f"Required source file not found: {p}")
        print(f"  WARNING: {p} not found, skipping")
        return data
    with open(p, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            data[row["review_id"]] = row
    return data


def safe_float(val, default=None):
    """Parse float, return default if empty/invalid."""
    if val is None or val == "":
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def safe_int(val, default=None):
    """Parse int, return default if empty/invalid."""
    if val is None or val == "":
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
        return None, "Insufficient"

    total_w = sum(weights)
    score = sum(c * w / total_w for c, w in zip(components, weights))
    score = round(score, 1)

    if score >= 80:
        grade = "A"
    elif score >= 60:
        grade = "B"
    elif score >= 40:
        grade = "C"
    else:
        grade = "D"

    return score, grade


BIAS_MAP = {"Clean": 100, "Suspected": 60, "Confirmed": 20, "Discordant": 40}
PRED_MAP = {"CONCORDANT_SIG": 100, "CONCORDANT_NS": 60, "FALSE_REASSURANCE": 20}


def _env_or_default(value, env_name, default):
    if value:
        return Path(value)
    env_value = os.environ.get(env_name)
    if env_value:
        return Path(env_value)
    return Path(default)


def resolve_paths(
    source_root=None,
    fragility_csv=None,
    bias_csv=None,
    prediction_csv=None,
    orb_csv=None,
    out_path=None,
):
    """Resolve input/output paths from args, env vars, or project-relative defaults."""
    source_root = _env_or_default(
        source_root,
        "EVIDENCE_QUALITY_SOURCE_ROOT",
        DEFAULT_SOURCE_ROOT,
    )
    return {
        "source_root": source_root,
        "fragility_csv": _env_or_default(
            fragility_csv,
            "EVIDENCE_QUALITY_FRAGILITY_CSV",
            source_root / "FragilityAtlas" / "data" / "output" / "fragility_atlas_results.csv",
        ),
        "bias_csv": _env_or_default(
            bias_csv,
            "EVIDENCE_QUALITY_BIAS_CSV",
            source_root / "BiasForensics" / "data" / "output" / "bias_forensics_results.csv",
        ),
        "prediction_csv": _env_or_default(
            prediction_csv,
            "EVIDENCE_QUALITY_PREDICTION_CSV",
            source_root / "PredictionGap" / "data" / "output" / "prediction_gap_results.csv",
        ),
        "orb_csv": _env_or_default(
            orb_csv,
            "EVIDENCE_QUALITY_ORB_CSV",
            source_root / "OutcomeReportingBias" / "data" / "output" / "orb_results.csv",
        ),
        "out_path": _env_or_default(
            out_path,
            "EVIDENCE_QUALITY_REVIEWS_JSON",
            DEFAULT_OUT_PATH,
        ),
    }


def derive_output_paths(out_path):
    """Derive all repo-local build_unified output paths from reviews.json."""
    out_path = Path(out_path)
    data_dir = out_path.parent
    return {
        "reviews_json": out_path,
        "reviews_compact_json": data_dir / "reviews_compact.json",
        "unified_quality_csv": data_dir / "unified_quality.csv",
        "unified_summary_json": data_dir / "unified_summary.json",
    }


def build_reviews(fragility_csv, bias_csv, prediction_csv, orb_csv):
    """Build the unified nested review dataset."""
    print("Loading source datasets...")
    fragility = load_csv(fragility_csv, required=True)
    bias = load_csv(bias_csv, required=True)
    prediction = load_csv(prediction_csv, required=True)
    orb = load_csv(orb_csv, required=True)

    print(f"  FragilityAtlas: {len(fragility)} reviews")
    print(f"  BiasForensics:  {len(bias)} reviews")
    print(f"  PredictionGap:  {len(prediction)} reviews")
    print(f"  ORB:            {len(orb)} reviews")

    reviews = []
    for rid in sorted(fragility.keys()):
        fa = fragility[rid]
        bf = bias.get(rid)
        pg = prediction.get(rid)
        ob = orb.get(rid)

        completeness = 1
        if bf is not None:
            completeness += 1
        if pg is not None:
            completeness += 1
        if ob is not None:
            completeness += 1

        frag_score = safe_float(fa.get("robustness_score"))

        bias_score = None
        if bf is not None:
            bias_score = BIAS_MAP.get(bf.get("bias_class", ""))

        pred_score = None
        if pg is not None:
            pred_score = PRED_MAP.get(pg.get("discordance", ""))

        orb_score_val = None
        if ob is not None:
            orb_raw = safe_float(ob.get("orb_score"))
            if orb_raw is not None:
                orb_score_val = round(100 - orb_raw, 1)

        quality_score, quality_grade = compute_score(
            frag_score,
            bias_score,
            pred_score,
            orb_score_val,
        )

        record = {
            "review_id": rid,
            "analysis_name": fa.get("analysis_name", ""),
            "k": safe_int(fa.get("k")),
            "review_doi": fa.get("review_doi", ""),
            "completeness": completeness,
            "quality_score": quality_score,
            "quality_grade": quality_grade,
            "fragility": {
                "robustness_score": frag_score,
                "classification": fa.get("classification", ""),
                "top_dimension": fa.get("top_dimension", ""),
                "frac_significant": safe_float(fa.get("frac_significant")),
                "frac_reversed": safe_float(fa.get("frac_reversed")),
            },
            "bias": {
                "bias_class": bf.get("bias_class", ""),
                "n_detect": safe_int(bf.get("n_detect")),
                "egger_p": safe_float(bf.get("egger_p")),
                "egger_sig": safe_int(bf.get("egger_sig")),
                "tf_k0": safe_int(bf.get("tf_k0")),
                "petpeese_theta": safe_float(bf.get("petpeese_theta")),
                "petpeese_method": bf.get("petpeese_method", ""),
            } if bf is not None else None,
            "prediction": {
                "discordance": pg.get("discordance", ""),
                "pi_ci_ratio": safe_float(pg.get("pi_ci_ratio")),
                "tau2": safe_float(pg.get("tau2")),
                "I2": safe_float(pg.get("I2")),
                "ci_lo": safe_float(pg.get("ci_lo")),
                "ci_hi": safe_float(pg.get("ci_hi")),
                "pi_lo": safe_float(pg.get("pi_lo")),
                "pi_hi": safe_float(pg.get("pi_hi")),
            } if pg is not None else None,
            "orb": {
                "orb_class": ob.get("orb_class", ""),
                "orb_score": safe_float(ob.get("orb_score")),
                "excess_significance": safe_float(ob.get("excess_significance")),
                "outlier_ratio": safe_float(ob.get("outlier_ratio")),
            } if ob is not None else None,
        }
        reviews.append(record)

    return reviews


def _flat_quality_rows(reviews):
    """Flatten nested review records into the legacy CSV export shape."""
    rows = []
    for review in reviews:
        bias = review.get("bias") or {}
        prediction = review.get("prediction") or {}
        orb = review.get("orb") or {}
        fragility = review.get("fragility") or {}
        rows.append({
            "review_id": review.get("review_id", ""),
            "analysis_name": review.get("analysis_name", ""),
            "k": review.get("k", ""),
            "robustness_score": fragility.get("robustness_score", ""),
            "fragility_class": fragility.get("classification", ""),
            "bias_class": bias.get("bias_class", ""),
            "egger_sig": bias.get("egger_sig", ""),
            "n_detect": bias.get("n_detect", ""),
            "pi_ci_ratio": prediction.get("pi_ci_ratio", ""),
            "discordance": prediction.get("discordance", ""),
            "orb_class": orb.get("orb_class", ""),
            "orb_score_raw": orb.get("orb_score", ""),
            "excess_sig": orb.get("excess_significance", ""),
            "quality_score": review.get("quality_score", ""),
            "quality_grade": review.get("quality_grade", ""),
        })
    return rows


def _summary_payload(reviews):
    """Build the legacy summary JSON payload from nested review records."""
    scored = [r["quality_score"] for r in reviews if r.get("quality_score") is not None]
    sorted_scores = sorted(scored)
    median = sorted_scores[len(sorted_scores) // 2] if sorted_scores else None
    grades = {
        grade: sum(1 for r in reviews if r.get("quality_grade") == grade)
        for grade in ["A", "B", "C", "D"]
    }
    return {
        "n_reviews": len(reviews),
        "grades": grades,
        "mean_score": round(sum(scored) / len(scored), 1) if scored else None,
        "median_score": median,
        "components": {
            "fragility_fragile_or_unstable": sum(
                1
                for r in reviews
                if (r.get("fragility") or {}).get("classification") in ("Fragile", "Unstable")
            ),
            "bias_confirmed_or_discordant": sum(
                1
                for r in reviews
                if (r.get("bias") or {}).get("bias_class") in ("Confirmed", "Discordant")
            ),
            "prediction_false_reassurance": sum(
                1
                for r in reviews
                if (r.get("prediction") or {}).get("discordance") == "FALSE_REASSURANCE"
            ),
            "orb_high_risk": sum(
                1
                for r in reviews
                if (r.get("orb") or {}).get("orb_class") == "High_Risk"
            ),
        },
    }


def write_outputs(reviews, out_path):
    """Write nested and sidecar outputs for the unified dataset."""
    paths = derive_output_paths(out_path)
    paths["reviews_json"].parent.mkdir(parents=True, exist_ok=True)

    with open(paths["reviews_json"], "w", encoding="utf-8") as f:
        json.dump(reviews, f, indent=None)

    with open(paths["reviews_compact_json"], "w", encoding="utf-8") as f:
        json.dump(reviews, f, separators=(",", ":"))

    flat_rows = _flat_quality_rows(reviews)
    with open(paths["unified_quality_csv"], "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "review_id",
                "analysis_name",
                "k",
                "robustness_score",
                "fragility_class",
                "bias_class",
                "egger_sig",
                "n_detect",
                "pi_ci_ratio",
                "discordance",
                "orb_class",
                "orb_score_raw",
                "excess_sig",
                "quality_score",
                "quality_grade",
            ],
        )
        writer.writeheader()
        for row in flat_rows:
            writer.writerow(row)

    with open(paths["unified_summary_json"], "w", encoding="utf-8") as f:
        json.dump(_summary_payload(reviews), f, indent=2)

    return paths


def print_summary(reviews, out_path):
    """Print headline metrics for the generated unified dataset."""
    n = len(reviews)
    grades = {
        g: sum(1 for r in reviews if r["quality_grade"] == g)
        for g in ["A", "B", "C", "D", "Insufficient"]
    }
    scored = [r["quality_score"] for r in reviews if r["quality_score"] is not None]
    comp4 = sum(1 for r in reviews if r["completeness"] == 4)
    comp3 = sum(1 for r in reviews if r["completeness"] == 3)

    print(f"\n{'=' * 50}")
    print("UNIFIED EVIDENCE QUALITY REPORT")
    print(f"{'=' * 50}")
    print(f"  {n} Cochrane reviews scored")
    print(f"  Completeness: {comp4} with 4/4, {comp3} with 3/4")
    if scored:
        print(f"  Mean quality: {sum(scored) / len(scored):.1f}/100")
        print(f"  Median quality: {sorted(scored)[len(scored) // 2]:.1f}/100")
    print()
    for grade in ["A", "B", "C", "D"]:
        count = grades.get(grade, 0)
        pct = (count / n * 100) if n else 0.0
        print(f"  Grade {grade}: {count:4d} ({pct:5.1f}%)")
    print(f"\n  Output: {out_path}")
    print(f"  JSON size: {out_path.stat().st_size / 1024:.0f} KB")


def build_unified_dataset(
    source_root=None,
    fragility_csv=None,
    bias_csv=None,
    prediction_csv=None,
    orb_csv=None,
    out_path=None,
):
    """Build and write the unified dataset."""
    paths = resolve_paths(
        source_root=source_root,
        fragility_csv=fragility_csv,
        bias_csv=bias_csv,
        prediction_csv=prediction_csv,
        orb_csv=orb_csv,
        out_path=out_path,
    )
    reviews = build_reviews(
        paths["fragility_csv"],
        paths["bias_csv"],
        paths["prediction_csv"],
        paths["orb_csv"],
    )
    output_paths = write_outputs(reviews, paths["out_path"])
    print_summary(reviews, output_paths["reviews_json"])
    print(f"  Compact JSON: {output_paths['reviews_compact_json']}")
    print(f"  Flat CSV:     {output_paths['unified_quality_csv']}")
    print(f"  Summary JSON: {output_paths['unified_summary_json']}")
    return reviews, output_paths["reviews_json"]


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Build unified EvidenceQuality dataset from sibling project outputs."
    )
    parser.add_argument(
        "--source-root",
        help="Directory containing sibling project folders (default: parent of this repo).",
    )
    parser.add_argument("--fragility-csv", help="Override FragilityAtlas CSV path.")
    parser.add_argument("--bias-csv", help="Override BiasForensics CSV path.")
    parser.add_argument("--prediction-csv", help="Override PredictionGap CSV path.")
    parser.add_argument("--orb-csv", help="Override OutcomeReportingBias CSV path.")
    parser.add_argument(
        "--out",
        dest="out_path",
        help="Override output JSON path (default: repo-relative data/reviews.json).",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    build_unified_dataset(
        source_root=args.source_root,
        fragility_csv=args.fragility_csv,
        bias_csv=args.bias_csv,
        prediction_csv=args.prediction_csv,
        orb_csv=args.orb_csv,
        out_path=args.out_path,
    )


if __name__ == "__main__":
    main()
