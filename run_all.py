"""Run the full EvidenceQuality build pipeline in the correct order."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

import build_concordance
import build_unified

PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_REVIEWS_OUT = PROJECT_ROOT / "data" / "reviews.json"
DEFAULT_CONCORDANCE_OUT_DIR = PROJECT_ROOT / "data"
DEFAULT_DASHBOARD_OUT = PROJECT_ROOT / "dashboard.html"
DEFAULT_DASHBOARD_INDEX_OUT = PROJECT_ROOT / "dashboard" / "index.html"


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Run the full EvidenceQuality pipeline: unified dataset, concordance, dashboard."
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
        "--reviews-out",
        default=str(DEFAULT_REVIEWS_OUT),
        help="Output path for unified reviews JSON.",
    )
    parser.add_argument(
        "--concordance-out-dir",
        default=str(DEFAULT_CONCORDANCE_OUT_DIR),
        help="Output directory for concordance artifacts.",
    )
    parser.add_argument(
        "--dashboard-out",
        default=str(DEFAULT_DASHBOARD_OUT),
        help="Output path for dashboard HTML.",
    )
    parser.add_argument(
        "--dashboard-index-out",
        help="Optional mirrored output path for dashboard/index.html.",
    )
    parser.add_argument(
        "--python",
        default=sys.executable,
        help="Python executable to use for the dashboard subprocess.",
    )
    return parser.parse_args(argv)


def resolve_dashboard_index_out(dashboard_html, dashboard_index_html=None):
    """Resolve the mirrored dashboard/index.html output path."""
    if dashboard_index_html:
        return Path(dashboard_index_html)
    dashboard_html = Path(dashboard_html)
    return dashboard_html.parent / "dashboard" / "index.html"


def verify_outputs(reviews_json, concordance_out_dir, dashboard_html, dashboard_index_html):
    """Ensure expected pipeline artifacts exist."""
    concordance_out_dir = Path(concordance_out_dir)
    unified_outputs = build_unified.derive_output_paths(reviews_json)
    expected = [
        unified_outputs["reviews_json"],
        unified_outputs["reviews_compact_json"],
        unified_outputs["unified_quality_csv"],
        unified_outputs["unified_summary_json"],
        concordance_out_dir / "unified_concordance.csv",
        concordance_out_dir / "concordance_summary.json",
        concordance_out_dir / "concordance_matrix.json",
        Path(dashboard_html),
        Path(dashboard_index_html),
    ]
    missing = [str(path) for path in expected if not Path(path).exists()]
    if missing:
        raise FileNotFoundError(
            "Pipeline completed with missing expected artifacts:\n- " + "\n- ".join(missing)
        )
    return expected


def run_dashboard(python_executable, reviews_json, dashboard_html):
    """Build dashboard HTML via subprocess to avoid import-time script execution."""
    sys.stdout.flush()
    cmd = [
        python_executable,
        str(PROJECT_ROOT / "build_dashboard.py"),
        "--reviews-json",
        str(reviews_json),
        "--out",
        str(dashboard_html),
    ]
    subprocess.run(cmd, cwd=PROJECT_ROOT, check=True)


def mirror_dashboard(dashboard_html, dashboard_index_html):
    """Copy the canonical dashboard HTML to dashboard/index.html."""
    dashboard_html = Path(dashboard_html)
    dashboard_index_html = Path(dashboard_index_html)
    dashboard_index_html.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(dashboard_html, dashboard_index_html)


def run_pipeline(
    source_root=None,
    fragility_csv=None,
    bias_csv=None,
    prediction_csv=None,
    orb_csv=None,
    reproducer_json=None,
    overlap_pairs_csv=None,
    overlap_studies_csv=None,
    reviews_out=DEFAULT_REVIEWS_OUT,
    concordance_out_dir=DEFAULT_CONCORDANCE_OUT_DIR,
    dashboard_out=DEFAULT_DASHBOARD_OUT,
    dashboard_index_out=None,
    python_executable=sys.executable,
):
    """Run all EvidenceQuality build steps and verify expected artifacts."""
    print("Running EvidenceQuality full pipeline", flush=True)
    print("=" * 40, flush=True)

    reviews_json = Path(reviews_out)
    concordance_out_dir = Path(concordance_out_dir)
    dashboard_html = Path(dashboard_out)
    dashboard_index_html = resolve_dashboard_index_out(dashboard_html, dashboard_index_out)

    build_unified.build_unified_dataset(
        source_root=source_root,
        fragility_csv=fragility_csv,
        bias_csv=bias_csv,
        prediction_csv=prediction_csv,
        orb_csv=orb_csv,
        out_path=reviews_json,
    )

    build_concordance.build_concordance(
        source_root=source_root,
        fragility_csv=fragility_csv,
        bias_csv=bias_csv,
        prediction_csv=prediction_csv,
        orb_csv=orb_csv,
        reproducer_json=reproducer_json,
        overlap_pairs_csv=overlap_pairs_csv,
        overlap_studies_csv=overlap_studies_csv,
        out_dir=concordance_out_dir,
    )

    run_dashboard(
        python_executable=python_executable,
        reviews_json=reviews_json,
        dashboard_html=dashboard_html,
    )
    mirror_dashboard(dashboard_html, dashboard_index_html)

    outputs = verify_outputs(
        reviews_json=reviews_json,
        concordance_out_dir=concordance_out_dir,
        dashboard_html=dashboard_html,
        dashboard_index_html=dashboard_index_html,
    )

    print("\nPipeline complete. Artifacts:")
    for path in outputs:
        print(f"  - {path}")
    return outputs


def main(argv=None):
    args = parse_args(argv)
    run_pipeline(
        source_root=args.source_root,
        fragility_csv=args.fragility_csv,
        bias_csv=args.bias_csv,
        prediction_csv=args.prediction_csv,
        orb_csv=args.orb_csv,
        reproducer_json=args.reproducer_json,
        overlap_pairs_csv=args.overlap_pairs_csv,
        overlap_studies_csv=args.overlap_studies_csv,
        reviews_out=args.reviews_out,
        concordance_out_dir=args.concordance_out_dir,
        dashboard_out=args.dashboard_out,
        dashboard_index_out=args.dashboard_index_out,
        python_executable=args.python,
    )


if __name__ == "__main__":
    main()
