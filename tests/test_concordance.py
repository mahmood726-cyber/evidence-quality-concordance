"""Tests for Cochrane Quality Concordance pipeline."""
import sys, json, csv, math, pytest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestDataIntegrity:
    """Verify pipeline output is consistent."""

    @pytest.fixture
    def data(self):
        path = Path('C:/EvidenceQuality/data/unified_concordance.csv')
        if not path.exists():
            pytest.skip('Run build_concordance.py first')
        rows = []
        with open(path, encoding='utf-8') as f:
            for row in csv.DictReader(f):
                for k in ['composite_score', 'd1_fragility_norm', 'd2_bias_norm',
                           'd3_prediction_norm', 'd4_orb_norm', 'd5_repro_norm', 'd6_overlap_norm']:
                    row[k] = float(row[k])
                row['k'] = int(row['k'])
                rows.append(row)
        return rows

    @pytest.fixture
    def summary(self):
        path = Path('C:/EvidenceQuality/data/concordance_summary.json')
        if not path.exists():
            pytest.skip('Run build_concordance.py first')
        with open(path) as f:
            return json.load(f)

    def test_review_count(self, data):
        assert len(data) == 403

    def test_all_have_grade(self, data):
        for r in data:
            assert r['grade'] in ('A', 'B', 'C', 'D')

    def test_composite_in_range(self, data):
        for r in data:
            assert 0 <= r['composite_score'] <= 100, f"{r['review_id']}: {r['composite_score']}"

    def test_dimensions_in_range(self, data):
        dims = ['d1_fragility_norm', 'd2_bias_norm', 'd3_prediction_norm',
                'd4_orb_norm', 'd5_repro_norm', 'd6_overlap_norm']
        for r in data:
            for d in dims:
                assert 0 <= r[d] <= 100, f"{r['review_id']}.{d}: {r[d]}"

    def test_grade_thresholds(self, data):
        for r in data:
            cs = r['composite_score']
            if r['grade'] == 'A':
                assert cs >= 80
            elif r['grade'] == 'B':
                assert 60 <= cs < 80
            elif r['grade'] == 'C':
                assert 40 <= cs < 60
            else:
                assert cs < 40

    def test_unique_review_ids(self, data):
        ids = [r['review_id'] for r in data]
        assert len(ids) == len(set(ids))

    def test_k_positive(self, data):
        for r in data:
            assert r['k'] >= 3, f"{r['review_id']}: k={r['k']}"

    def test_summary_matches(self, data, summary):
        assert summary['n_reviews'] == len(data)
        grades = {}
        for r in data:
            grades[r['grade']] = grades.get(r['grade'], 0) + 1
        for g in 'ABCD':
            assert summary['grades'].get(g, 0) == grades.get(g, 0)


class TestCorrelationMatrix:
    @pytest.fixture
    def matrix(self):
        path = Path('C:/EvidenceQuality/data/concordance_matrix.json')
        if not path.exists():
            pytest.skip('Run build_concordance.py first')
        with open(path) as f:
            return json.load(f)

    def test_diagonal_is_one(self, matrix):
        for i in range(6):
            assert abs(matrix['rho'][i][i] - 1.0) < 1e-6

    def test_symmetric(self, matrix):
        for i in range(6):
            for j in range(6):
                assert abs(matrix['rho'][i][j] - matrix['rho'][j][i]) < 1e-6

    def test_rho_in_range(self, matrix):
        for i in range(6):
            for j in range(6):
                assert -1 <= matrix['rho'][i][j] <= 1

    def test_6_labels(self, matrix):
        assert len(matrix['labels']) == 6

    def test_strongest_is_bias_orb(self, matrix):
        """Pub Bias (idx 1) vs ORB (idx 3) should be the strongest off-diagonal."""
        max_rho = 0
        max_pair = None
        for i in range(6):
            for j in range(i + 1, 6):
                if abs(matrix['rho'][i][j]) > max_rho:
                    max_rho = abs(matrix['rho'][i][j])
                    max_pair = (i, j)
        assert max_pair == (1, 3), f"Expected (1,3), got {max_pair}"

    def test_mean_abs_rho_low(self, matrix):
        """Mean off-diagonal |rho| should be < 0.3 (orthogonal)."""
        off_diag = []
        for i in range(6):
            for j in range(i + 1, 6):
                off_diag.append(abs(matrix['rho'][i][j]))
        mean_rho = sum(off_diag) / len(off_diag)
        assert mean_rho < 0.3, f"Mean |rho| = {mean_rho:.3f}, not orthogonal"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
