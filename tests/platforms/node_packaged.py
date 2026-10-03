import json
import platform
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from runtime_evidence import architecture, container_runtime, record
from test_linux_packages import LinuxPackages, packages

ROOT = Path(__file__).resolve().parents[2]


def run(command, cwd=None):
    result = subprocess.run(
        [str(item) for item in command],
        cwd=cwd,
        check=True,
        text=True,
        capture_output=True,
    )
    print(result.stdout, end="")
    print(result.stderr, end="")
    return result.stdout


def suite(command, cwd):
    output = run(command, cwd)
    counts = dict(re.findall(r"^# (tests|fail|cancelled|skipped) (\d+)$", output, re.M))
    if not counts.get("tests") or int(counts["tests"]) == 0:
        raise ValueError("Installed Node suite is empty")
    if any(counts.get(key) != "0" for key in ("fail", "cancelled", "skipped")):
        raise ValueError(
            "Installed Node suite must pass without skips or cancellations"
        )


def check(artifacts):
    release = packages.version(ROOT)
    archives = artifacts / "npm"
    if len(list(archives.glob("*.tgz"))) != 5:
        raise ValueError("The npm release requires five prepared archives")
    browser = packages.test_typescript_consumer(browser=True, artifacts=archives)
    record("typescript", "browser", "browser", browser)
    record(
        "typescript",
        "macos-" + architecture(),
        "native",
        {"node": run(["node", "--version"]).strip(), "os": platform.platform()},
    )
    with tempfile.TemporaryDirectory(prefix="radroots-node-packaged-") as temporary:
        root = Path(temporary)
        consumer = root / "compiler"
        shutil.copytree(ROOT / "tests/consumers/typescript", consumer)
        shutil.copytree(ROOT / "bindings/typescript/test", consumer / "test")
        run(["npm", "ci", "--ignore-scripts", "--no-audit", "--no-fund"], consumer)
        run(
            [
                "npm",
                "install",
                "--offline",
                "--ignore-scripts",
                "--no-audit",
                "--no-fund",
                archives / f"radroots-{release}.tgz",
                archives / f"radroots-native-darwin-arm64-{release}.tgz",
            ],
            consumer,
        )
        run(["npm", "run", "build"], consumer)
        shutil.copytree(consumer / "build/test", root / "test")
        shutil.copytree(archives, root / "npm")
        (root / "package.json").write_text(
            json.dumps({"private": True, "type": "module"})
        )
        probe = LinuxPackages("test_macos_x64_npm_consumer")
        probe.artifacts = artifacts
        probe.test_macos_x64_npm_consumer()
        tools = ROOT / "build/node-x64/node-v22.22.3-darwin-x64"
        native = root / "macos-x64"
        native.mkdir()
        shutil.copytree(root / "test", native / "test")
        shutil.copyfile(root / "package.json", native / "package.json")
        run(
            [
                tools / "bin/node",
                tools / "lib/node_modules/npm/bin/npm-cli.js",
                "install",
                "--offline",
                "--ignore-scripts",
                "--no-audit",
                "--no-fund",
                archives / f"radroots-{release}.tgz",
                archives / f"radroots-native-darwin-x64-{release}.tgz",
            ],
            native,
        )
        suite(
            [
                tools / "bin/node",
                "--test",
                "--test-reporter=tap",
                "test/node.test.js",
                "test/wasm.test.js",
            ],
            native,
        )
        for cpu, suffix in (("arm64", "arm64"), ("amd64", "x64")):
            image = "node:22.22.3-bookworm-slim"
            code = (
                "mkdir /tmp/consumer && cd /tmp/consumer && "
                "cp /artifacts/package.json . && cp -R /artifacts/test . && "
                "npm install --offline --ignore-scripts --no-audit --no-fund "
                f"/artifacts/npm/radroots-{release}.tgz "
                f"/artifacts/npm/radroots-native-linux-{suffix}-gnu-{release}.tgz >/dev/null && "
                "node --test --test-reporter=tap test/node.test.js test/wasm.test.js"
            )
            suite(
                [
                    "docker",
                    "run",
                    "--rm",
                    "--network=none",
                    "--platform",
                    "linux/" + cpu,
                    "--mount",
                    f"type=bind,src={root},dst=/artifacts,readonly",
                    image,
                    "sh",
                    "-ec",
                    code,
                ],
                root,
            )
            mode, runtime = container_runtime(image, cpu)
            record("typescript", "linux-" + suffix, mode, runtime, cpu=cpu)
