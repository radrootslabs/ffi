import argparse
import contextlib
import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

from runtime_evidence import architecture, container_runtime, record

ROOT = Path(__file__).resolve().parents[2]
FAMILIES = (
    "python",
    "typescript",
    "kotlin",
    "linux",
    "go",
    "swift",
    "ios",
    "android",
    "c",
    "cpp",
)


@contextlib.contextmanager
def frozen_environment():
    """Block accidental native producers and retain each invocation's evidence."""
    with tempfile.TemporaryDirectory(prefix="radroots-frozen-guard-") as temporary:
        root = Path(temporary)
        sentinel = root / "rebuild-attempt"
        for name in (
            "cargo",
            "rustc",
            "cargo-zigbuild",
            "wasm-pack",
            "uniffi-bindgen",
            "uniffi-bindgen-go",
        ):
            guard = root / name
            guard.write_text(
                '#!/bin/sh\n: > "' + str(sentinel) + '"\n'
                'echo "Native production is forbidden during frozen qualification" >&2\nexit 97\n'
            )
            guard.chmod(0o755)
        keys = (
            "PATH",
            "CARGO",
            "RUSTC",
            "RADROOTS_TEST_EVIDENCE",
            "RADROOTS_TEST_SUITE",
        )
        original = {key: os.environ.get(key) for key in keys}
        evidence = root / "runtime.jsonl"
        os.environ.update(
            PATH=str(root) + os.pathsep + os.environ.get("PATH", ""),
            CARGO=str(root / "cargo"),
            RUSTC=str(root / "rustc"),
            RADROOTS_TEST_EVIDENCE=str(evidence),
            RADROOTS_TEST_SUITE="packaged",
        )
        try:
            yield evidence
        finally:
            for key, value in original.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
            if sentinel.exists():
                raise ValueError("Native rebuild attempted during frozen qualification")


def validate_runtime(language, evidence):
    entries = (
        [json.loads(line) for line in evidence.read_text().splitlines()]
        if evidence.exists()
        else []
    )
    if not entries or any(entry.get("suite") != "packaged" for entry in entries):
        raise ValueError(
            "Frozen qualification requires actual packaged runtime evidence"
        )
    expected = {
        "python": {
            ("python", "macos-arm64"),
            ("python", "linux-arm64"),
            ("python", "linux-x64"),
        },
        "typescript": {
            ("typescript", target)
            for target in (
                "macos-arm64",
                "macos-x64",
                "linux-arm64",
                "linux-x64",
                "browser",
            )
        },
        "kotlin": {
            ("kotlin", target)
            for target in ("macos-arm64", "macos-x64", "linux-arm64", "linux-x64")
        },
        "go": {
            ("go", target)
            for target in ("macos-arm64", "macos-x64", "linux-arm64", "linux-x64")
        },
        "c": {("c", "macos-arm64")},
        "cpp": {("c", "macos-arm64"), ("cpp", "macos-arm64")},
        "swift": {
            ("swift", target)
            for target in ("macos-arm64", "macos-x64", "ios-arm64", "ios-sim-x64")
        },
        "ios": {("swift", "ios-sim-arm64")},
        "android": {("android", "android-arm64")},
    }
    observed = {(entry["language"], entry["target"]) for entry in entries}
    if language == "linux":
        required = {
            (family, target)
            for family in ("python", "typescript", "kotlin")
            for target in ("linux-arm64", "linux-x64")
        }
    else:
        required = expected.get(language, set())
    if not required.issubset(observed):
        raise ValueError("Frozen runtime matrix is incomplete")
    for entry in entries:
        if (
            entry.get("schema") != 1
            or not entry.get("runtime")
            or entry.get("minimum_runtime") is not False
        ):
            raise ValueError("Invalid frozen runtime evidence")
        target = entry["target"]
        execution = entry["execution"]
        if execution == "link" and (entry["language"], target) not in {
            ("kotlin", "macos-x64"),
            ("swift", "ios-arm64"),
            ("swift", "ios-sim-x64"),
        }:
            raise ValueError("Runtime execution cannot be replaced by linkage")
        if target.startswith("linux-") and execution not in (
            "container-native",
            "container-emulated",
        ):
            raise ValueError("Linux runtime mode differs")
        if (
            entry["language"] == "android"
            and entry["runtime"].get("page_size") != 16384
        ):
            raise ValueError("Android runtime must observe 16 KiB pages")
    if language in ("kotlin", "linux"):
        for target in ("linux-arm64", "linux-x64"):
            java = [
                entry["runtime"].get("java", "")
                for entry in entries
                if (entry["language"], entry["target"]) == ("kotlin", target)
            ]
            if not all(
                any(marker in identity for identity in java)
                for marker in ('version "1.8.', 'version "21.')
            ):
                raise ValueError("Frozen JVM matrix requires Java 8 and 21")
    return entries


def inventory(directory):
    directory = Path(directory)
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError("Prepared artifact directory is missing or symlinked")
    result = {}
    for path in sorted(directory.rglob("*")):
        if path.is_symlink() or not (path.is_file() or path.is_dir()):
            raise ValueError("Unsupported prepared artifact entry")
        if path.is_file():
            result[path.relative_to(directory).as_posix()] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
    if not result:
        raise ValueError("Prepared artifact inventory is empty")
    return result


def run(command, **kwargs):
    return subprocess.run([str(item) for item in command], check=True, **kwargs)


def python_consumer(artifacts):
    version = tomllib.loads((ROOT / "contracts/bootstrap.toml").read_text())["version"]
    wheels = artifacts / "python"
    if len(list(wheels.glob(f"radroots-{version}-*.whl"))) != 3:
        raise ValueError("The Python release requires three prepared wheels")
    with tempfile.TemporaryDirectory(prefix="radroots-packaged-python-") as temporary:
        root = Path(temporary)
        environment = root / "python"
        run(["uv", "venv", "--python", "3.14.7", "--no-python-downloads", environment])
        python = environment / "bin/python"
        run(
            [
                "uv",
                "pip",
                "install",
                "--python",
                python,
                "--no-cache",
                "--no-deps",
                "--no-index",
                "--find-links",
                wheels,
                "radroots==" + version,
            ]
        )
        identity = root / "runtime.json"
        run(
            [
                python,
                "-I",
                ROOT / "tests/platforms/python_runtime.py",
                ROOT / "bindings/python/tests",
                "--identity",
                identity,
            ]
        )
        run([python, "-I", ROOT / "tests/consumers/python_types.py", python])
        runtime = json.loads(identity.read_text())
        cpu = architecture(runtime.pop("architecture"))
        system = "macos" if platform.system() == "Darwin" else "linux"
        record("python", system + "-" + cpu, "native", runtime, cpu=cpu)
        image = "python:3.14.7-slim-bookworm"
        for cpu, suffix in (("arm64", "arm64"), ("amd64", "x64")):
            mode, runtime = container_runtime(image, cpu)
            code = (
                "python -m venv /tmp/consumer && "
                "/tmp/consumer/bin/python -m pip install --quiet --no-deps --no-index "
                f"--find-links /artifacts/python radroots=={version} && "
                "/tmp/consumer/bin/python -I /runner/python_runtime.py /tests --identity /tmp/runtime.json && cat /tmp/runtime.json"
            )
            result = run(
                [
                    "docker",
                    "run",
                    "--rm",
                    "--network=none",
                    "--platform",
                    "linux/" + cpu,
                    "--mount",
                    f"type=bind,src={artifacts},dst=/artifacts,readonly",
                    "--mount",
                    f"type=bind,src={ROOT / 'bindings/python/tests'},dst=/tests,readonly",
                    "--mount",
                    f"type=bind,src={ROOT / 'tests/platforms'},dst=/runner,readonly",
                    runtime["image_id"],
                    "sh",
                    "-ec",
                    code,
                ],
                capture_output=True,
                text=True,
            )
            print(result.stdout, end="")
            print(result.stderr, end="")
            runtime.update(json.loads(result.stdout.splitlines()[-1]))
            record("python", "linux-" + suffix, mode, runtime, cpu=cpu)


def consume(language, artifacts):
    artifacts = Path(artifacts).absolute()
    if language == "python":
        python_consumer(artifacts)
    elif language == "typescript":
        from node_packaged import check as node_consumer

        node_consumer(artifacts)
    elif language in ("kotlin", "android"):
        from jvm_packaged import check as jvm_consumer

        jvm_consumer(language, artifacts)
    elif language == "linux":
        from jvm_packaged import check as jvm_consumer
        from node_packaged import check as node_consumer

        python_consumer(artifacts)
        node_consumer(artifacts)
        jvm_consumer("kotlin", artifacts)
    elif language == "go":
        from jvm_packaged import run_suite
        from test_go_platforms import GoPlatforms
        from test_linux_packages import packages

        version = packages.version(ROOT)
        archive = artifacts / f"go/radroots-go-{version}.zip"
        with tempfile.TemporaryDirectory(prefix="radroots-go-packaged-") as temporary:
            root = Path(temporary)
            packages.extract_zip(archive, root)
            module = root / f"github.com/radrootslabs/ffi/bindings/go@v{version}"
            packages.distribution_files(ROOT, module)
            run_suite(GoPlatforms, module=module, module_zip=archive)
    elif language in ("c", "cpp"):
        run(
            [
                sys.executable,
                ROOT / "tests/consumers/native_packages.py",
                f"test-{language}-package",
                "--artifacts",
                artifacts,
            ]
        )
        for family in ("c", "cpp") if language == "cpp" else ("c",):
            record(
                family,
                "macos-" + architecture(),
                "native",
                {
                    "os": platform.platform(),
                    "compiler": subprocess.check_output(
                        ["cc" if family == "c" else "c++", "--version"], text=True
                    ).strip(),
                },
            )
    elif language in ("swift", "ios"):
        from jvm_packaged import run_suite
        from test_ios import IOSConsumer
        from test_swift_platforms import SwiftPlatforms

        version = tomllib.loads((ROOT / "Cargo.toml").read_text())["workspace"][
            "package"
        ]["version"]
        archive = artifacts / f"swift/radroots-swift-{version}.zip"
        if language == "swift":
            run(
                [
                    sys.executable,
                    ROOT / "tests/consumers/swift_packages.py",
                    "test",
                    "--artifact",
                    archive,
                ]
            )
        with tempfile.TemporaryDirectory(
            prefix="radroots-swift-packaged-"
        ) as temporary:
            from test_linux_packages import packages

            root = Path(temporary)
            packages.extract_zip(archive, root)
            package = root / f"radroots-swift-{version}"
            run_suite(
                SwiftPlatforms if language == "swift" else IOSConsumer,
                package=package,
            )
        if language == "swift":
            record(
                "swift",
                "macos-" + architecture(),
                "native",
                {
                    "swift": subprocess.check_output(
                        ["swift", "--version"], text=True
                    ).strip(),
                    "os": platform.platform(),
                },
            )
    else:
        raise ValueError("Unsupported packaged language")


def check(language, artifacts):
    if language not in FAMILIES:
        raise ValueError("Unsupported packaged language")
    artifacts = Path(artifacts).absolute()
    before = inventory(artifacts)
    try:
        with frozen_environment() as evidence:
            consume(language, artifacts)
            entries = validate_runtime(language, evidence)
    finally:
        after = inventory(artifacts)
        if before != after:
            raise ValueError("Prepared artifacts changed during qualification")
    destination = os.environ.get("RADROOTS_TEST_EVIDENCE")
    if destination:
        with Path(destination).open("a") as output:
            for entry in entries:
                output.write(json.dumps(entry, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "language": language,
                "before": before,
                "after": after,
                "unchanged": True,
                "runtime": entries,
                "command": sys.argv,
                "exit_status": 0,
            },
            sort_keys=True,
        )
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "language",
        choices=FAMILIES,
    )
    parser.add_argument("--artifacts", type=Path, required=True)
    arguments = parser.parse_args()
    check(arguments.language, arguments.artifacts)


if __name__ == "__main__":
    main()
