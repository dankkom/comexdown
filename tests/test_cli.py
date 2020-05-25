import argparse
from collections import namedtuple
import os
import unittest
from unittest import mock

from comexdown import cli
from comexdown import download as d


class TestCliFunctions(unittest.TestCase):

    def test_set_parser(self):
        parser = cli.set_parser()
        self.assertIsInstance(parser, argparse.ArgumentParser)

    def test_expand_years(self):
        years = cli.expand_years(["2010:2019", "2000:2005"])
        self.assertListEqual(
            years,
            [y for y in range(2010, 2020)] + [y for y in range(2000, 2006)]
        )
        years = cli.expand_years(["2000:2005", "2010:2019"])
        self.assertListEqual(
            years,
            [y for y in range(2000, 2006)] + [y for y in range(2010, 2020)]
        )
        years = cli.expand_years(["2000:2005", "2010"])
        self.assertListEqual(
            years,
            [y for y in range(2000, 2006)] + [2010]
        )
        years = cli.expand_years(["2010", "2000:2005"])
        self.assertListEqual(
            years,
            [2010] + [y for y in range(2000, 2006)]
        )
        years = cli.expand_years(["2010", "2005:2000"])
        self.assertListEqual(
            years,
            [2010] + [2005, 2004, 2003, 2002, 2001, 2000]
        )

    @mock.patch("comexdown.cli.set_parser")
    def test_main(self, mock_set_parser):
        cli.main()
        mock_set_parser.assert_called()
        parser = mock_set_parser.return_value
        parser.parse_args.assert_called()
        args = parser.parse_args.return_value
        args.func.assert_called()


class TestCliDownloadTrade(unittest.TestCase):

    def setUp(self):
        self.parser = cli.set_parser()
        self.Args = namedtuple("Args", ["exp", "imp", "mun"])
        self.o = os.path.join(".", "DATA")

    @mock.patch("comexdown.cli.get_year")
    def test_download_trade_args(self, mock_get_year):
        args_list = [
            self.Args(exp=False, imp=True, mun=False),
            self.Args(exp=False, imp=True, mun=True),
            self.Args(exp=True, imp=False, mun=False),
            self.Args(exp=True, imp=False, mun=True),
            self.Args(exp=True, imp=True, mun=False),
            self.Args(exp=True, imp=True, mun=True),
        ]
        for args in args_list:
            mutable = []
            if args.exp:
                mutable.append("-exp")
            if args.imp:
                mutable.append("-imp")
            if args.mun:
                mutable.append("-mun")
            self.args = self.parser.parse_args(
                ["download", "trade", "2010"] + mutable + ["-o", self.o]
            )
            self.args.func(self.args)
            mock_get_year.assert_called_with(
                year=2010,
                exp=args.exp,
                imp=args.imp,
                mun=args.mun,
                path=self.o,
            )

        self.args = self.parser.parse_args(
            ["download", "trade", "2010", "-o", self.o]
        )
        self.args.func(self.args)
        mock_get_year.assert_called_with(
            year=2010,
            exp=True,
            imp=True,
            mun=False,
            path=self.o,
        )

        self.args = self.parser.parse_args(
            ["download", "trade", "2010", "-mun", "-o", self.o]
        )
        self.args.func(self.args)
        mock_get_year.assert_called_with(
            year=2010,
            exp=True,
            imp=True,
            mun=True,
            path=self.o,
        )

    @mock.patch("comexdown.cli.get_complete")
    def test_download_trade_complete_args(self, mock_get_complete):
        args_list = [
            # self.Args(exp=False, imp=False, mun=False),
            # self.Args(exp=False, imp=False, mun=True),
            self.Args(exp=False, imp=True, mun=False),
            self.Args(exp=False, imp=True, mun=True),
            self.Args(exp=True, imp=False, mun=False),
            self.Args(exp=True, imp=False, mun=True),
            self.Args(exp=True, imp=True, mun=False),
            self.Args(exp=True, imp=True, mun=True),
        ]
        for args in args_list:
            mutable = []
            if args.exp:
                mutable.append("-exp")
            if args.imp:
                mutable.append("-imp")
            if args.mun:
                mutable.append("-mun")
            self.args = self.parser.parse_args(
                ["download", "trade", "complete"] + mutable + ["-o", self.o]
            )
            self.args.func(self.args)
            mock_get_complete.assert_called_with(
                exp=args.exp,
                imp=args.imp,
                mun=args.mun,
                path=self.o,
            )

        self.args = self.parser.parse_args(
            ["download", "trade", "complete", "-o", self.o]
        )
        self.args.func(self.args)
        mock_get_complete.assert_called_with(
            exp=True,
            imp=True,
            mun=False,
            path=self.o,
        )

        self.args = self.parser.parse_args(
            ["download", "trade", "complete", "-mun", "-o", self.o]
        )
        self.args.func(self.args)
        mock_get_complete.assert_called_with(
            exp=True,
            imp=True,
            mun=True,
            path=self.o,
        )


class TestCliDownloadCode(unittest.TestCase):

    def setUp(self):
        self.parser = cli.set_parser()
        self.o = os.path.join(".", "DATA")

    @mock.patch("comexdown.cli.get_table")
    def test_download_table_all(self, mock_get_table):
        self.args = self.parser.parse_args(
            [
                "download",
                "table",
                "all",
                "-o",
                self.o,
            ]
        )
        self.args.func(self.args)
        mock_get_table.assert_called()
        self.assertEqual(mock_get_table.call_count, len(d.AUX_TABLES))

    @mock.patch("comexdown.cli.get_table")
    def test_download_table(self, mock_get_table):
        for table_name in d.AUX_TABLES:
            self.args = self.parser.parse_args(
                [
                    "download",
                    "table",
                    table_name,
                    "-o",
                    self.o,
                ]
            )
            self.args.func(self.args)
            mock_get_table.assert_called_with(
                table=table_name,
                path=self.o,
            )

    @mock.patch("comexdown.cli.print_code_tables")
    def test_download_table_print_code_tables(self, mock_print_code_tables):
        self.args = self.parser.parse_args(
            [
                "download",
                "table",
            ]
        )
        self.args.func(self.args)
        mock_print_code_tables.assert_called()


if __name__ == "__main__":
    unittest.main()
