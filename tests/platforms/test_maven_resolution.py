import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class MavenResolution(unittest.TestCase):
    def test_missing_prepared_coordinates_cannot_use_a_shadow_repository(self):
        settings = (
            ROOT / "bindings/kotlin/android-smoke/settings.gradle.kts"
        ).read_text()
        for present in (True, False):
            with (
                self.subTest(prepared=present),
                tempfile.TemporaryDirectory(
                    prefix="radroots-maven-selection-"
                ) as temporary,
            ):
                root = Path(temporary)
                for repository in ("repository", "shadow"):
                    base = root / repository / "org/radroots/radroots/0.0.0"
                    base.mkdir(parents=True)
                    if repository == "repository" and not present:
                        continue
                    (base / "radroots-0.0.0.pom").write_text(
                        "<project><modelVersion>4.0.0</modelVersion>"
                        "<groupId>org.radroots</groupId><artifactId>radroots</artifactId>"
                        "<version>0.0.0</version></project>"
                    )
                    (base / "radroots-0.0.0.jar").write_text(repository)
                (root / "settings.gradle.kts").write_text(
                    settings.replace(
                        "google()", 'maven { url = uri("shadow") }'
                    ).replace("mavenCentral()", 'maven { url = uri("shadow") }')
                )
                (root / "build.gradle.kts").write_text(
                    "val probe by configurations.creating\n"
                    'dependencies { add("probe", "org.radroots:radroots:0.0.0") }\n'
                    'tasks.register("verifySelection") { doLast {\n'
                    'check(probe.singleFile.readText() == "repository") { "WRONG_REPOSITORY" }\n'
                    'println("PREPARED_REPOSITORY_SELECTED")\n} }\n'
                )
                result = subprocess.run(
                    [
                        str(ROOT / "bindings/kotlin/gradlew"),
                        "--no-daemon",
                        "--offline",
                        "verifySelection",
                    ],
                    cwd=root,
                    capture_output=True,
                    text=True,
                    timeout=180,
                )
                output = result.stdout + result.stderr
                if present:
                    self.assertEqual(result.returncode, 0, output)
                    self.assertIn("PREPARED_REPOSITORY_SELECTED", output)
                else:
                    self.assertNotEqual(result.returncode, 0, output)
                    self.assertIn("Could not find org.radroots:radroots:0.0.0", output)
                    self.assertNotIn("WRONG_REPOSITORY", output)
