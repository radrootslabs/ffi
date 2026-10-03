import re
import subprocess


def validate_delta(repository, source, distribution, payloads):
    if not all(
        re.fullmatch(r"[0-9a-f]{40}", value) for value in (source, distribution)
    ):
        raise ValueError("Go distribution requires exact commit identities")
    expected = {
        f"bindings/go/internal/native/lib/{platform}/libradroots_ffi.a{suffix}"
        for platform in ("darwin_arm64", "darwin_amd64", "linux_arm64", "linux_amd64")
        for suffix in ("", ".json")
    }
    if set(payloads) != expected:
        raise ValueError("Go distribution requires exactly eight declared payloads")

    def git(*arguments):
        return subprocess.check_output(["git", "-C", str(repository), *arguments])

    parents = git("rev-list", "--parents", "-n", "1", distribution).decode().split()
    if parents != [distribution, source]:
        raise ValueError("Go distribution must have source as its sole parent")
    entries = git(
        "diff", "--no-renames", "--name-status", "-z", source, distribution
    ).split(b"\0")
    if entries[-1] != b"" or len(entries[:-1]) != 16:
        raise ValueError("Go distribution tree delta differs")
    additions = {}
    for status, raw_path in zip(entries[0:-1:2], entries[1:-1:2], strict=True):
        path = raw_path.decode()
        if status != b"A" or path not in expected or path in additions:
            raise ValueError("Go distribution permits only declared additions")
        entry = git("ls-tree", distribution, "--", path)
        if not entry.startswith(b"100644 blob "):
            raise ValueError(
                "Go distribution payload must be a regular non-executable file"
            )
        additions[path] = git("show", distribution + ":" + path)
    if additions != payloads:
        raise ValueError("Go distribution payload bytes differ")
    return {"source": source, "distribution": distribution, "paths": sorted(additions)}
