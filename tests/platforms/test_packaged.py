import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import node_packaged
import packaged
import python_runtime


class FrozenArtifacts(unittest.TestCase):
    def test_skipped_node_suite_cannot_pass(self):
        with patch(
            "node_packaged.run",
            return_value="# tests 2\n# fail 0\n# cancelled 0\n# skipped 1\n",
        ):
            with self.assertRaisesRegex(ValueError, "without skips"):
                node_packaged.suite([], None)

    def test_empty_node_suite_cannot_pass(self):
        with patch(
            "node_packaged.run",
            return_value="# tests 0\n# fail 0\n# cancelled 0\n# skipped 0\n",
        ):
            with self.assertRaisesRegex(ValueError, "empty"):
                node_packaged.suite([], None)

    def test_consumer_mutation_fails_qualification(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            artifact = root / "wheel.whl"
            artifact.write_bytes(b"prepared")
            with patch(
                "packaged.python_consumer",
                side_effect=lambda _: artifact.write_bytes(b"rebuilt"),
            ):
                with self.assertRaisesRegex(ValueError, "changed during"):
                    packaged.check("python", root)

    def test_symlinked_payload_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "wheel.whl").symlink_to(root / "missing")
            with self.assertRaisesRegex(ValueError, "Unsupported prepared"):
                packaged.inventory(root)

    def test_empty_python_suite_cannot_pass(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(AssertionError, "without skips"):
                python_runtime.check(Path(temporary), None)

    def test_skipped_python_suite_cannot_pass(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "test_skipped.py").write_text(
                "import unittest\nclass Probe(unittest.TestCase):\n"
                " @unittest.skip('missing runner')\n def test_missing(self): pass\n"
            )
            with self.assertRaisesRegex(AssertionError, "without skips"):
                python_runtime.check(root, None)
