#!/usr/bin/env python3
import os
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEIGHTS = Path(os.environ.get("DOFBOT_MODEL_PATH", ROOT / "models" / "best.pt"))


class ModelArtifactTests(unittest.TestCase):
    def test_model_artifact_policy(self):
        gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("*.pt", gitignore)
        self.assertIn("models/", gitignore)

    @unittest.skipUnless(WEIGHTS.exists(), "trained weights are not stored in Git")
    def test_local_weights_are_nonempty(self):
        self.assertGreater(WEIGHTS.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
