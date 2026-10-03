import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import jvm_packaged
import node_packaged
import packaged
import python_runtime


class FrozenArtifacts(unittest.TestCase):
    def test_empty_installed_unittest_suite_cannot_pass(self):
        class Empty(unittest.TestCase):
            pass

        with self.assertRaisesRegex(ValueError, "without skips"):
            jvm_packaged.run_suite(Empty)

    def test_skipped_installed_unittest_suite_cannot_pass(self):
        class Skipped(unittest.TestCase):
            @unittest.skip("runner missing")
            def test_runtime(self):
                pass

        with self.assertRaisesRegex(ValueError, "without skips"):
            jvm_packaged.run_suite(Skipped)

    def test_missing_artifact_root_fails_all_families(self):
        with tempfile.TemporaryDirectory() as temporary:
            for family in packaged.FAMILIES:
                with self.subTest(family=family):
                    with self.assertRaisesRegex(ValueError, "missing"):
                        packaged.check(family, Path(temporary) / "missing")

    def test_ten_families_are_exposed(self):
        self.assertEqual(len(set(packaged.FAMILIES)), 10)
        self.assertIn("linux", packaged.FAMILIES)

    def test_rebuild_cannot_be_ignored(self):
        old_path = os.environ["PATH"]
        with self.assertRaisesRegex(ValueError, "rebuild attempted"):
            with packaged.frozen_environment():
                result = subprocess.run(["cargo", "build"], capture_output=True)
                self.assertEqual(result.returncode, 97)
        self.assertEqual(os.environ["PATH"], old_path)

    def test_absent_runtime_cannot_pass(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(ValueError, "actual packaged"):
                packaged.validate_runtime("python", Path(temporary) / "missing")

    def test_incomplete_matrix_cannot_pass(self):
        with tempfile.TemporaryDirectory() as temporary:
            evidence = Path(temporary) / "runtime.jsonl"
            evidence.write_text(
                '{"suite":"packaged","language":"python","target":"macos-arm64"}\n'
            )
            with self.assertRaisesRegex(ValueError, "incomplete"):
                packaged.validate_runtime("python", evidence)

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
