import unittest
from pathlib import Path
from unittest import mock

import comex_fetcher


@mock.patch("comex_fetcher.download.download_file")
class TestFunctions(unittest.TestCase):
    def setUp(self):
        self.path = Path("tmp")

    def test_get_year(self, mock_download_file):
        comex_fetcher.get_year(self.path, year=2000, exp=True, imp=True)
        # Should be called twice (exp and imp)
        self.assertEqual(mock_download_file.call_count, 2)

        comex_fetcher.get_year(self.path, year=2000, exp=True, imp=True, mun=True)
        # Should be called 2 more times (exp_mun and imp_mun)
        self.assertEqual(mock_download_file.call_count, 4)

    def test_get_year_nbm(self, mock_download_file):
        comex_fetcher.get_year_nbm(self.path, 2000, exp=True, imp=True)
        self.assertEqual(mock_download_file.call_count, 2)

    def test_get_table(self, mock_download_file):
        comex_fetcher.get_table(self.path, "ncm")
        mock_download_file.assert_called_once()

    def test_get_repetro(self, mock_download_file):
        comex_fetcher.get_repetro(self.path)
        self.assertEqual(mock_download_file.call_count, 2)

    def test_get_validation(self, mock_download_file):
        comex_fetcher.get_validation(self.path)
        self.assertEqual(mock_download_file.call_count, 4)

    def test_get_other_tables(self, mock_download_file):
        comex_fetcher.get_other_tables(self.path)
        mock_download_file.assert_called_once()


if __name__ == "__main__":
    unittest.main()
