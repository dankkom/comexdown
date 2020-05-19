import unittest
from unittest import mock

from comexdown import download


@mock.patch("comexdown.download.download_file")
class TestDownload(unittest.TestCase):

    def test_exp(self, mock_download):
        download.exp(2019, ".\\DATA")
        mock_download.assert_called_with(
            "http://www.mdic.gov.br/balanca/bd/comexstat-bd/ncm/EXP_2019.csv",
            ".\\DATA",
        )

    def test_imp(self, mock_download):
        download.imp(2019, ".\\DATA")
        mock_download.assert_called_with(
            "http://www.mdic.gov.br/balanca/bd/comexstat-bd/ncm/IMP_2019.csv",
            ".\\DATA",
        )

    def test_exp_mun(self, mock_download):
        download.exp_mun(2019, ".\\DATA")
        mock_download.assert_called_with(
            "http://www.mdic.gov.br/balanca/bd/comexstat-bd/mun/EXP_2019_MUN.csv",
            ".\\DATA",
        )

    def test_imp_mun(self, mock_download):
        download.imp_mun(2019, ".\\DATA")
        mock_download.assert_called_with(
            "http://www.mdic.gov.br/balanca/bd/comexstat-bd/mun/IMP_2019_MUN.csv",
            ".\\DATA",
        )

    def test_exp_nbm(self, mock_download):
        download.exp_nbm(1990, ".\\DATA")
        mock_download.assert_called_with(
            "http://www.mdic.gov.br/balanca/bd/comexstat-bd/nbm/EXP_1990_NBM.csv",
            ".\\DATA",
        )

    def test_imp_nbm(self, mock_download):
        download.imp_nbm(1990, ".\\DATA")
        mock_download.assert_called_with(
            "http://www.mdic.gov.br/balanca/bd/comexstat-bd/nbm/IMP_1990_NBM.csv",
            ".\\DATA",
        )

    def test_exp_complete(self, mock_download):
        download.exp_complete(".\\DATA")
        mock_download.assert_called_with(
            "http://www.mdic.gov.br/balanca/bd/comexstat-bd/ncm/EXP_COMPLETA.zip",
            ".\\DATA",
        )

    def test_imp_complete(self, mock_download):
        download.imp_complete(".\\DATA")
        mock_download.assert_called_with(
            "http://www.mdic.gov.br/balanca/bd/comexstat-bd/ncm/IMP_COMPLETA.zip",
            ".\\DATA",
        )

    def test_exp_mun_complete(self, mock_download):
        download.exp_mun_complete(".\\DATA")
        mock_download.assert_called_with(
            "http://www.mdic.gov.br/balanca/bd/comexstat-bd/mun/EXP_COMPLETA_MUN.zip",
            ".\\DATA",
        )

    def test_imp_mun_complete(self, mock_download):
        download.imp_mun_complete(".\\DATA")
        mock_download.assert_called_with(
            "http://www.mdic.gov.br/balanca/bd/comexstat-bd/mun/IMP_COMPLETA_MUN.zip",
            ".\\DATA",
        )


if __name__ == "__main__":
    unittest.main()
