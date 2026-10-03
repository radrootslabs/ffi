"""Compare prepared Go bytes with the official VCS module ZIP implementation."""

import subprocess
import tempfile
import zipfile
from pathlib import Path

import package_tools

ROOT = Path(__file__).resolve().parents[2]


def check(sdk=ROOT):
    files = package_tools.distribution_files(sdk)
    payloads = {
        "bindings/go/" + name: path.read_bytes()
        for name, path in files.items()
        if name.startswith("internal/native/lib/")
    }
    tracked = (
        subprocess.check_output(
            ["git", "-C", str(sdk), "ls-files", "-z", "--", "bindings/go"]
        )
        .decode()
        .split("\0")[:-1]
    )
    with tempfile.TemporaryDirectory(prefix="radroots-go-vcs-") as temporary:
        root = Path(temporary)
        repository = root / "repository"
        repository.mkdir()

        def git(*arguments):
            return (
                subprocess.check_output(
                    [
                        "git",
                        "-C",
                        str(repository),
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

        git("init", "--quiet")
        for name in tracked:
            source = package_tools.safe_file(sdk, name)
            destination = repository / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(source.read_bytes())
        git("add", "bindings")
        source = git("commit-tree", git("write-tree"), "-m", "Source fixture")
        for name, content in payloads.items():
            destination = repository / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(content)
        git("add", "--force", *sorted(payloads))
        distribution = git(
            "commit-tree",
            git("write-tree"),
            "-p",
            source,
            "-m",
            "Additive distribution fixture",
        )
        git("update-ref", "refs/heads/master", distribution)
        # The production distribution validator enforces the same eight-file delta.
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "go_distribution", sdk / "tools/radroots_ffi/go_distribution.py"
        )
        validator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(validator)
        validator.validate_delta(repository, source, distribution, payloads)
        prepared = sdk / f"build/dist/go/radroots-go-{package_tools.version(sdk)}.zip"

        def compare(path):
            return subprocess.run(
                [
                    "go",
                    "run",
                    "-mod=readonly",
                    ".",
                    str(repository),
                    distribution,
                    str(path),
                    str(root / "vcs.zip"),
                ],
                cwd=sdk / "tests/consumers/go_zip",
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

        result = compare(prepared)
        if result.returncode:
            raise ValueError(result.stderr)
        print("Go VCS module ZIP parity: " + result.stdout.strip())
        for remove in (True, False):
            altered = root / "altered.zip"
            with (
                zipfile.ZipFile(prepared) as before,
                zipfile.ZipFile(altered, "w") as after,
            ):
                for entry in before.infolist():
                    if remove and entry.filename.endswith("/api_test.go"):
                        continue
                    after.writestr(entry, before.read(entry))
                if not remove:
                    after.writestr("unexpected.go", b"package unexpected")
            rejected = compare(altered)
            if rejected.returncode == 0 or "inventory differs" not in rejected.stderr:
                raise ValueError("Go VCS ZIP fault control failed")
        print("Go VCS ZIP missing/extra-member fault controls passed")


if __name__ == "__main__":
    check()
