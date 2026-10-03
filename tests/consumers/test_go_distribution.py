import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "go_distribution", ROOT / "tools/radroots_ffi/go_distribution.py"
)
distribution = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(distribution)


class AdditiveDistribution(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="radroots-go-delta-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.git("init", "--quiet")
        (self.root / "source.txt").write_text("source")
        self.git("add", "source.txt")
        self.source = self.commit([])
        self.payloads = {
            f"bindings/go/internal/native/lib/{platform}/libradroots_ffi.a{suffix}": b"prepared"
            for platform in (
                "darwin_arm64",
                "darwin_amd64",
                "linux_arm64",
                "linux_amd64",
            )
            for suffix in ("", ".json")
        }
        for name, content in self.payloads.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        self.git("add", "bindings")

    def git(self, *arguments):
        return (
            subprocess.check_output(
                [
                    "git",
                    "-C",
                    str(self.root),
                    "-c",
                    "user.name=FFI Fixture",
                    "-c",
                    "user.email=ffi@example.invalid",
                    *arguments,
                ]
            )
            .decode()
            .strip()
        )

    def commit(self, parents):
        arguments = ["commit-tree", self.git("write-tree"), "-m", "Fixture"]
        for parent in parents:
            arguments.extend(["-p", parent])
        return self.git(*arguments)

    def test_exact_additive_tree_and_sole_parent_pass(self):
        candidate = self.commit([self.source])
        result = distribution.validate_delta(
            self.root, self.source, candidate, self.payloads
        )
        self.assertEqual(result["paths"], sorted(self.payloads))

    def test_source_mutation_and_merge_parent_fail(self):
        (self.root / "source.txt").write_text("changed")
        self.git("add", "source.txt")
        candidate = self.commit([self.source])
        with self.assertRaisesRegex(ValueError, "tree delta"):
            distribution.validate_delta(
                self.root, self.source, candidate, self.payloads
            )
        other = self.commit([])
        merge = self.commit([self.source, other])
        with self.assertRaisesRegex(ValueError, "sole parent"):
            distribution.validate_delta(self.root, self.source, merge, self.payloads)

    def test_executable_and_wrong_payload_fail(self):
        path = sorted(self.payloads)[0]
        self.git("update-index", "--chmod=+x", path)
        candidate = self.commit([self.source])
        with self.assertRaisesRegex(ValueError, "non-executable"):
            distribution.validate_delta(
                self.root, self.source, candidate, self.payloads
            )
        self.git("update-index", "--chmod=-x", path)
        candidate = self.commit([self.source])
        altered = {**self.payloads, path: b"altered"}
        with self.assertRaisesRegex(ValueError, "bytes differ"):
            distribution.validate_delta(self.root, self.source, candidate, altered)
