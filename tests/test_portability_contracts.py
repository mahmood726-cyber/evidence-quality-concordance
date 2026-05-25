import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "e156-submission" / "config.json"


class PortabilityContracts(unittest.TestCase):
    def test_submission_config_uses_repo_relative_root(self) -> None:
        payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))

        self.assertEqual(payload["path"], "..")
        resolved_root = (CONFIG_PATH.parent / payload["path"]).resolve()
        self.assertEqual(resolved_root, REPO_ROOT.resolve())

    def test_release_docs_and_dashboard_template_are_repo_relative(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        dashboard_builder = (REPO_ROOT / "build_dashboard.py").read_text(encoding="utf-8")

        self.assertNotIn(r"C:\EvidenceQuality", readme)
        self.assertIn("shared projects root", readme)
        self.assertNotIn(r"C:\EvidenceQuality", dashboard_builder)
        self.assertIn("__REVIEWS_SOURCE__", dashboard_builder)


if __name__ == "__main__":
    unittest.main()
