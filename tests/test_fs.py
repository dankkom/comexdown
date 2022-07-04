import os
import pathlib
import unittest

from comexdown import fs


class TestFS(unittest.TestCase):

    def setUp(self):
        self.root = pathlib.Path("tmp")
        with open("testdata.csv", "w") as f:
            f.write(100*"a")

    def test_path_aux(self):
        path = fs.path_aux(self.root, "ncm")
        self.assertEqual(
            str(path), os.path.join("tmp", "auxiliary-tables", "NCM.csv")
        )

    def test_path_trade(self):
        path = fs.path_trade(self.root, "exp", 2020, mun=False)
        self.assertEqual(
            str(path), os.path.join("tmp", "exp", "EXP_2020.csv")
        )
        path = fs.path_trade(self.root, "imp", 2020, mun=False)
        self.assertEqual(
            str(path), os.path.join("tmp", "imp", "IMP_2020.csv")
        )
        path = fs.path_trade(self.root, "exp", 2020, mun=True)
        self.assertEqual(
            str(path), os.path.join("tmp", "exp-mun", "EXP_2020_MUN.csv")
        )
        path = fs.path_trade(self.root, "imp", 2020, mun=True)
        self.assertEqual(
            str(path), os.path.join("tmp", "imp-mun", "IMP_2020_MUN.csv")
        )

    def test_path_trade_nbm(self):
        path = fs.path_trade_nbm(self.root, "exp", 1990)
        self.assertEqual(
            str(path), os.path.join("tmp", "exp-nbm", "EXP_1990_NBM.csv")
        )
        path = fs.path_trade_nbm(self.root, "imp", 1990)
        self.assertEqual(
            str(path), os.path.join("tmp", "imp-nbm", "IMP_1990_NBM.csv")
        )

    @staticmethod
    def tearDown():
        os.remove("testdata.csv")


if __name__ == "__main__":
    unittest.main()
