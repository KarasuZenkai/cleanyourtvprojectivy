"""Comprueba el formato de las listas de referencia conservadas en examples/.

Run from the repository root: python3 -m unittest discover -s tests -v
"""
import re
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
PACKAGE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z0-9_]+)+$")


def folders():
    return sorted(p for p in EXAMPLES.iterdir() if p.is_dir())


class ExampleListsTest(unittest.TestCase):
    def test_every_folder_has_a_list(self):
        for folder in folders():
            with self.subTest(folder=folder.name):
                self.assertTrue((folder / "debloat.txt").is_file(), "no debloat.txt")

    def test_list_format(self):
        for folder in folders():
            path = folder / "debloat.txt"
            if not path.is_file():
                continue
            with self.subTest(folder=folder.name):
                lines = path.read_text(encoding="utf-8").split("\n")
                self.assertTrue(lines and lines[0].startswith("#"),
                                "first line should be a comment naming the TV, Android version and build")
                packages = []
                for n, line in enumerate(lines, 1):
                    body = line.split("#", 1)[0].strip()
                    if not body:
                        continue
                    self.assertRegex(body, PACKAGE, f"line {n}: not a package name: {line!r}")
                    packages.append(body)
                self.assertTrue(packages, "una carpeta de ejemplos necesita una lista de paquetes")
                dupes = sorted({p for p in packages if packages.count(p) > 1})
                self.assertFalse(dupes, f"listed twice: {dupes}")

if __name__ == "__main__":
    unittest.main()
