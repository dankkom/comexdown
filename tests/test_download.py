import unittest
from pathlib import Path
from unittest import mock

from comexdown import download


class TestDownloadFile(unittest.TestCase):

    @mock.patch("comexdown.download.sys")
    @mock.patch("comexdown.download.request")
    @mock.mock_open()
    def test_download_file(self, mock_open, mock_request, mock_sys):
        download.download_file("http://www.example.com/file.csv", Path("data"))
        mock_open.assert_called()
        mock_sys.stdout.write.assert_called()
        mock_sys.stdout.flush.assert_called()
        mock_request.urlopen.assert_called()


@mock.patch("comexdown.download.download_file")
class TestDownload(unittest.TestCase):

    def test_exp(self, mock_download):
        download.exp(2019, Path("data"))
        mock_download.assert_called_with(
            "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/ncm/EXP_2019.csv",
            Path("data"),
        )

    def test_imp(self, mock_download):
        download.imp(2019, Path("data"))
        mock_download.assert_called_with(
            "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/ncm/IMP_2019.csv",
            Path("data"),
        )

    def test_exp_mun(self, mock_download):
        download.exp_mun(2019, Path("data"))
        mock_download.assert_called_with(
            "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/mun/EXP_2019_MUN.csv",
            Path("data"),
        )

    def test_imp_mun(self, mock_download):
        download.imp_mun(2019, Path("data"))
        mock_download.assert_called_with(
            "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/mun/IMP_2019_MUN.csv",
            Path("data"),
        )

    def test_exp_nbm(self, mock_download):
        download.exp_nbm(1990, Path("data"))
        mock_download.assert_called_with(
            "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/nbm/EXP_1990_NBM.csv",
            Path("data"),
        )

    def test_imp_nbm(self, mock_download):
        download.imp_nbm(1990, Path("data"))
        mock_download.assert_called_with(
            "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/nbm/IMP_1990_NBM.csv",
            Path("data"),
        )

    def test_exp_complete(self, mock_download):
        download.exp_complete(Path("data"))
        mock_download.assert_called_with(
            "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/ncm/EXP_COMPLETA.zip",
            Path("data"),
        )

    def test_imp_complete(self, mock_download):
        download.imp_complete(Path("data"))
        mock_download.assert_called_with(
            "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/ncm/IMP_COMPLETA.zip",
            Path("data"),
        )

    def test_exp_mun_complete(self, mock_download):
        download.exp_mun_complete(Path("data"))
        mock_download.assert_called_with(
            "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/mun/EXP_COMPLETA_MUN.zip",
            Path("data"),
        )

    def test_imp_mun_complete(self, mock_download):
        download.imp_mun_complete(Path("data"))
        mock_download.assert_called_with(
            "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/mun/IMP_COMPLETA_MUN.zip",
            Path("data"),
        )

    def test_agronegocio(self, mock_download):
        download.agronegocio(Path("data"))
        mock_download.assert_called_with(
            "https://github.com/dankkom/ncm-agronegocio/raw"
            "/master/ncm-agronegocio.csv",
            Path("data"),
        )


if __name__ == "__main__":
    unittest.main()
