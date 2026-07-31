import argparse
import unittest
from unittest import mock

from comex_fetcher import cli


class TestCliFunctions(unittest.TestCase):
    def test_get_parser(self):
        parser = cli.get_parser()
        self.assertIsInstance(parser, argparse.ArgumentParser)

    def test_expand_years(self):
        years = cli.expand_years(["2010:2019", "2000:2005"])
        self.assertListEqual(
            years, [y for y in range(2010, 2020)] + [y for y in range(2000, 2006)]
        )
        years = cli.expand_years(["2000:2005", "2010:2019"])
        self.assertListEqual(
            years, [y for y in range(2000, 2006)] + [y for y in range(2010, 2020)]
        )
        years = cli.expand_years(["2000:2005", "2010"])
        self.assertListEqual(years, [y for y in range(2000, 2006)] + [2010])
        years = cli.expand_years(["2010", "2000:2005"])
        self.assertListEqual(years, [2010] + [y for y in range(2000, 2006)])
        years = cli.expand_years(["2010", "2005:2000"])
        self.assertListEqual(years, [2010] + [2005, 2004, 2003, 2002, 2001, 2000])

    @mock.patch("comex_fetcher.cli.get_parser")
    def test_main(self, mock_get_parser):
        cli.main()
        mock_get_parser.assert_called()
        parser = mock_get_parser.return_value
        parser.parse_args.assert_called()
        args = parser.parse_args.return_value
        args.func.assert_called()


class TestCliSync(unittest.TestCase):
    def setUp(self):
        self.parser = cli.get_parser()

    def test_sync_defaults(self):
        args = self.parser.parse_args(["sync"])
        self.assertEqual(args.func, cli.handle_sync)
        self.assertEqual(args.years, [])
        self.assertFalse(args.no_tables)
        self.assertFalse(args.tables_only)
        self.assertFalse(args.dry_run)
        self.assertFalse(args.repetro)
        self.assertFalse(args.validation)
        self.assertFalse(args.other_tables)

    def test_sync_with_years(self):
        args = self.parser.parse_args(["sync", "2020", "2022:2024"])
        self.assertListEqual(args.years, ["2020", "2022:2024"])

    def test_sync_with_new_options(self):
        args = self.parser.parse_args(
            ["sync", "--repetro", "--validation", "--other-tables"]
        )
        self.assertTrue(args.repetro)
        self.assertTrue(args.validation)
        self.assertTrue(args.other_tables)


class TestCliList(unittest.TestCase):
    def setUp(self):
        self.parser = cli.get_parser()

    def test_list_dispatches(self):
        args = self.parser.parse_args(["list"])
        self.assertIs(args.func, cli.handle_list)


if __name__ == "__main__":
    unittest.main()
