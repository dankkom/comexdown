"""Functions to download foreign trade data from remote servers.

This module provides functionality for downloading files from the Brazilian
government's foreign trade data servers. It includes features for:
- Progress tracking during downloads
- Automatic retry on failure
- File timestamp comparison to avoid redundant downloads
- Chunked streaming downloads for large files

The module disables SSL warnings for compatibility with government servers
that may have certificate issues.
"""

import sys
import time
from pathlib import Path

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def remote_is_more_recent(headers: dict, dest: Path) -> bool:
    """Check if the remote file is more recent than the local file.

    Compares the Last-Modified header from a remote file with the modification
    time of a local file to determine if the remote version is newer.

    Parameters
    ----------
    headers : dict
        HTTP headers from the remote server response, should contain
        'Last-Modified' field in standard HTTP date format.
    dest : Path
        Path to the local file to compare against.

    Returns
    -------
    bool
        True if the remote file is more recent than the local file,
        False if the local file doesn't exist, the remote has no
        Last-Modified header, or the local file is up to date.

    Notes
    -----
    This function is used to avoid re-downloading files that haven't
    changed on the server, saving bandwidth and time.
    """
    if not dest.exists():
        return False

    last_modified = headers.get("Last-Modified")
    if last_modified:
        # Parse standard HTTP date format
        remote_mtime = time.mktime(
            time.strptime(last_modified, "%a, %d %b %Y %H:%M:%S %Z")
        )
        if dest.stat().st_mtime < remote_mtime:
            return True

    return False


def _print_progress(
    downloaded: int,
    total: int,
    width: int = 50,
) -> None:
    """Print download progress bar to stdout.

    Displays a real-time progress bar showing download completion percentage
    and downloaded size in MiB.

    Parameters
    ----------
    downloaded : int
        Number of bytes downloaded so far.
    total : int
        Total file size in bytes. If 0 or None, progress bar is not shown.
    width : int, optional
        Width of the progress bar in characters, by default 50.

    Notes
    -----
    The progress bar is printed to stdout using carriage return to update
    in place. Format: [=====>-----] 45.2% (12.34 MiB)
    """
    if not total:
        return

    p = downloaded / total
    filled = int(p * width)
    bar = "=" * filled + "-" * (width - filled)
    size_mb = downloaded / (1024 * 1024)
    msg = f"\r[{bar}] {p:.1%} ({size_mb:.2f} MiB)"
    sys.stdout.write(msg)
    sys.stdout.flush()


def _download_stream(
    response: requests.Response,
    output: Path,
    blocksize: int,
) -> None:
    """Stream download content to file with progress tracking.

    Downloads a file in chunks, writing to disk incrementally while displaying
    progress information.

    Parameters
    ----------
    response : requests.Response
        Active HTTP response object with streaming enabled.
    output : Path
        Destination file path where content will be written.
    blocksize : int
        Size of chunks to download and write at a time, in bytes.

    Raises
    ------
    requests.HTTPError
        If the response status code indicates an error.

    Notes
    -----
    This function writes data to disk as it's downloaded rather than loading
    the entire file into memory, making it suitable for large files.
    """
    response.raise_for_status()
    total_length = int(response.headers.get("content-length", 0))

    downloaded_size = 0
    with open(output, "wb") as f:
        for chunk in response.iter_content(chunk_size=blocksize):
            if chunk:
                f.write(chunk)
                downloaded_size += len(chunk)
                _print_progress(downloaded_size, total_length)

    sys.stdout.write("\n")


def download_file(
    url: str,
    output: Path,
    retry: int = 3,
    blocksize: int = 8192,
    verify_ssl: bool = False,
) -> Path:
    """Download a file from a URL to a specific output path.

    Downloads a file with automatic retry on failure, progress tracking,
    and smart update detection. Creates parent directories as needed.
    Checks if local file is already up to date before downloading.

    Parameters
    ----------
    url : str
        Source URL of the file to download.
    output : Path
        Destination local path where the file will be saved.
    retry : int, optional
        Maximum number of download attempts, by default 3.
    blocksize : int, optional
        Size of chunks to download at a time in bytes, by default 8192.
    verify_ssl : bool, optional
        Whether to verify SSL certificates, by default False.
        Set to False for compatibility with some government servers.

    Returns
    -------
    Path
        The path to the downloaded file (same as output parameter).

    Raises
    ------
    requests.RequestException
        If all download attempts fail.

    Notes
    -----
    - Parent directories are created automatically if they don't exist
    - File is only downloaded if it doesn't exist locally or if the remote
      version is newer (based on Last-Modified header)
    - Uses a browser-like User-Agent header for compatibility
    - Retries with 2-second delay between attempts on failure
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/142.0.0.0 Safari/537.36"
        ),
    }

    # Ensure parent directory exists
    output.parent.mkdir(parents=True, exist_ok=True)

    for attempt in range(retry):
        sys.stdout.write(f"Downloading: {url:<50} --> {output.name}\n")
        sys.stdout.flush()

        try:
            # Check for updates with HEAD request
            head_resp = requests.head(
                url, headers=headers, timeout=10, verify=verify_ssl
            )

            # Check if local file is up to date (i.e. remote is NOT newer)
            cond = remote_is_more_recent(head_resp.headers, output)
            if output.exists() and not cond:
                sys.stdout.write(f"{output.name} is up to date.\n")
                sys.stdout.flush()
                return output

            # Perform the specific download
            with requests.get(
                url,
                headers=headers,
                stream=True,
                timeout=30,
                verify=verify_ssl,
            ) as r:
                _download_stream(r, output, blocksize)

            return output

        except requests.RequestException as e:
            sys.stdout.write(f"\nError downloading {url}: {e}\n")
            if attempt < retry - 1:
                time.sleep(2)
            else:
                raise

    return output
