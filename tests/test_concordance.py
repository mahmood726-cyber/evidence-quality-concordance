"""Tests for the EvidenceQuality build pipeline."""

import csv
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
sys.path.insert(0, str(PROJECT_ROOT))


def _write_csv(path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


class TestDataIntegrity:
    """Verify concordance outputs already on disk are internally consistent."""

    @pytest.fixture
    def data(self):
        path = DATA_DIR / "unified_concordance.csv"
        if not path.exists():
            pytest.skip("Run build_concordance.py first")
        rows = []
        with open(path, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                for key in [
                    "composite_score",
                    "d1_fragility_norm",
                    "d2_bias_norm",
                    "d3_prediction_norm",
                    "d4_orb_norm",
                    "d5_repro_norm",
                    "d6_overlap_norm",
                ]:
                    row[key] = float(row[key])
                row["k"] = int(row["k"])
                rows.append(row)
        return rows

    @pytest.fixture
    def summary(self):
        path = DATA_DIR / "concordance_summary.json"
        if not path.exists():
            pytest.skip("Run build_concordance.py first")
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def test_review_count(self, data):
        assert len(data) == 403

    def test_all_have_grade(self, data):
        for row in data:
            assert row["grade"] in ("A", "B", "C", "D")

    def test_composite_in_range(self, data):
        for row in data:
            assert 0 <= row["composite_score"] <= 100, f"{row['review_id']}: {row['composite_score']}"

    def test_dimensions_in_range(self, data):
        dims = [
            "d1_fragility_norm",
            "d2_bias_norm",
            "d3_prediction_norm",
            "d4_orb_norm",
            "d5_repro_norm",
            "d6_overlap_norm",
        ]
        for row in data:
            for dim in dims:
                assert 0 <= row[dim] <= 100, f"{row['review_id']}.{dim}: {row[dim]}"

    def test_grade_thresholds(self, data):
        for row in data:
            score = row["composite_score"]
            if row["grade"] == "A":
                assert score >= 80
            elif row["grade"] == "B":
                assert 60 <= score < 80
            elif row["grade"] == "C":
                assert 40 <= score < 60
            else:
                assert score < 40

    def test_unique_review_ids(self, data):
        ids = [row["review_id"] for row in data]
        assert len(ids) == len(set(ids))

    def test_k_positive(self, data):
        for row in data:
            assert row["k"] >= 3, f"{row['review_id']}: k={row['k']}"

    def test_summary_matches(self, data, summary):
        assert summary["n_reviews"] == len(data)
        grades = {}
        for row in data:
            grades[row["grade"]] = grades.get(row["grade"], 0) + 1
        for grade in "ABCD":
            assert summary["grades"].get(grade, 0) == grades.get(grade, 0)


class TestCorrelationMatrix:
    @pytest.fixture
    def matrix(self):
        path = DATA_DIR / "concordance_matrix.json"
        if not path.exists():
            pytest.skip("Run build_concordance.py first")
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def test_diagonal_is_one(self, matrix):
        for i in range(6):
            assert abs(matrix["rho"][i][i] - 1.0) < 1e-6

    def test_symmetric(self, matrix):
        for i in range(6):
            for j in range(6):
                assert abs(matrix["rho"][i][j] - matrix["rho"][j][i]) < 1e-6

    def test_rho_in_range(self, matrix):
        for i in range(6):
            for j in range(6):
                assert -1 <= matrix["rho"][i][j] <= 1

    def test_6_labels(self, matrix):
        assert len(matrix["labels"]) == 6

    def test_strongest_is_bias_orb(self, matrix):
        """Pub Bias (idx 1) vs ORB (idx 3) should be the strongest off-diagonal."""
        max_rho = 0
        max_pair = None
        for i in range(6):
            for j in range(i + 1, 6):
                if abs(matrix["rho"][i][j]) > max_rho:
                    max_rho = abs(matrix["rho"][i][j])
                    max_pair = (i, j)
        assert max_pair == (1, 3), f"Expected (1,3), got {max_pair}"

    def test_mean_abs_rho_low(self, matrix):
        """Mean off-diagonal |rho| should be < 0.3 (orthogonal)."""
        off_diag = []
        for i in range(6):
            for j in range(i + 1, 6):
                off_diag.append(abs(matrix["rho"][i][j]))
        mean_rho = sum(off_diag) / len(off_diag)
        assert mean_rho < 0.3, f"Mean |rho| = {mean_rho:.3f}, not orthogonal"


class TestBuildScripts:
    def test_build_unified_dataset_from_repo_relative_source_root(self, tmp_path):
        import build_unified

        source_root = tmp_path / "sources"
        _write_csv(
            source_root / "FragilityAtlas" / "data" / "output" / "fragility_atlas_results.csv",
            ["review_id", "analysis_name", "k", "review_doi", "robustness_score", "classification", "top_dimension", "frac_significant", "frac_reversed"],
            [
                {
                    "review_id": "CD000001",
                    "analysis_name": "Mortality",
                    "k": "5",
                    "review_doi": "10.1000/a",
                    "robustness_score": "82",
                    "classification": "Robust",
                    "top_dimension": "model",
                    "frac_significant": "0.9",
                    "frac_reversed": "0.1",
                },
                {
                    "review_id": "CD000002",
                    "analysis_name": "Readmission",
                    "k": "4",
                    "review_doi": "10.1000/b",
                    "robustness_score": "45",
                    "classification": "Fragile",
                    "top_dimension": "zero_cells",
                    "frac_significant": "0.5",
                    "frac_reversed": "0.4",
                },
            ],
        )
        _write_csv(
            source_root / "BiasForensics" / "data" / "output" / "bias_forensics_results.csv",
            ["review_id", "bias_class", "n_detect", "egger_p", "egger_sig", "tf_k0", "petpeese_theta", "petpeese_method"],
            [
                {
                    "review_id": "CD000001",
                    "bias_class": "Clean",
                    "n_detect": "0",
                    "egger_p": "0.6",
                    "egger_sig": "0",
                    "tf_k0": "0",
                    "petpeese_theta": "0.1",
                    "petpeese_method": "PET",
                }
            ],
        )
        _write_csv(
            source_root / "PredictionGap" / "data" / "output" / "prediction_gap_results.csv",
            ["review_id", "discordance", "pi_ci_ratio", "tau2", "I2", "ci_lo", "ci_hi", "pi_lo", "pi_hi"],
            [
                {
                    "review_id": "CD000001",
                    "discordance": "CONCORDANT_SIG",
                    "pi_ci_ratio": "1.1",
                    "tau2": "0.01",
                    "I2": "15",
                    "ci_lo": "0.1",
                    "ci_hi": "0.3",
                    "pi_lo": "0.05",
                    "pi_hi": "0.35",
                },
                {
                    "review_id": "CD000002",
                    "discordance": "FALSE_REASSURANCE",
                    "pi_ci_ratio": "3.0",
                    "tau2": "0.20",
                    "I2": "70",
                    "ci_lo": "0.2",
                    "ci_hi": "0.4",
                    "pi_lo": "-0.1",
                    "pi_hi": "0.8",
                },
            ],
        )
        _write_csv(
            source_root / "OutcomeReportingBias" / "data" / "output" / "orb_results.csv",
            ["review_id", "orb_class", "orb_score", "excess_significance", "outlier_ratio"],
            [
                {
                    "review_id": "CD000001",
                    "orb_class": "Low_Risk",
                    "orb_score": "10",
                    "excess_significance": "0.1",
                    "outlier_ratio": "0.05",
                },
                {
                    "review_id": "CD000002",
                    "orb_class": "High_Risk",
                    "orb_score": "80",
                    "excess_significance": "0.8",
                    "outlier_ratio": "0.4",
                },
            ],
        )

        out_path = tmp_path / "outputs" / "reviews.json"
        reviews, written = build_unified.build_unified_dataset(
            source_root=source_root,
            out_path=out_path,
        )

        assert written == out_path
        assert out_path.exists()
        sidecars = build_unified.derive_output_paths(out_path)
        assert sidecars["reviews_compact_json"].exists()
        assert sidecars["unified_quality_csv"].exists()
        assert sidecars["unified_summary_json"].exists()
        assert len(reviews) == 2

        written_reviews = json.loads(out_path.read_text(encoding="utf-8"))
        summary_payload = json.loads(sidecars["unified_summary_json"].read_text(encoding="utf-8"))
        first = next(r for r in written_reviews if r["review_id"] == "CD000001")
        second = next(r for r in written_reviews if r["review_id"] == "CD000002")

        assert first["completeness"] == 4
        assert first["quality_grade"] == "A"
        assert second["completeness"] == 3
        assert second["bias"] is None
        assert second["quality_grade"] in {"C", "D"}
        assert summary_payload["n_reviews"] == 2
        assert summary_payload["components"]["prediction_false_reassurance"] == 1

    def test_load_reproducer_prefers_primary_and_new_schema_fields(self, tmp_path):
        import build_concordance

        path = tmp_path / "summary.json"
        path.write_text(json.dumps([
            {
                "review_id": "CD100001",
                "outcome_label": "Secondary",
                "is_primary": False,
                "outcome_rank": 2,
                "study_level": {"total_studies": 4, "n_with_pdf": 1, "match_rate_strict": 0.25},
                "review_level": {"tier": "major_discrepancy"},
                "errors": {"primary_error_source": "no_match"},
            },
            {
                "review_id": "CD100001",
                "outcome_label": "Primary",
                "is_primary": True,
                "outcome_rank": 1,
                "study_level": {"total_studies": 5, "n_with_pdf": 4, "match_rate_strict": 0.8},
                "review_level": {"classification": "reproduced"},
                "errors": {"primary_error_source": "missing_pdf"},
            },
        ]), encoding="utf-8")

        loaded = build_concordance.load_reproducer(path)
        assert loaded["CD100001"]["repro_class"] == "reproduced"
        assert loaded["CD100001"]["repro_total_k"] == 5
        assert loaded["CD100001"]["repro_n_pdf"] == 4
        assert loaded["CD100001"]["repro_rate_strict"] == 0.8
        assert loaded["CD100001"]["repro_primary_error"] == "missing_pdf"

    def test_build_concordance_writes_repo_relative_outputs(self, tmp_path):
        import build_concordance

        source_root = tmp_path / "sources"
        _write_csv(
            source_root / "FragilityAtlas" / "data" / "output" / "fragility_atlas_results.csv",
            ["review_id", "k", "scale", "robustness_score", "classification", "frac_significant", "top_dimension"],
            [
                {"review_id": "CD200001", "k": "5", "scale": "RR", "robustness_score": "85", "classification": "Robust", "frac_significant": "0.9", "top_dimension": "model"},
                {"review_id": "CD200002", "k": "6", "scale": "OR", "robustness_score": "40", "classification": "Fragile", "frac_significant": "0.4", "top_dimension": "measure"},
            ],
        )
        _write_csv(
            source_root / "BiasForensics" / "data" / "output" / "bias_forensics_results.csv",
            ["review_id", "n_detect", "concordance", "bias_class", "egger_p", "tf_k0"],
            [
                {"review_id": "CD200001", "n_detect": "1", "concordance": "1", "bias_class": "Clean", "egger_p": "0.5", "tf_k0": "0"},
                {"review_id": "CD200002", "n_detect": "6", "concordance": "6", "bias_class": "Confirmed", "egger_p": "0.01", "tf_k0": "2"},
            ],
        )
        _write_csv(
            source_root / "PredictionGap" / "data" / "output" / "prediction_gap_results.csv",
            ["review_id", "pi_ci_ratio", "discordance", "I2", "tau2"],
            [
                {"review_id": "CD200001", "pi_ci_ratio": "1.2", "discordance": "CONCORDANT_SIG", "I2": "20", "tau2": "0.01"},
                {"review_id": "CD200002", "pi_ci_ratio": "2.5", "discordance": "FALSE_REASSURANCE", "I2": "65", "tau2": "0.12"},
            ],
        )
        _write_csv(
            source_root / "OutcomeReportingBias" / "data" / "output" / "orb_results.csv",
            ["review_id", "orb_score", "orb_class", "excess_significance"],
            [
                {"review_id": "CD200001", "orb_score": "15", "orb_class": "Low_Risk", "excess_significance": "0.1"},
                {"review_id": "CD200002", "orb_score": "75", "orb_class": "High_Risk", "excess_significance": "0.7"},
            ],
        )

        reproducer_path = source_root / "MetaReproducer" / "data" / "results" / "summary_primary.json"
        reproducer_path.parent.mkdir(parents=True, exist_ok=True)
        reproducer_path.write_text(json.dumps([
            {
                "review_id": "CD200001",
                "is_primary": True,
                "study_level": {"total_studies": 5, "n_with_pdf": 4, "match_rate_strict": 0.8},
                "review_level": {"classification": "reproduced"},
                "errors": {"primary_error_source": "missing_pdf"},
            },
            {
                "review_id": "CD200002",
                "is_primary": True,
                "study_level": {"total_studies": 6, "n_with_pdf": 2, "match_rate_strict": 0.33},
                "review_level": {"classification": "major_discrepancy"},
                "errors": {"primary_error_source": "no_match"},
            },
        ]), encoding="utf-8")

        _write_csv(
            source_root / "OverlapDetector" / "data" / "output" / "overlap_pairs.csv",
            ["review_1", "review_2", "n_shared", "jaccard"],
            [
                {"review_1": "CD200001", "review_2": "CD200002", "n_shared": "2", "jaccard": "0.15"},
            ],
        )
        _write_csv(
            source_root / "OverlapDetector" / "data" / "output" / "overlap_top_studies.csv",
            ["study_id", "count"],
            [
                {"study_id": "S1", "count": "2"},
            ],
        )

        out_dir = tmp_path / "outputs"
        rows, summary, matrix = build_concordance.build_concordance(
            source_root=source_root,
            out_dir=out_dir,
        )

        assert len(rows) == 2
        assert summary["n_reviews"] == 2
        assert summary["strongest_pair"]
        assert len(matrix["labels"]) == 6
        assert (out_dir / "unified_concordance.csv").exists()
        assert (out_dir / "concordance_summary.json").exists()
        assert (out_dir / "concordance_matrix.json").exists()

    def test_build_rows_caps_reproducibility_dimension_at_100(self):
        import build_concordance

        rows = build_concordance.build_rows(
            fragility={
                "CD500001": {
                    "k": "5",
                    "scale": "RR",
                    "robustness_score": "80",
                    "classification": "Robust",
                    "frac_significant": "0.8",
                    "top_dimension": "model",
                }
            },
            bias={
                "CD500001": {
                    "n_detect": "0",
                    "concordance": "0",
                    "bias_class": "Clean",
                    "egger_p": "0.8",
                    "tf_k0": "0",
                }
            },
            prediction={
                "CD500001": {
                    "pi_ci_ratio": "1.0",
                    "discordance": "CONCORDANT_SIG",
                    "I2": "10",
                    "tau2": "0.01",
                }
            },
            orb={
                "CD500001": {
                    "orb_score": "10",
                    "orb_class": "Low_Risk",
                    "excess_significance": "0.1",
                }
            },
            reproducer={
                "CD500001": {
                    "repro_class": "reproduced",
                    "repro_total_k": 7,
                    "repro_n_pdf": 8,
                    "repro_rate_strict": 0.75,
                }
            },
            overlap={
                "CD500001": {
                    "max_jaccard": 0.1,
                    "max_shared": 1,
                }
            },
        )

        assert len(rows) == 1
        assert rows[0]["repro_oa_coverage"] == 1.0
        assert rows[0]["d5_repro_norm"] == 100.0

    def test_build_dashboard_respects_env_overrides_and_dynamic_counts(self, tmp_path):
        reviews_json = tmp_path / "reviews.json"
        dashboard_html = tmp_path / "dashboard.html"
        dashboard_index_html = tmp_path / "dashboard" / "index.html"

        reviews_json.write_text(
            json.dumps(
                [
                    {
                        "review_id": "CD300001",
                        "analysis_name": "Mortality",
                        "k": 5,
                        "completeness": 4,
                        "quality_score": 82.0,
                        "quality_grade": "A",
                        "fragility": {"robustness_score": 90.0},
                        "bias": {"bias_class": "Clean"},
                        "prediction": {"discordance": "CONCORDANT_SIG"},
                        "orb": {"orb_score": 10.0},
                    },
                    {
                        "review_id": "CD300002",
                        "analysis_name": "Readmission",
                        "k": 4,
                        "completeness": 3,
                        "quality_score": 55.0,
                        "quality_grade": "C",
                        "fragility": {"robustness_score": 50.0},
                        "bias": None,
                        "prediction": {"discordance": "FALSE_REASSURANCE"},
                        "orb": {"orb_score": 70.0},
                    },
                ]
            ),
            encoding="utf-8",
        )

        env = os.environ.copy()
        env["EVIDENCE_QUALITY_REVIEWS_JSON"] = str(reviews_json)
        env["EVIDENCE_QUALITY_DASHBOARD_HTML"] = str(dashboard_html)
        env["EVIDENCE_QUALITY_DASHBOARD_INDEX_HTML"] = str(dashboard_index_html)

        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "build_dashboard.py")],
            cwd=PROJECT_ROOT,
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )

        assert dashboard_html.exists()
        assert dashboard_index_html.exists()
        html = dashboard_html.read_text(encoding="utf-8")
        index_html = dashboard_index_html.read_text(encoding="utf-8")
        assert "2 Cochrane reviews graded across 4 dimensions" in html
        assert f"Source: {reviews_json}" in html
        assert "CD300001" in html
        assert html == index_html
        assert "SUCCESS" in result.stdout

    def test_run_all_executes_full_pipeline_with_cli_overrides(self, tmp_path):
        source_root = tmp_path / "sources"
        _write_csv(
            source_root / "FragilityAtlas" / "data" / "output" / "fragility_atlas_results.csv",
            ["review_id", "analysis_name", "k", "review_doi", "scale", "robustness_score", "classification", "top_dimension", "frac_significant", "frac_reversed"],
            [
                {
                    "review_id": "CD400001",
                    "analysis_name": "Mortality",
                    "k": "5",
                    "review_doi": "10.1000/c",
                    "scale": "RR",
                    "robustness_score": "88",
                    "classification": "Robust",
                    "top_dimension": "model",
                    "frac_significant": "0.9",
                    "frac_reversed": "0.1",
                },
                {
                    "review_id": "CD400002",
                    "analysis_name": "Readmission",
                    "k": "4",
                    "review_doi": "10.1000/d",
                    "scale": "OR",
                    "robustness_score": "42",
                    "classification": "Fragile",
                    "top_dimension": "measure",
                    "frac_significant": "0.4",
                    "frac_reversed": "0.4",
                },
            ],
        )
        _write_csv(
            source_root / "BiasForensics" / "data" / "output" / "bias_forensics_results.csv",
            ["review_id", "bias_class", "n_detect", "concordance", "egger_p", "egger_sig", "tf_k0", "petpeese_theta", "petpeese_method"],
            [
                {
                    "review_id": "CD400001",
                    "bias_class": "Clean",
                    "n_detect": "1",
                    "concordance": "1",
                    "egger_p": "0.5",
                    "egger_sig": "0",
                    "tf_k0": "0",
                    "petpeese_theta": "0.1",
                    "petpeese_method": "PET",
                },
                {
                    "review_id": "CD400002",
                    "bias_class": "Confirmed",
                    "n_detect": "6",
                    "concordance": "6",
                    "egger_p": "0.01",
                    "egger_sig": "1",
                    "tf_k0": "2",
                    "petpeese_theta": "0.8",
                    "petpeese_method": "PEESE",
                },
            ],
        )
        _write_csv(
            source_root / "PredictionGap" / "data" / "output" / "prediction_gap_results.csv",
            ["review_id", "discordance", "pi_ci_ratio", "tau2", "I2", "ci_lo", "ci_hi", "pi_lo", "pi_hi"],
            [
                {
                    "review_id": "CD400001",
                    "discordance": "CONCORDANT_SIG",
                    "pi_ci_ratio": "1.1",
                    "tau2": "0.01",
                    "I2": "15",
                    "ci_lo": "0.1",
                    "ci_hi": "0.3",
                    "pi_lo": "0.05",
                    "pi_hi": "0.35",
                },
                {
                    "review_id": "CD400002",
                    "discordance": "FALSE_REASSURANCE",
                    "pi_ci_ratio": "2.8",
                    "tau2": "0.18",
                    "I2": "68",
                    "ci_lo": "0.2",
                    "ci_hi": "0.4",
                    "pi_lo": "-0.1",
                    "pi_hi": "0.8",
                },
            ],
        )
        _write_csv(
            source_root / "OutcomeReportingBias" / "data" / "output" / "orb_results.csv",
            ["review_id", "orb_class", "orb_score", "excess_significance", "outlier_ratio"],
            [
                {
                    "review_id": "CD400001",
                    "orb_class": "Low_Risk",
                    "orb_score": "10",
                    "excess_significance": "0.1",
                    "outlier_ratio": "0.05",
                },
                {
                    "review_id": "CD400002",
                    "orb_class": "High_Risk",
                    "orb_score": "75",
                    "excess_significance": "0.8",
                    "outlier_ratio": "0.4",
                },
            ],
        )

        reproducer_path = source_root / "MetaReproducer" / "data" / "results" / "summary_primary.json"
        reproducer_path.parent.mkdir(parents=True, exist_ok=True)
        reproducer_path.write_text(
            json.dumps(
                [
                    {
                        "review_id": "CD400001",
                        "is_primary": True,
                        "study_level": {"total_studies": 5, "n_with_pdf": 4, "match_rate_strict": 0.8},
                        "review_level": {"classification": "reproduced"},
                        "errors": {"primary_error_source": "missing_pdf"},
                    },
                    {
                        "review_id": "CD400002",
                        "is_primary": True,
                        "study_level": {"total_studies": 4, "n_with_pdf": 2, "match_rate_strict": 0.5},
                        "review_level": {"classification": "major_discrepancy"},
                        "errors": {"primary_error_source": "no_match"},
                    },
                ]
            ),
            encoding="utf-8",
        )

        _write_csv(
            source_root / "OverlapDetector" / "data" / "output" / "overlap_pairs.csv",
            ["review_1", "review_2", "n_shared", "jaccard"],
            [
                {"review_1": "CD400001", "review_2": "CD400002", "n_shared": "2", "jaccard": "0.15"},
            ],
        )
        _write_csv(
            source_root / "OverlapDetector" / "data" / "output" / "overlap_top_studies.csv",
            ["study_id", "count"],
            [
                {"study_id": "S1", "count": "2"},
            ],
        )

        output_dir = tmp_path / "outputs"
        reviews_json = output_dir / "reviews.json"
        dashboard_html = output_dir / "dashboard.html"
        dashboard_index_html = output_dir / "dashboard" / "index.html"

        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "run_all.py"),
                "--source-root",
                str(source_root),
                "--reviews-out",
                str(reviews_json),
                "--concordance-out-dir",
                str(output_dir),
                "--dashboard-out",
                str(dashboard_html),
            ],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        assert reviews_json.exists()
        assert (output_dir / "reviews_compact.json").exists()
        assert (output_dir / "unified_quality.csv").exists()
        assert (output_dir / "unified_summary.json").exists()
        assert (output_dir / "unified_concordance.csv").exists()
        assert (output_dir / "concordance_summary.json").exists()
        assert (output_dir / "concordance_matrix.json").exists()
        assert dashboard_html.exists()
        assert dashboard_index_html.exists()

        html = dashboard_html.read_text(encoding="utf-8")
        index_html = dashboard_index_html.read_text(encoding="utf-8")
        assert "2 Cochrane reviews graded across 4 dimensions" in html
        assert html == index_html
        assert "Pipeline complete. Artifacts:" in result.stdout


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
