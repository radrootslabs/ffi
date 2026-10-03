import json
import tomllib
from pathlib import Path


def validate(root):
    api = tomllib.loads((root / "contracts/api.toml").read_text())
    bootstrap = tomllib.loads((root / "contracts/bootstrap.toml").read_text())
    if set(api) != {
        "schema_version",
        "version",
        "implementation",
        "native_stdout",
        "browser_print",
        "c_abi_version",
        "packages",
        "imports",
        "behavior",
    }:
        raise ValueError("Unsupported API contract fields")
    if api["schema_version"] != 1 or api["implementation"] != "local_example":
        raise ValueError("Unsupported API implementation or schema")
    for key in ("version", "native_stdout", "browser_print", "c_abi_version"):
        if api[key] != bootstrap[key]:
            raise ValueError(f"API/bootstrap disagreement: {key}")
    packages = api["packages"]
    if packages != {
        "python": "radroots",
        "npm": "radroots",
        "maven": "org.radroots:radroots",
        "android": "org.radroots:radroots-android",
        "swift": "Radroots",
        "go": "github.com/radrootslabs/ffi/bindings/go",
    }:
        raise ValueError("Public package contract differs")
    python = tomllib.loads((root / "pyproject.toml").read_text())["project"]
    npm = json.loads((root / "bindings/typescript/package.json").read_text())
    for language, manifest in (("python", python), ("npm", npm)):
        if (
            manifest["name"] != packages[language]
            or manifest["version"] != api["version"]
        ):
            raise ValueError(f"Package identity/version differs: {language}")
    module = (root / "bindings/go/go.mod").read_text().splitlines()[0]
    generator = tomllib.loads((root / "crates/ffi/uniffi.toml").read_text())["bindings"]
    if module != "module " + packages["go"] or generator["go"]["go_mod"] != (
        packages["go"] + "/internal/native"
    ):
        raise ValueError("Go module/generator identity differs")
    for name in ("tests/consumers/go/go.mod", "tests/platforms/fixtures/go/go.mod"):
        if packages["go"] not in (root / name).read_text():
            raise ValueError("Go consumer identity differs")
    if generator["kotlin"]["package_name"] != "org.radroots.internal":
        raise ValueError("Kotlin generated namespace differs")
    if generator["swift"]["module_name"] != "RadrootsBindings":
        raise ValueError("Swift generated module differs")
    if set(api["imports"]) != {
        "python",
        "typescript",
        "browser",
        "kotlin",
        "swift",
        "go",
        "c",
        "cpp",
    }:
        raise ValueError("Incomplete public import inventory")


if __name__ == "__main__":
    validate(Path(__file__).resolve().parents[2])
    print("FFI API contract matches example and package identities")
