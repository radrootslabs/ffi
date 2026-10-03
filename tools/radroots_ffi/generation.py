import json
import tomllib
from pathlib import Path


def validate(root):
    contract = tomllib.loads((root / "contracts/generation.toml").read_text())
    if (
        set(contract)
        != {
            "schema_version",
            "languages",
            "inputs",
            "outputs",
            "rust",
            "node",
            "external",
        }
        or contract["schema_version"] != 1
    ):
        raise ValueError("Unsupported generation contract")
    bootstrap = tomllib.loads((root / "contracts/bootstrap.toml").read_text())
    if contract["languages"] != bootstrap["languages"]:
        raise ValueError("Generation language coverage differs")
    for kind in ("inputs", "outputs"):
        paths = contract[kind]
        if len(paths) != len(set(paths)) or not paths:
            raise ValueError(f"Invalid generation {kind} inventory")
        for name in paths:
            path = Path(name)
            source = root / path
            if (
                path.is_absolute()
                or ".." in path.parts
                or source.is_symlink()
                or not source.is_file()
                or not source.resolve().is_relative_to(root.resolve())
            ):
                raise ValueError(f"Unsafe or missing generation file: {name}")
    workspace = tomllib.loads((root / "Cargo.toml").read_text())["workspace"]
    locked = tomllib.loads((root / "Cargo.lock").read_text())["package"]
    for name, version in contract["rust"].items():
        dependency = workspace["dependencies"][name]
        actual = dependency if isinstance(dependency, str) else dependency["version"]
        if actual != "=" + version or not any(
            item["name"] == name and item["version"] == version for item in locked
        ):
            raise ValueError(f"Rust generator pin differs: {name}")
    tooling = json.loads((root / "package.json").read_text())
    lock = json.loads((root / "package-lock.json").read_text())
    for name, version in contract["node"].items():
        if (
            tooling["devDependencies"][name] != version
            or lock["packages"]["node_modules/" + name]["version"] != version
        ):
            raise ValueError(f"Node generator pin differs: {name}")
    go = json.loads((root / contract["external"]["go_configuration"]).read_text())
    if go["uniffi"] != contract["rust"]["uniffi"] or len(go["revision"]) != 40:
        raise ValueError("Go generator compatibility or revision differs")
    commands = (root / "tools/radroots_ffi/make.sh").read_text() + (
        root / "tools/radroots_ffi/native.sh"
    ).read_text()
    for name in ("cbindgen", "wasm-pack"):
        if name + " " + contract["external"][name] not in commands:
            raise ValueError(f"External generator command pin differs: {name}")
    if not (root / contract["external"]["cpp_facade"]).is_file():
        raise ValueError("Missing C++ facade")


if __name__ == "__main__":
    validate(Path(__file__).resolve().parents[2])
    print("Generation inventory and locked tool pins match")
