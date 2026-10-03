import importlib.util
import json
import shutil
import tempfile
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "generation", ROOT / "tools/radroots_ffi/generation.py"
)
generation = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(generation)


class GenerationContractTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="radroots-generation-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        contract = tomllib.loads((ROOT / "contracts/generation.toml").read_text())
        names = set(contract["inputs"] + contract["outputs"]) | {
            "contracts/generation.toml",
            "contracts/bootstrap.toml",
            "tools/radroots_ffi/make.sh",
            "tools/radroots_ffi/native.sh",
            contract["external"]["cpp_facade"],
        }
        for name in names:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, path)

    def test_source_inventory_matches(self):
        generation.validate(self.root)

    def test_rejects_changed_generator_lock(self):
        path = self.root / "package-lock.json"
        value = json.loads(path.read_text())
        value["packages"]["node_modules/@napi-rs/cli"]["version"] = "0.0.0"
        path.write_text(json.dumps(value))
        with self.assertRaisesRegex(ValueError, "Node generator pin"):
            generation.validate(self.root)

    def test_rejects_symlinked_generated_output(self):
        path = self.root / "bindings/python/src/radroots/radroots_ffi.py"
        path.unlink()
        path.symlink_to(self.root / "README.md")
        with self.assertRaisesRegex(ValueError, "Unsafe or missing"):
            generation.validate(self.root)
