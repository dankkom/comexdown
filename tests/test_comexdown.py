import unittest
from pathlib import Path
from unittest import mock

import comexdown


@mock.patch("comexdown.download")
class TestFunctions(unittest.TestCase):

    def setUp(self):
        self.path = Path("tmp")

    def test_get_year(self, mock_download):
        comexdown.get_year(self.path, year=2000, exp=True, imp=True)
        mock_download.exp.assert_called()
        mock_download.imp.assert_called()
        comexdown.get_year(self.path, year=2000, exp=True, imp=True, mun=True)
        mock_download.exp_mun.assert_called()
        mock_download.imp_mun.assert_called()

    def test_get_year_nbm(self, mock_download):
        comexdown.get_year_nbm(self.path, 2000, exp=True, imp=True)
        mock_download.exp_nbm.assert_called()
        mock_download.imp_nbm.assert_called()

    def test_get_complete(self, mock_download):
        comexdown.get_complete(self.path, exp=True, imp=True)
        mock_download.exp_complete.assert_called()
        mock_download.imp_complete.assert_called()
        comexdown.get_complete(self.path, exp=True, imp=True, mun=True)
        mock_download.exp_mun_complete.assert_called()
        mock_download.imp_mun_complete.assert_called()

    def test_get_table(self, mock_download):
        comexdown.get_table(self.path, "ncm")
        mock_download.table.assert_called()


if __name__ == "__main__":
    unittest.main()
