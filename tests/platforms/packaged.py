import argparse
import hashlib
import json
import platform
import subprocess
import tempfile
import tomllib
from pathlib import Path

from runtime_evidence import architecture, container_runtime, record

ROOT = Path(__file__).resolve().parents[2]


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
    subprocess.run([str(item) for item in command], check=True, **kwargs)


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
            code = (
                "python -m venv /tmp/consumer && "
                "/tmp/consumer/bin/python -m pip install --quiet --no-deps --no-index "
                f"--find-links /artifacts/python radroots=={version} && "
                "/tmp/consumer/bin/python -I /runner/python_runtime.py /tests"
            )
            run(
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
                    image,
                    "sh",
                    "-ec",
                    code,
                ]
            )
            mode, runtime = container_runtime(image, cpu)
            record("python", "linux-" + suffix, mode, runtime, cpu=cpu)


def check(language, artifacts):
    artifacts = Path(artifacts).absolute()
    before = inventory(artifacts)
    try:
        if language == "python":
            python_consumer(artifacts)
        elif language == "typescript":
            from node_packaged import check as node_consumer

            node_consumer(artifacts)
        elif language in ("kotlin", "android"):
            from jvm_packaged import check as jvm_consumer

            jvm_consumer(language, artifacts)
        elif language == "go":
            from jvm_packaged import run_suite
            from test_go_platforms import GoPlatforms
            from test_linux_packages import packages

            version = packages.version(ROOT)
            archive = artifacts / f"go/radroots-go-{version}.zip"
            with tempfile.TemporaryDirectory(
                prefix="radroots-go-packaged-"
            ) as temporary:
                root = Path(temporary)
                packages.extract_zip(archive, root)
                module = root / f"github.com/radrootslabs/ffi/bindings/go@v{version}"
                packages.distribution_files(ROOT, module)
                run_suite(GoPlatforms, module=module, module_zip=archive)
        else:
            raise ValueError("Unsupported packaged language")
    finally:
        if before != inventory(artifacts):
            raise ValueError("Prepared artifacts changed during qualification")
    print(
        json.dumps(
            {"language": language, "artifacts": before, "unchanged": True},
            sort_keys=True,
        )
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "language", choices=("python", "typescript", "kotlin", "android", "go")
    )
    parser.add_argument("--artifacts", type=Path, required=True)
    arguments = parser.parse_args()
    check(arguments.language, arguments.artifacts)


if __name__ == "__main__":
    main()
