import hashlib
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

import package_tools as packages


class MavenBundle(unittest.TestCase):
    def test_bundle_is_deterministic_and_extractable_without_prefix(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "Cargo.toml").write_text('[workspace.package]\nversion="0.0.0"\n')
            repository = root / "build/dist/maven"
            for artifact, extension in (
                ("radroots", "jar"),
                ("radroots-android", "aar"),
            ):
                for ending in (
                    "." + extension,
                    ".pom",
                    ".module",
                    "-sources.jar",
                    "-javadoc.jar",
                ):
                    for checksum in ("", ".md5", ".sha1", ".sha256", ".sha512"):
                        path = (
                            repository
                            / f"org/radroots/{artifact}/0.0.0/{artifact}-0.0.0{ending}{checksum}"
                        )
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_bytes(
                            hashlib.new(checksum[1:], b"prepared").hexdigest().encode()
                            if checksum
                            else b"prepared"
                        )
            with patch("package_tools.validate_maven"):
                packages.build_maven_bundle(root)
                bundle = repository / "radroots-0.0.0-central-bundle.zip"
                original = bundle.read_bytes()
                packages.build_maven_bundle(root)
                self.assertEqual(bundle.read_bytes(), original)
                packages.extract_zip(bundle, root / "installed")
                with zipfile.ZipFile(bundle) as archive:
                    self.assertEqual(len(archive.namelist()), 50)
                self.assertEqual(
                    (
                        root
                        / "installed/org/radroots/radroots/0.0.0/radroots-0.0.0.jar"
                    ).read_bytes(),
                    b"prepared",
                )
                required = repository / "org/radroots/radroots/0.0.0/radroots-0.0.0.jar"
                required.unlink()
                with self.assertRaisesRegex(ValueError, "missing"):
                    packages.build_maven_bundle(root)
                self.assertEqual(bundle.read_bytes(), original)
                required.write_bytes(b"prepared")
                required.with_suffix(".jar.sha256").write_text("invalid")
                with self.assertRaisesRegex(ValueError, "checksum differs"):
                    packages.build_maven_bundle(root)
                self.assertEqual(bundle.read_bytes(), original)
