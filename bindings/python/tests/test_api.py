import subprocess
import sys
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import radroots


class RadrootsTests(unittest.TestCase):
    def test_identity(self):
        self.assertEqual(radroots.NAME, "Radroots")
        self.assertEqual(radroots.name(), "Radroots")

    def test_repeated_calls(self):
        self.assertEqual([radroots.name() for _ in range(1000)], ["Radroots"] * 1000)

    def test_concurrent_calls(self):
        def names(_):
            return [radroots.name() for _ in range(128)]

        with ThreadPoolExecutor(max_workers=8) as executor:
            for values in executor.map(names, range(8)):
                self.assertEqual(values, ["Radroots"] * 128)

    def test_print_name(self):
        result = subprocess.run(
            [
                sys.executable,
                "-I",
                str(Path(__file__).parent / "helpers/print_name.py"),
            ],
            capture_output=True,
            text=True,
            timeout=20,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "Radroots\n")
        self.assertEqual(result.stderr, "")
