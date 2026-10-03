import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "bootstrap", ROOT / "tools/radroots_ffi/bootstrap.py"
)
bootstrap = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bootstrap)


class BootstrapContractTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="radroots-bootstrap-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for name in (
            "Cargo.toml",
            "rust-toolchain.toml",
            "contracts/bootstrap.toml",
            "crates/example/Cargo.toml",
        ):
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)

    def test_source_contract_matches(self):
        bootstrap.validate(self.root)

    def test_rejects_package_version_drift(self):
        path = self.root / "Cargo.toml"
        path.write_text(
            path.read_text().replace('version = "0.0.0"', 'version = "0.1.0"')
        )
        with self.assertRaisesRegex(ValueError, "Bootstrap contract differs"):
            bootstrap.validate(self.root)

    def test_rejects_publishable_example(self):
        path = self.root / "crates/example/Cargo.toml"
        path.write_text(path.read_text().replace("publish = false", "publish = true"))
        with self.assertRaisesRegex(ValueError, "publication policy differs"):
            bootstrap.validate(self.root)
