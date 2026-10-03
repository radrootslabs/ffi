import hashlib
import importlib.util
import os
import platform
import shutil
import subprocess
import tarfile
import tempfile
import tomllib
import unittest
import urllib.request
from pathlib import Path

from runtime_evidence import architecture as normalized_architecture
from runtime_evidence import record

SDK = Path(__file__).resolve().parents[2]
VERSION = tomllib.loads((SDK / "Cargo.toml").read_text())["workspace"]["package"][
    "version"
]
spec = importlib.util.spec_from_file_location(
    "sdk_packages", SDK / "tests/consumers/package_tools.py"
)
packages = importlib.util.module_from_spec(spec)
spec.loader.exec_module(packages)


class LinuxPackages(unittest.TestCase):
    artifacts = Path(
        os.environ.get("RADROOTS_PACKAGE_ROOT", SDK / "build/dist")
    ).resolve()

    def run_command(self, command, cwd=None):
        result = subprocess.run(
            [str(item) for item in command],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=900,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    @unittest.skipUnless(
        platform.system() == "Darwin", "The macOS x64 consumer requires macOS"
    )
    def test_macos_x64_npm_consumer(self):
        tools = SDK / "build/node-x64"
        node = tools / "node-v22.22.3-darwin-x64/bin/node"
        if not node.is_file():
            tools.mkdir(parents=True, exist_ok=True)
            name = "node-v22.22.3-darwin-x64.tar.gz"
            base = "https://nodejs.org/dist/v22.22.3/"
            checksums = (
                urllib.request.urlopen(base + "SHASUMS256.txt", timeout=60)
                .read()
                .decode()
            )
            expected = next(
                line.split()[0]
                for line in checksums.splitlines()
                if line.endswith("  " + name)
            )
            artifact = tools / name
            urllib.request.urlretrieve(base + name, artifact)
            self.assertEqual(
                hashlib.sha256(artifact.read_bytes()).hexdigest(), expected
            )
            with tarfile.open(artifact) as archive:
                archive.extractall(tools, filter="data")
        with tempfile.TemporaryDirectory(prefix="radroots_node-x64-") as temporary:
            root = Path(temporary)
            npm = tools / "node-v22.22.3-darwin-x64/lib/node_modules/npm/bin/npm-cli.js"
            self.run_command(
                [
                    node,
                    npm,
                    "install",
                    "--ignore-scripts",
                    "--offline",
                    "--no-audit",
                    "--no-fund",
                    self.artifacts / f"npm/radroots-native-darwin-x64-{VERSION}.tgz",
                    self.artifacts / f"npm/radroots-{VERSION}.tgz",
                ],
                cwd=root,
            )
            shutil.copyfile(
                SDK / "tests/platforms/fixtures/node/consumer.mjs",
                root / "consumer.mjs",
            )
            result = self.run_command([node, "consumer.mjs"], cwd=root)
            self.assertEqual(result.stdout, "Radroots\n")
            record(
                "typescript",
                "macos-x64",
                "native" if normalized_architecture() == "x64" else "rosetta",
                {
                    "node": self.run_command([node, "--version"]).stdout.strip(),
                    "os": platform.platform(),
                },
                cpu="x64",
            )

    def test_linux_packaged_consumers(self):
        from packaged import check

        check("linux", self.artifacts)


if __name__ == "__main__":
    unittest.main()
