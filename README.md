# EvidenceQuality

EvidenceQuality builds a multi-dimensional evidence-quality dataset and concordance analysis from sibling project outputs on `C:\`.

## Expected sibling projects

By default the scripts look for these folders next to `C:\EvidenceQuality`:

- `C:\FragilityAtlas`
- `C:\BiasForensics`
- `C:\PredictionGap`
- `C:\OutcomeReportingBias`
- `C:\MetaReproducer`
- `C:\OverlapDetector`

The older fallback path `C:\Models\MetaReproducer` is still supported for concordance builds.

## Quick start

From `C:\EvidenceQuality`:

```bash
python run_all.py
python build_unified.py
python build_concordance.py
python build_dashboard.py
pytest -q -p no:cacheprovider tests/test_concordance.py
```

Outputs are written repo-locally by default:

- `data/reviews.json`
- `data/reviews_compact.json`
- `data/unified_quality.csv`
- `data/unified_summary.json`
- `data/unified_concordance.csv`
- `data/concordance_summary.json`
- `data/concordance_matrix.json`
- `dashboard.html`
- `dashboard/index.html`

`run_all.py` is the preferred entry point when you want the full pipeline in one command.

## Overrides

All scripts support repo-independent overrides either by CLI flag or environment variable.

Common env vars:

- `EVIDENCE_QUALITY_SOURCE_ROOT`
- `EVIDENCE_QUALITY_FRAGILITY_CSV`
- `EVIDENCE_QUALITY_BIAS_CSV`
- `EVIDENCE_QUALITY_PREDICTION_CSV`
- `EVIDENCE_QUALITY_ORB_CSV`
- `EVIDENCE_QUALITY_REPRODUCER_JSON`
- `EVIDENCE_QUALITY_OVERLAP_PAIRS_CSV`
- `EVIDENCE_QUALITY_OVERLAP_STUDIES_CSV`
- `EVIDENCE_QUALITY_OUTPUT_DIR`
- `EVIDENCE_QUALITY_REVIEWS_JSON`
- `EVIDENCE_QUALITY_DASHBOARD_HTML`
- `EVIDENCE_QUALITY_DASHBOARD_INDEX_HTML`

CLI help:

```bash
python run_all.py --help
python build_unified.py --help
python build_concordance.py --help
python build_dashboard.py --help
```
