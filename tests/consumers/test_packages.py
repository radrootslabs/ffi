import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from package_tools import core_identity, digest, distribution_files, package_go


class GoDistributionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="radroots-go-provenance-")
        self.addCleanup(self.temporary.cleanup)
        self.sdk = Path(self.temporary.name)
        self.module = self.sdk / "bindings/go"
        self.module.mkdir(parents=True)
        (self.sdk / "crates/ffi").mkdir(parents=True)
        (self.sdk / "Cargo.toml").write_text(
            '[workspace.dependencies.radroots]\nrev = "' + "a" * 40 + '"\n'
        )
        (self.sdk / "rust-toolchain.toml").write_text(
            '[toolchain]\nchannel = "1.99.0"\n'
        )
        (self.module / "go.mod").write_text(
            "module github.com/radrootslabs/ffi/bindings/go\n\ngo 1.27.1\n"
        )
        self.generator = {
            "version": "test",
            "revision": "b" * 40,
            "repository": "https://example.invalid/generator",
            "uniffi": "test",
        }
        (self.sdk / "crates/ffi/go-bindgen.json").write_text(json.dumps(self.generator))
        self.policy = {
            "platforms": {
                "darwin_arm64": "aarch64-apple-darwin",
                "linux_amd64": "x86_64-unknown-linux-gnu",
            },
            "source_files": [
                "Cargo.toml",
                "rust-toolchain.toml",
                "crates/ffi/go-bindgen.json",
                "bindings/go/native-platforms.json",
                "bindings/go/go.mod",
            ],
            "package_files": ["go.mod", "native-platforms.json"],
        }
        (self.module / "native-platforms.json").write_text(json.dumps(self.policy))
        self.receipts = []
        self.archives = []
        for target_platform, target in self.policy["platforms"].items():
            archive = (
                self.module / f"internal/native/lib/{target_platform}/libradroots_ffi.a"
            )
            archive.parent.mkdir(parents=True)
            archive.write_bytes(b"!<arch>\n")
            receipt = archive.with_name(archive.name + ".json")
            receipt.write_text(
                json.dumps(
                    {
                        "schema": 1,
                        "platform": target_platform,
                        "rust_target": target,
                        "profile": "release",
                        "core_rev": "a" * 40,
                        "archive_sha256": digest(archive),
                        "inputs": [
                            {"path": name, "sha256": digest(self.sdk / name)}
                            for name in self.policy["source_files"]
                        ],
                        "generator": self.generator | {"binary_sha256": "c" * 64},
                        "rustc": "rustc 1.99.0 (fixture)",
                    }
                )
            )
            self.archives.append(archive)
            self.receipts.append(receipt)

    def change_receipt(self, **changes):
        receipt = self.receipts[0]
        receipt.write_text(json.dumps(json.loads(receipt.read_text()) | changes))

    def test_complete_archive_is_deterministic_and_excludes_test_sources(self):
        (self.module / "api_test.go").write_text("package radroots_test\n")
        first = self.sdk / "first.zip"
        second = self.sdk / "second.zip"
        package_go(self.sdk, first, "github.com/radrootslabs/ffi/bindings/go@v0.0.0")
        package_go(self.sdk, second, "github.com/radrootslabs/ffi/bindings/go@v0.0.0")
        self.assertEqual(first.read_bytes(), second.read_bytes())
        with zipfile.ZipFile(first) as archive:
            self.assertEqual(
                set(archive.namelist()),
                {
                    f"github.com/radrootslabs/ffi/bindings/go@v0.0.0/{name}"
                    for name in distribution_files(self.sdk)
                },
            )
            self.assertFalse(
                any(name.endswith("_test.go") for name in archive.namelist())
            )

    def test_missing_native_archive_is_rejected(self):
        self.archives[0].unlink()
        with self.assertRaisesRegex(ValueError, "Invalid or missing distribution file"):
            distribution_files(self.sdk)

    def test_corrupt_native_archive_is_rejected(self):
        self.archives[0].write_bytes(b"corrupt")
        with self.assertRaisesRegex(ValueError, "Stale or corrupt"):
            distribution_files(self.sdk)

    def test_changed_input_is_rejected(self):
        (self.module / "go.mod").write_text("module example.invalid/wrong\n")
        with self.assertRaisesRegex(ValueError, "Stale or corrupt"):
            distribution_files(self.sdk)

    def test_wrong_generator_revision_is_rejected(self):
        self.change_receipt(
            generator=self.generator | {"revision": "d" * 40, "binary_sha256": "c" * 64}
        )
        with self.assertRaisesRegex(ValueError, "Wrong Go generator provenance"):
            distribution_files(self.sdk)

    def test_inconsistent_generator_binary_is_rejected(self):
        self.change_receipt(generator=self.generator | {"binary_sha256": "d" * 64})
        with self.assertRaisesRegex(ValueError, "inconsistent generator binaries"):
            distribution_files(self.sdk)

    def test_wrong_compiler_is_rejected(self):
        self.change_receipt(rustc="rustc 1.96.0 (fixture)")
        with self.assertRaisesRegex(ValueError, "Wrong Rust toolchain"):
            distribution_files(self.sdk)

    def test_symlinked_archive_is_rejected(self):
        archive = self.archives[0]
        target = self.sdk / "external.a"
        archive.rename(target)
        archive.symlink_to(target)
        with self.assertRaisesRegex(ValueError, "Invalid or missing"):
            distribution_files(self.sdk)


class ExampleCoreIdentityTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="radroots-example-core-")
        self.addCleanup(temporary.cleanup)
        self.sdk = Path(temporary.name)
        (self.sdk / "crates/example/src").mkdir(parents=True)
        (self.sdk / "Cargo.toml").write_text(
            "[workspace.dependencies.radroots]\n"
            'package = "radroots_ffi_example"\n'
            'path = "crates/example"\nversion = "=0.0.0"\n'
        )
        (self.sdk / "crates/example/Cargo.toml").write_text(
            '[package]\nname = "radroots_ffi_example"\n'
        )
        self.source = self.sdk / "crates/example/src/lib.rs"
        self.source.write_text('pub const NAME: &str = "Radroots";\n')

    def test_identity_changes_with_source_and_new_modules(self):
        original = core_identity(self.sdk)
        self.assertRegex(original, r"^example-sha256:[0-9a-f]{64}$")
        self.assertEqual(original, core_identity(self.sdk))
        self.source.write_text('pub const NAME: &str = "Changed";\n')
        changed = core_identity(self.sdk)
        self.assertNotEqual(original, changed)
        self.source.with_name("additional.rs").write_text("pub const VALUE: u8 = 1;\n")
        self.assertNotEqual(changed, core_identity(self.sdk))

    def test_rejects_missing_and_symlinked_core_source(self):
        self.source.unlink()
        with self.assertRaisesRegex(ValueError, "Missing example core source"):
            core_identity(self.sdk)
        other = self.sdk / "external.rs"
        other.write_text("pub const EXTERNAL: u8 = 1;\n")
        self.source.symlink_to(other)
        with self.assertRaisesRegex(ValueError, "Invalid or missing"):
            core_identity(self.sdk)

    def test_rejects_arbitrary_path_dependency(self):
        manifest = self.sdk / "Cargo.toml"
        manifest.write_text(manifest.read_text().replace("crates/example", "../core"))
        with self.assertRaisesRegex(ValueError, "Unexpected local example dependency"):
            core_identity(self.sdk)


if __name__ == "__main__":
    unittest.main()
