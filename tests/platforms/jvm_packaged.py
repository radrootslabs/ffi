import platform
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path

from android_elf import check_elf
from runtime_evidence import architecture, container_runtime, record
from test_android import AndroidConsumer
from test_linux_packages import packages
from test_maven_resolution import MavenResolution

ROOT = Path(__file__).resolve().parents[2]


def run(command, cwd=None):
    result = subprocess.run(
        [str(item) for item in command],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout, result.stderr


def run_suite(kind, **attributes):
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(kind)
    for test in suite:
        for name, value in attributes.items():
            setattr(test, name, value)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful() or result.skipped or not result.testsRun:
        raise ValueError("Installed JVM/Android suite must pass without skips")


def check(language, artifacts):
    release = packages.version(ROOT)
    bundle = artifacts / f"maven/radroots-{release}-central-bundle.zip"
    with tempfile.TemporaryDirectory(prefix="radroots-jvm-packaged-") as temporary:
        root = Path(temporary)
        repository = root / "maven"
        packages.extract_zip(bundle, repository)
        for android in (False, True):
            packages.validate_maven(android=android, artifacts=repository)
        if language == "android":
            aar = (
                repository
                / f"org/radroots/radroots-android/{release}/radroots-android-{release}.aar"
            )
            with zipfile.ZipFile(aar) as archive:
                expected = {
                    f"jni/{abi}/libradroots_ffi.so"
                    for abi in ("arm64-v8a", "armeabi-v7a", "x86_64")
                }
                actual = {name for name in archive.namelist() if name.endswith(".so")}
                if expected != actual:
                    raise ValueError("Android AAR native inventory differs")
                for name in actual:
                    check_elf(archive.read(name), name.split("/")[1], 16384)
            run_suite(MavenResolution)
            run_suite(AndroidConsumer, repository_directory=repository)
            return
        packages.test_kotlin_consumer(artifacts=bundle)
        _, java = run(["java", "-version"])
        record(
            "kotlin",
            "macos-" + architecture(),
            "native",
            {"java": java.strip(), "os": platform.platform()},
        )
        jar = repository / f"org/radroots/radroots/{release}/radroots-{release}.jar"
        with zipfile.ZipFile(jar) as archive:
            expected = {
                f"{cpu}/libradroots_ffi.{extension}"
                for cpu, extension in (
                    ("darwin-aarch64", "dylib"),
                    ("darwin-x86-64", "dylib"),
                    ("linux-aarch64", "so"),
                    ("linux-x86-64", "so"),
                )
            }
            if {
                name for name in archive.namelist() if name.endswith((".dylib", ".so"))
            } != expected:
                raise ValueError("JVM native inventory differs")
            library = root / "libradroots_ffi.dylib"
            library.write_bytes(archive.read("darwin-x86-64/libradroots_ffi.dylib"))
        source = root / "link.c"
        source.write_text(
            "#include <stdint.h>\nextern uint16_t uniffi_radroots_ffi_checksum_func_name(void);\nint main(void) { return uniffi_radroots_ffi_checksum_func_name() == 0; }\n"
        )
        run(["clang", "-arch", "x86_64", source, library, "-o", root / "link"])
        record(
            "kotlin",
            "macos-x64",
            "link",
            {"clang": run(["clang", "--version"])[0].strip()},
            cpu="x64",
        )
        consumer = root / "consumer"
        shutil.copytree(ROOT / "tests/consumers/kotlin", consumer)
        run(
            [
                ROOT / "bindings/kotlin/gradlew",
                "--no-daemon",
                "copyRuntimeDependencies",
            ],
            consumer,
        )
        shutil.copytree(consumer / "build/runtime", root / "runtime")
        shutil.copyfile(
            ROOT / "tests/platforms/fixtures/jvm/Consumer.java", root / "Consumer.java"
        )
        coordinate = (
            f"/artifacts/maven/org/radroots/radroots/{release}/radroots-{release}.jar"
        )
        for cpu, suffix in (("arm64", "arm64"), ("amd64", "x64")):
            for version in (8, 21):
                image = f"eclipse-temurin:{version}-jdk-jammy"
                code = f'cp /artifacts/Consumer.java . && javac -cp {coordinate} Consumer.java && java -version >&2 && java -Djna.nosys=true -cp ".:{coordinate}:/artifacts/runtime/*" Consumer'
                stdout, stderr = run(
                    [
                        "docker",
                        "run",
                        "--rm",
                        "--network=none",
                        "--platform",
                        "linux/" + cpu,
                        "--mount",
                        f"type=bind,src={root},dst=/artifacts,readonly",
                        "--workdir",
                        "/tmp",
                        image,
                        "sh",
                        "-ec",
                        code,
                    ]
                )
                if stdout != "Radroots\n":
                    raise ValueError(
                        "Installed JVM consumer produced unexpected output"
                    )
                mode, runtime = container_runtime(image, cpu)
                runtime["java"] = stderr.strip()
                record("kotlin", "linux-" + suffix, mode, runtime, cpu=cpu)
