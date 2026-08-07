#!/usr/bin/env python3

"""Command-line interface for downloading Brazil's foreign trade data.

This tool provides access to trade transaction data and auxiliary code tables
from Brazil's Ministry of Economy (SECEX/COMEX).
"""

import sys

from .plugin import app


def main(argv: list[str] | None = None) -> None:
    """Main entry point."""
    if argv is None:
        argv = sys.argv[1:]
    app(argv)

if __name__ == "__main__":
    main()
