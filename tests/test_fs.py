from comexdown.fs import DataDirectory
import os
import tempfile
import unittest
from unittest import mock

from comexdown import fs


class TestFS(unittest.TestCase):

    @staticmethod
    def setUp():
        with open("testdata.csv", "w") as f:
            f.write(100*"a")

    def test_get_hash(self):
        blake2 = fs.get_hash("testdata.csv")
        self.assertEqual(
            blake2,
            "edd9e36b355fdacc63b23b6b522294f5d3ccd6ed8df37a2ff1c6d074634995c8"
            "c9d987365a237550ac2939feb38548f76ba54b5d6b6f80e3840e53fb1a8b67f7",
        )

    @staticmethod
    def tearDown():
        os.remove("testdata.csv")


class TestDataDirectory(unittest.TestCase):

    def setUp(self):
        self.dd = DataDirectory(root="tmp")

    def test_path_aux(self):
        path = self.dd.path_aux("ncm")
        self.assertEqual(
            str(path), os.path.join("tmp", "auxiliary_tables", "NCM.csv")
        )

    def test_path_trade(self):
        path = self.dd.path_trade("exp", 2020, mun=False)
        self.assertEqual(
            str(path), os.path.join("tmp", "exp", "EXP_2020.csv")
        )
        path = self.dd.path_trade("imp", 2020, mun=False)
        self.assertEqual(
            str(path), os.path.join("tmp", "imp", "IMP_2020.csv")
        )
        path = self.dd.path_trade("exp", 2020, mun=True)
        self.assertEqual(
            str(path), os.path.join("tmp", "mun_exp", "EXP_2020_MUN.csv")
        )
        path = self.dd.path_trade("imp", 2020, mun=True)
        self.assertEqual(
            str(path), os.path.join("tmp", "mun_imp", "IMP_2020_MUN.csv")
        )

    def test_path_trade_nbm(self):
        path = self.dd.path_trade_nbm("exp", 1990)
        self.assertEqual(
            str(path), os.path.join("tmp", "nbm_exp", "EXP_1990_NBM.csv")
        )
        path = self.dd.path_trade_nbm("imp", 1990)
        self.assertEqual(
            str(path), os.path.join("tmp", "nbm_imp", "IMP_1990_NBM.csv")
        )

    @mock.patch("comexdown.fs.get_hash")
    @mock.mock_open()
    def test_create_index(self, mock_open, mock_get_hash):
        self.dd.create_index()
        mock_get_hash.assert_called()
        mock_open.assert_called()

    @mock.mock_open()
    def test_read_index(self, mock_open):
        self.dd.read_index()
        mock_open.assert_called()


if __name__ == "__main__":
    unittest.main()
