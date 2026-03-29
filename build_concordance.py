"""The Cochrane Quality Concordance: merging 6 quality dimensions across 403 reviews.

Produces:
  - unified_concordance.csv: one row per review, all quality metrics
  - concordance_matrix.json: Spearman correlation matrix + p-values
  - concordance_summary.json: headline stats
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_SOURCE_ROOT = PROJECT_ROOT.parent
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data"


def load_csv(path, key="review_id", required=True):
    """Load CSV rows keyed by the provided id column."""
    p = Path(path)
    if not p.exists():
        if required:
            raise FileNotFoundError(f"Required source file not found: {p}")
        print(f"  WARNING: {p} not found, skipping")
        return {}

    data = {}
    with open(p, encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            data[row[key]] = row
    return data


def load_reproducer(path, required=True):
    """Load one reproducibility record per review from MetaReproducer JSON."""
    p = Path(path)
    if not p.exists():
        if required:
            raise FileNotFoundError(f"Required MetaReproducer summary not found: {p}")
        print(f"  WARNING: {p} not found, skipping reproducibility dimension")
        return {}

    with open(p, encoding="utf-8") as f:
        data = json.load(f)

    out = {}
    for record in data:
        rid = record.get("review_id") or record.get("cert", {}).get("review_id")
        if not rid:
            continue

        sl = record.get("study_level", {})
        rl = record.get("review_level", {})
        cert = record.get("cert", {})
        is_primary = record.get("is_primary") is True
        rank = record.get("outcome_rank")
        rank = rank if isinstance(rank, int) else 10**9

        normalized = {
            "repro_class": cert.get("classification") or rl.get("classification") or rl.get("tier", "unknown"),
            "repro_total_k": sl.get("total_studies", sl.get("total_k", 0)),
            "repro_n_pdf": sl.get("n_with_pdf", 0),
            "repro_rate_strict": sl.get("match_rate_strict", sl.get("rate_strict", 0)),
            "repro_rate_moderate": sl.get("match_rate_moderate", sl.get("rate_moderate", 0)),
            "repro_primary_error": record.get("errors", {}).get("primary_error_source", "unknown"),
            "_is_primary": is_primary,
            "_rank": rank,
        }

        existing = out.get(rid)
        if existing is None:
            out[rid] = normalized
            continue
        if normalized["_is_primary"] and not existing["_is_primary"]:
            out[rid] = normalized
            continue
        if normalized["_is_primary"] == existing["_is_primary"] and normalized["_rank"] < existing["_rank"]:
            out[rid] = normalized

    for rid, row in out.items():
        row.pop("_is_primary", None)
        row.pop("_rank", None)
    return out


def load_overlap(pairs_path, studies_path=None, required=True):
    """Per-review maximum overlap with any other review."""
    pairs = Path(pairs_path)
    if not pairs.exists():
        if required:
            raise FileNotFoundError(f"Required overlap pairs file not found: {pairs}")
        print(f"  WARNING: {pairs} not found, skipping overlap dimension")
        return {}

    if studies_path:
        studies = Path(studies_path)
        if not studies.exists():
            print(f"  WARNING: overlap studies file not found: {studies}")

    review_max_overlap = {}
    with open(pairs, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            r1, r2 = row["review_1"], row["review_2"]
            n = int(row["n_shared"])
            j = float(row["jaccard"])
            for rid in (r1, r2):
                if rid not in review_max_overlap or j > review_max_overlap[rid]["max_jaccard"]:
                    review_max_overlap[rid] = {
                        "max_jaccard": j,
                        "max_shared": n,
                        "overlap_partner": r2 if rid == r1 else r1,
                    }
    return review_max_overlap


def _env_or_default(value, env_name, default):
    if value:
        return Path(value)
    env_value = os.environ.get(env_name)
    if env_value:
        return Path(env_value)
    return Path(default)


def _first_existing(candidates):
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def resolve_paths(
    source_root=None,
    fragility_csv=None,
    bias_csv=None,
    prediction_csv=None,
    orb_csv=None,
    reproducer_json=None,
    overlap_pairs_csv=None,
    overlap_studies_csv=None,
    out_dir=None,
):
    """Resolve input/output paths from args, env vars, or project-relative defaults."""
    source_root = _env_or_default(
        source_root,
        "EVIDENCE_QUALITY_SOURCE_ROOT",
        DEFAULT_SOURCE_ROOT,
    )
    reproducer_default = _first_existing([
        source_root / "MetaReproducer" / "data" / "results" / "summary_primary.json",
        source_root / "MetaReproducer" / "data" / "results" / "summary.json",
        source_root / "Models" / "MetaReproducer" / "data" / "results" / "summary_primary.json",
        source_root / "Models" / "MetaReproducer" / "data" / "results" / "summary.json",
    ])

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
        "reproducer_json": _env_or_default(
            reproducer_json,
            "EVIDENCE_QUALITY_REPRODUCER_JSON",
            reproducer_default,
        ),
        "overlap_pairs_csv": _env_or_default(
            overlap_pairs_csv,
            "EVIDENCE_QUALITY_OVERLAP_PAIRS_CSV",
            source_root / "OverlapDetector" / "data" / "output" / "overlap_pairs.csv",
        ),
        "overlap_studies_csv": _env_or_default(
            overlap_studies_csv,
            "EVIDENCE_QUALITY_OVERLAP_STUDIES_CSV",
            source_root / "OverlapDetector" / "data" / "output" / "overlap_top_studies.csv",
        ),
        "out_dir": _env_or_default(
            out_dir,
            "EVIDENCE_QUALITY_OUTPUT_DIR",
            DEFAULT_OUTPUT_DIR,
        ),
    }


def build_rows(fragility, bias, prediction, orb, reproducer, overlap):
    """Build the unified concordance row set."""
    common = set(fragility.keys()) & set(prediction.keys()) & set(orb.keys())
    print(f"\n  Common reviews (Frag + Pred + ORB): {len(common)}")

    rows = []
    for rid in sorted(common):
        f = fragility[rid]
        p = prediction[rid]
        o = orb[rid]
        b = bias.get(rid, {})
        r = reproducer.get(rid, {})
        ov = overlap.get(rid, {})
        repro_total_k = max(1, int(r.get("repro_total_k", 1)))
        repro_n_pdf = max(0, int(r.get("repro_n_pdf", 0)))
        repro_oa_coverage = min(1.0, repro_n_pdf / repro_total_k)

        row = {
            "review_id": rid,
            "k": int(f.get("k", 0)),
            "scale": f.get("scale", ""),
            "fragility_score": float(f.get("robustness_score", 0)),
            "fragility_class": f.get("classification", ""),
            "fragility_frac_sig": float(f.get("frac_significant", 0)),
            "fragility_top_dim": f.get("top_dimension", ""),
            "bias_n_detect": int(float(b.get("n_detect", 0))),
            "bias_concordance": int(float(b.get("concordance", 0))),
            "bias_class": b.get("bias_class", "unknown"),
            "bias_egger_p": float(b.get("egger_p", 1)),
            "bias_tf_k0": int(float(b.get("tf_k0", 0))),
            "pred_pi_ci_ratio": float(p.get("pi_ci_ratio", 1)),
            "pred_discordance": p.get("discordance", ""),
            "pred_I2": float(p.get("I2", 0)),
            "pred_tau2": float(p.get("tau2", 0)),
            "orb_score": float(o.get("orb_score", 0)),
            "orb_class": o.get("orb_class", ""),
            "orb_excess_sig": float(o.get("excess_significance", 0)),
            "repro_class": r.get("repro_class", "unknown"),
            "repro_oa_coverage": repro_oa_coverage,
            "repro_rate_strict": float(r.get("repro_rate_strict", 0)),
            "overlap_max_jaccard": ov.get("max_jaccard", 0),
            "overlap_max_shared": ov.get("max_shared", 0),
        }

        d1 = row["fragility_score"]
        d2 = max(0, 100 - row["bias_n_detect"] * 12.5)
        d3 = max(0, 100 - (row["pred_pi_ci_ratio"] - 1) * 20)
        d4 = max(0, 100 - row["orb_score"])
        d5 = row["repro_oa_coverage"] * 100
        d6 = max(0, 100 - row["overlap_max_jaccard"] * 200)

        row["composite_score"] = round((d1 + d2 + d3 + d4 + d5 + d6) / 6, 1)
        row["d1_fragility_norm"] = round(d1, 1)
        row["d2_bias_norm"] = round(d2, 1)
        row["d3_prediction_norm"] = round(d3, 1)
        row["d4_orb_norm"] = round(d4, 1)
        row["d5_repro_norm"] = round(d5, 1)
        row["d6_overlap_norm"] = round(d6, 1)

        cs = row["composite_score"]
        row["grade"] = "A" if cs >= 80 else "B" if cs >= 60 else "C" if cs >= 40 else "D"
        rows.append(row)

    print(f"\n  Unified rows: {len(rows)}")
    return rows


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


def spearman(x, y):
    """Spearman rank correlation with approximate p-value."""
    n = len(x)
    if n < 3:
        return 0, 1
    rx = rank_data(x)
    ry = rank_data(y)
    d2 = sum((a - b) ** 2 for a, b in zip(rx, ry))
    rho = 1 - 6 * d2 / (n * (n * n - 1))
    if abs(rho) >= 1:
        return rho, 0
    t = rho * math.sqrt((n - 2) / (1 - rho * rho))
    p = 2 * (1 - normal_cdf(abs(t) / math.sqrt(1 + t * t / n)))
    return rho, p


def calculate_correlation_payload(rows):
    """Compute correlation outputs and headline summary values."""
    dims = [
        "d1_fragility_norm",
        "d2_bias_norm",
        "d3_prediction_norm",
        "d4_orb_norm",
        "d5_repro_norm",
        "d6_overlap_norm",
    ]
    dim_labels = [
        "Fragility",
        "Pub Bias",
        "Prediction Gap",
        "ORB",
        "Reproducibility",
        "Overlap",
    ]

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

    off_diag = {}
    for i, li in enumerate(dim_labels):
        for j, lj in enumerate(dim_labels):
            if i < j:
                key = f"{li} vs {lj}"
                off_diag[key] = corr_matrix[key]

    strongest = max(off_diag, key=lambda k: abs(off_diag[k]))
    weakest = min(off_diag, key=lambda k: abs(off_diag[k]))
    mean_abs_rho = sum(abs(v) for v in off_diag.values()) / len(off_diag)

    matrix_json = {
        "labels": dim_labels,
        "rho": [[corr_matrix[f"{li} vs {lj}"] for lj in dim_labels] for li in dim_labels],
        "p": [[p_matrix[f"{li} vs {lj}"] for lj in dim_labels] for li in dim_labels],
    }

    return {
        "dims": dims,
        "dim_labels": dim_labels,
        "corr_matrix": corr_matrix,
        "p_matrix": p_matrix,
        "off_diag": off_diag,
        "strongest": strongest,
        "weakest": weakest,
        "mean_abs_rho": round(mean_abs_rho, 3),
        "matrix_json": matrix_json,
    }


def build_summary(rows, correlation_payload):
    """Build headline summary JSON."""
    grades = Counter(r["grade"] for r in rows)
    scores = [r["composite_score"] for r in rows]
    mean_score = sum(scores) / len(scores)
    median_score = sorted(scores)[len(scores) // 2]

    fragile_and_biased = sum(
        1
        for r in rows
        if r["fragility_class"] in ("Fragile", "Unstable")
        and r["bias_class"] in ("Confirmed", "Discordant")
    )
    fragile_total = sum(1 for r in rows if r["fragility_class"] in ("Fragile", "Unstable"))
    biased_total = sum(1 for r in rows if r["bias_class"] in ("Confirmed", "Discordant"))
    false_reassurance_and_orb = sum(
        1
        for r in rows
        if r["pred_discordance"] == "FALSE_REASSURANCE" and r["orb_class"] == "High_Risk"
    )

    dim_labels = correlation_payload["dim_labels"]
    corr_matrix = correlation_payload["corr_matrix"]
    p_matrix = correlation_payload["p_matrix"]

    return {
        "n_reviews": len(rows),
        "grades": dict(grades),
        "mean_composite": round(mean_score, 1),
        "median_composite": round(median_score, 1),
        "dimension_means": {
            label: round(sum(r[dim] for r in rows) / len(rows), 1)
            for dim, label in zip(correlation_payload["dims"], dim_labels)
        },
        "cross_dimension": {
            "fragile_and_biased": fragile_and_biased,
            "false_reassurance_and_high_orb": false_reassurance_and_orb,
            "fragile_total": fragile_total,
            "biased_total": biased_total,
        },
        "correlation_matrix": {
            key: value
            for key, value in corr_matrix.items()
            if dim_labels.index(key.split(" vs ")[0]) < dim_labels.index(key.split(" vs ")[1])
        },
        "p_values": {
            key: value
            for key, value in p_matrix.items()
            if dim_labels.index(key.split(" vs ")[0]) < dim_labels.index(key.split(" vs ")[1])
        },
        "mean_abs_rho": correlation_payload["mean_abs_rho"],
        "strongest_pair": correlation_payload["strongest"],
        "weakest_pair": correlation_payload["weakest"],
    }


def print_report(rows, summary, correlation_payload):
    """Print matrix and headline findings."""
    dim_labels = correlation_payload["dim_labels"]
    corr_matrix = correlation_payload["corr_matrix"]
    p_matrix = correlation_payload["p_matrix"]

    print("\n" + "=" * 60)
    print("SPEARMAN CORRELATION MATRIX")
    print("=" * 60)
    print(f"{'':>18s}", end="")
    for label in dim_labels:
        print(f"{label:>14s}", end="")
    print()

    for li in dim_labels:
        print(f"{li:>18s}", end="")
        for lj in dim_labels:
            key = f"{li} vs {lj}"
            rho = corr_matrix[key]
            star = "*" if p_matrix[key] < 0.05 else " "
            print(f"  {rho:>6.3f}{star:>1s}    ", end="")
        print()

    cross = summary["cross_dimension"]
    grades = summary["grades"]
    print("\n" + "=" * 60)
    print("HEADLINE FINDINGS")
    print("=" * 60)
    print(f"  Reviews analyzed: {summary['n_reviews']}")
    print(
        f"  Composite score: mean={summary['mean_composite']:.1f}, "
        f"median={summary['median_composite']:.1f}"
    )
    print(
        f"  Grades: A={grades.get('A', 0)}, B={grades.get('B', 0)}, "
        f"C={grades.get('C', 0)}, D={grades.get('D', 0)}"
    )
    print(
        f"  Fragile+Biased: {cross['fragile_and_biased']}/{summary['n_reviews']} "
        f"({100 * cross['fragile_and_biased'] / summary['n_reviews']:.1f}%)"
    )
    print(
        f"  False reassurance+High ORB: "
        f"{cross['false_reassurance_and_high_orb']}/{summary['n_reviews']} "
        f"({100 * cross['false_reassurance_and_high_orb'] / summary['n_reviews']:.1f}%)"
    )
    print(
        f"  Fragile total: {cross['fragile_total']} | "
        f"Biased total: {cross['biased_total']}"
    )
    print(f"\n  Strongest correlation: {correlation_payload['strongest']}"
          f" (rho={correlation_payload['off_diag'][correlation_payload['strongest']]:.3f})")
    print(f"  Weakest correlation:  {correlation_payload['weakest']}"
          f" (rho={correlation_payload['off_diag'][correlation_payload['weakest']]:.3f})")
    print(f"  Mean |rho| off-diagonal: {correlation_payload['mean_abs_rho']:.3f}")
    if correlation_payload["mean_abs_rho"] < 0.3:
        print("  >> QUALITY DIMENSIONS ARE LARGELY ORTHOGONAL")
    else:
        print("  >> QUALITY DIMENSIONS SHOW MODERATE CORRELATION")


def write_outputs(rows, summary, matrix_json, output_dir):
    """Persist concordance outputs to the repo-relative data directory."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    fields = list(rows[0].keys())
    with open(output_dir / "unified_concordance.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    with open(output_dir / "concordance_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    with open(output_dir / "concordance_matrix.json", "w", encoding="utf-8") as f:
        json.dump(matrix_json, f, indent=2)

    print(f"\n  Saved to {output_dir}/")
    print("  - unified_concordance.csv")
    print("  - concordance_summary.json")
    print("  - concordance_matrix.json")


def build_concordance(
    source_root=None,
    fragility_csv=None,
    bias_csv=None,
    prediction_csv=None,
    orb_csv=None,
    reproducer_json=None,
    overlap_pairs_csv=None,
    overlap_studies_csv=None,
    out_dir=None,
):
    """Build and write concordance artifacts."""
    print("The Cochrane Quality Concordance")
    print("=" * 40)

    paths = resolve_paths(
        source_root=source_root,
        fragility_csv=fragility_csv,
        bias_csv=bias_csv,
        prediction_csv=prediction_csv,
        orb_csv=orb_csv,
        reproducer_json=reproducer_json,
        overlap_pairs_csv=overlap_pairs_csv,
        overlap_studies_csv=overlap_studies_csv,
        out_dir=out_dir,
    )

    fragility = load_csv(paths["fragility_csv"], required=True)
    bias = load_csv(paths["bias_csv"], required=True)
    prediction = load_csv(paths["prediction_csv"], required=True)
    orb = load_csv(paths["orb_csv"], required=True)
    reproducer = load_reproducer(paths["reproducer_json"], required=True)
    overlap = load_overlap(
        paths["overlap_pairs_csv"],
        studies_path=paths["overlap_studies_csv"],
        required=True,
    )

    print(f"  Fragility Atlas: {len(fragility)} reviews")
    print(f"  Bias Forensics:  {len(bias)} reviews")
    print(f"  Prediction Gap:  {len(prediction)} reviews")
    print(f"  ORB Detector:    {len(orb)} reviews")
    print(f"  MetaReproducer:  {len(reproducer)} reviews")
    print(f"  Overlap (pairs): {len(overlap)} reviews with any overlap")

    rows = build_rows(fragility, bias, prediction, orb, reproducer, overlap)
    if not rows:
        raise ValueError("No concordance rows could be built from the resolved inputs.")

    correlation_payload = calculate_correlation_payload(rows)
    summary = build_summary(rows, correlation_payload)
    print_report(rows, summary, correlation_payload)
    write_outputs(rows, summary, correlation_payload["matrix_json"], paths["out_dir"])
    return rows, summary, correlation_payload["matrix_json"]


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Build EvidenceQuality concordance artifacts from sibling project outputs."
    )
    parser.add_argument(
        "--source-root",
        help="Directory containing sibling project folders (default: parent of this repo).",
    )
    parser.add_argument("--fragility-csv", help="Override FragilityAtlas CSV path.")
    parser.add_argument("--bias-csv", help="Override BiasForensics CSV path.")
    parser.add_argument("--prediction-csv", help="Override PredictionGap CSV path.")
    parser.add_argument("--orb-csv", help="Override OutcomeReportingBias CSV path.")
    parser.add_argument("--reproducer-json", help="Override MetaReproducer summary JSON path.")
    parser.add_argument("--overlap-pairs-csv", help="Override overlap pairs CSV path.")
    parser.add_argument("--overlap-studies-csv", help="Override overlap studies CSV path.")
    parser.add_argument(
        "--out-dir",
        help="Override output directory (default: repo-relative data/).",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    build_concordance(
        source_root=args.source_root,
        fragility_csv=args.fragility_csv,
        bias_csv=args.bias_csv,
        prediction_csv=args.prediction_csv,
        orb_csv=args.orb_csv,
        reproducer_json=args.reproducer_json,
        overlap_pairs_csv=args.overlap_pairs_csv,
        overlap_studies_csv=args.overlap_studies_csv,
        out_dir=args.out_dir,
    )


if __name__ == "__main__":
    main()
