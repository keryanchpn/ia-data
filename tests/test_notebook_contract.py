import json
import unittest
from pathlib import Path


NOTEBOOK_PATH = Path(__file__).resolve().parents[1] / "notebook" / "analyse_anssi.ipynb"


class NotebookContractTest(unittest.TestCase):
    def test_csv_loading_is_stable_from_project_root(self):
        notebook = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
        source = "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"])

        self.assertIn("PROJECT_ROOT", source)
        self.assertIn("data/vulnerabilites_anssi.csv", source)
        self.assertNotIn('pd.read_csv("../data/vulnerabilites_anssi.csv"', source)

    def test_supervised_validation_keeps_one_sample_per_class_in_test_set(self):
        notebook = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
        source = "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"])

        self.assertIn("class_counts", source)
        self.assertIn("min_test_size", source)
        self.assertIn("test_size=test_size", source)


if __name__ == "__main__":
    unittest.main()
