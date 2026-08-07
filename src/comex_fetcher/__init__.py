"""Brazil's foreign trade data downloader"""

from importlib.metadata import PackageNotFoundError, version

from quantilica.core.logging import get_logger

try:
    __version__ = version("comex-fetcher")
except PackageNotFoundError:
    __version__ = "0.0.0"

logger = get_logger(__name__)

__all__ = ["__version__"]
