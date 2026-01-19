import unittest
from pathlib import Path

from comexdown import storage


class TestStorage(unittest.TestCase):

    def setUp(self):
        self.root = Path("tmp")
        with open("testdata.csv", "w") as f:
            f.write(100*"a")

    def test_path_aux(self):
        path = storage.path_aux(self.root, "ncm")
        self.assertEqual(
            path, Path("tmp", "auxiliary-tables", "NCM.csv")
        )

    def test_path_trade(self):
        path = storage.path_trade(self.root, "exp", 2020, mun=False)
        self.assertEqual(
            path, Path("tmp", "exp", "EXP_2020.csv")
        )
        path = storage.path_trade(self.root, "imp", 2020, mun=False)
        self.assertEqual(
            path, Path("tmp", "imp", "IMP_2020.csv")
        )
        path = storage.path_trade(self.root, "exp", 2020, mun=True)
        self.assertEqual(
            path, Path("tmp", "exp-mun", "EXP_2020_MUN.csv")
        )
        path = storage.path_trade(self.root, "imp", 2020, mun=True)
        self.assertEqual(
            path, Path("tmp", "imp-mun", "IMP_2020_MUN.csv")
        )

    def test_path_trade_nbm(self):
        path = storage.path_trade_nbm(self.root, "exp", 1990)
        self.assertEqual(
            path, Path("tmp", "exp-nbm", "EXP_1990_NBM.csv")
        )
        path = storage.path_trade_nbm(self.root, "imp", 1990)
        self.assertEqual(
            path, Path("tmp", "imp-nbm", "IMP_1990_NBM.csv")
        )

    @staticmethod
    def tearDown():
        Path("testdata.csv").unlink()


if __name__ == "__main__":
    unittest.main()
