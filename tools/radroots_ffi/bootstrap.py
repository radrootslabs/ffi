import tomllib
from pathlib import Path


def validate(root):
    cargo = tomllib.loads((root / "Cargo.toml").read_text())
    package = cargo["workspace"]["package"]
    dependency = cargo["workspace"]["dependencies"]["radroots"]
    contract = tomllib.loads((root / "contracts/bootstrap.toml").read_text())
    toolchain = tomllib.loads((root / "rust-toolchain.toml").read_text())
    expected = {
        "schema_version": 1,
        "repository": package["repository"],
        "homepage": package["homepage"],
        "version": package["version"],
        "publication": "unpublished",
        "core_package": dependency["package"],
        "core_path": dependency["path"],
        "adapter_dependency_alias": "radroots",
        "canonical_core_repository": "https://github.com/radrootslabs/lib",
        "canonical_core_integration": "deferred",
        "name": "Radroots",
        "native_stdout": "Radroots\n",
        "browser_print": "console.log(name()) after initialize()",
        "rust_toolchain": toolchain["toolchain"]["channel"],
        "c_abi_version": 65536,
        "languages": ["c", "cpp", "go", "kotlin", "python", "swift", "typescript"],
    }
    if contract != expected:
        raise ValueError("Bootstrap contract differs from the supported source scope")
    core = tomllib.loads((root / dependency["path"] / "Cargo.toml").read_text())
    if (
        core["package"]["name"] != dependency["package"]
        or core["package"]["publish"] is not False
        or package["publish"] is not False
        or dependency["version"] != "=" + package["version"]
        or package["rust-version"] != contract["rust_toolchain"]
    ):
        raise ValueError("Example package identity or publication policy differs")


if __name__ == "__main__":
    validate(Path(__file__).resolve().parents[2])
    print("Bootstrap contract matches the unpublished example and adapters")
