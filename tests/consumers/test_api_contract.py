import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("api", ROOT / "tools/radroots_ffi/api.py")
api = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(api)


class ApiContractTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="radroots-api-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for name in (
            "contracts/api.toml",
            "contracts/bootstrap.toml",
            "pyproject.toml",
            "bindings/typescript/package.json",
            "bindings/go/go.mod",
            "crates/ffi/uniffi.toml",
            "tests/consumers/go/go.mod",
            "tests/platforms/fixtures/go/go.mod",
        ):
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)

    def test_matches_public_packages(self):
        api.validate(self.root)

    def test_rejects_wrong_python_release(self):
        path = self.root / "pyproject.toml"
        path.write_text(
            path.read_text().replace('version = "0.0.0"', 'version = "0.1.0"')
        )
        with self.assertRaisesRegex(ValueError, "identity/version"):
            api.validate(self.root)

    def test_rejects_stale_go_generator(self):
        path = self.root / "crates/ffi/uniffi.toml"
        path.write_text(
            path.read_text().replace(
                "github.com/radrootslabs/ffi/bindings/go", "radroots.org"
            )
        )
        with self.assertRaisesRegex(ValueError, "Go module/generator"):
            api.validate(self.root)

    def test_rejects_wrong_stdout(self):
        path = self.root / "contracts/api.toml"
        path.write_text(
            path.read_text().replace(
                'native_stdout = "Radroots\\n"', 'native_stdout = "Radroots"'
            )
        )
        with self.assertRaisesRegex(ValueError, "API/bootstrap disagreement"):
            api.validate(self.root)
