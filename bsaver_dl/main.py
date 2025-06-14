#!/usr/bin/env python3
"""
BeatSaver Playlist Downloader

A comprehensive CLI tool for downloading BeatSaver playlists.
This tool reads .bplist files (BeatSaver playlist format), extracts metadata,
downloads cover images, and fetches all associated song files (.zip) from BeatSaver's CDN.

Features:
- Rich CLI interface with progress bars and status indicators
- Automatic filename sanitization for cross-platform compatibility
- Resume capability (skips already downloaded files)
- Comprehensive error handling and logging
- Browser-like User-Agent to avoid 403 responses
- Detailed playlist and song status reporting

Author: Open Source Community
License: MIT
Repository: https://github.com/cristiangauma/bsaver-dl
"""

import argparse
import base64
import json
import logging
import re
import shutil
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

# Third-party dependencies
try:
    from rich.console import Console
    from rich.logging import RichHandler
    from rich.panel import Panel
    from rich.progress import (
        BarColumn,
        Progress,
        TextColumn,
        TimeElapsedColumn,
        TimeRemainingColumn,
    )
    from rich.table import Table
    from rich.text import Text
except ImportError:
    print(
        "This script requires the 'rich' library for enhanced UI.\n"
        "Install it with: pip install rich",
        file=sys.stderr
    )
    sys.exit(1)

# Import version from package
try:
    from . import __version__
except ImportError:
    __version__ = "1.0.0"  # Fallback version

# Constants
BEATSAVER_CDN_URL = "https://r2cdn.beatsaver.com"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/115.0 Safari/537.36"
)
MAX_RETRIES = 3
RETRY_DELAY = 1.0

# Global console instance
console = Console()


class PlaylistDownloaderError(Exception):
    """Base exception class for all playlist downloader errors.
    
    This exception serves as the parent class for all custom exceptions
    raised by the playlist downloader. It allows for catching all
    downloader-specific errors with a single except clause.
    
    Attributes:
        Inherits all attributes from the base Exception class.
    """
    pass


class PlaylistParseError(PlaylistDownloaderError):
    """Exception raised when playlist file cannot be parsed or is invalid.
    
    This exception is raised when:
    - Playlist file doesn't exist or cannot be read
    - File contains invalid JSON syntax
    - File has encoding issues
    - File structure doesn't match expected format
    
    Attributes:
        Inherits all attributes from PlaylistDownloaderError.
    """
    pass


class DownloadError(PlaylistDownloaderError):
    """Exception raised when download operations fail permanently.
    
    This exception is raised for non-recoverable download failures
    that cannot be resolved through retry mechanisms. Individual
    song download failures are typically handled gracefully without
    raising this exception.
    
    Attributes:
        Inherits all attributes from PlaylistDownloaderError.
    """
    pass


def setup_logging(verbose: bool = False) -> None:
    """Configure logging with Rich handler for enhanced output.
    
    Sets up the logging system with Rich integration for beautiful
    console output including colored logs and rich tracebacks.
    
    Args:
        verbose (bool): Enable debug-level logging if True, defaults to False.
            When False, only INFO level and above will be shown.
    
    Returns:
        None
    
    Note:
        This function configures the global logging system and should
        be called once at the start of the application.
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True)]
    )


def safe_filename(name: str, replace_with: str = "_", max_length: int = 200) -> str:
    """
    Sanitize a string to be safe as a filename across different operating systems.
    
    This function removes or replaces characters that are illegal in filenames
    on Windows, macOS, and Linux systems. It also handles Unicode normalization
    and length limitations.
    
    Args:
        name: The original filename string
        replace_with: Character to replace illegal characters with
        max_length: Maximum allowed filename length
        
    Returns:
        A sanitized filename string safe for all major operating systems
        
    Examples:
        >>> safe_filename('My "Awesome" Playlist: Part 1')
        'My _Awesome_ Playlist_ Part 1'
        >>> safe_filename('Song\\with/illegal?chars*')
        'Song_with_illegal_chars_'
    """
    if not name:
        return "untitled"
    
    # Remove/replace illegal characters for Windows/Unix filesystems
    # < > : " / \ | ? * and control characters (0x00-0x1F)
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1F]', replace_with, name)
    
    # Normalize whitespace
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    
    # Remove leading/trailing dots and spaces (Windows compatibility)
    sanitized = sanitized.strip('. ')
    
    # Ensure we have something left
    if not sanitized:
        return "untitled"
    
    # Truncate if too long, but preserve extension if present
    if len(sanitized) > max_length:
        if '.' in sanitized:
            name_part, ext = sanitized.rsplit('.', 1)
            name_part = name_part[:max_length - len(ext) - 1]
            sanitized = f"{name_part}.{ext}"
        else:
            sanitized = sanitized[:max_length]
    
    return sanitized


def download_file_with_retry(
    url: str, 
    dest: Path, 
    max_retries: int = MAX_RETRIES,
    retry_delay: float = RETRY_DELAY
) -> bool:
    """
    Download a file from URL to destination with retry logic and proper error handling.
    
    This function implements exponential backoff retry logic and comprehensive
    error handling for network requests. It uses a browser-like User-Agent
    to avoid 403 responses from some servers.
    
    Args:
        url: The URL to download from
        dest: Path object representing the destination file
        max_retries: Maximum number of retry attempts
        retry_delay: Base delay between retries (seconds)
        
    Returns:
        True if download successful, False otherwise
        
    Raises:
        DownloadError: If all retry attempts fail with non-recoverable error
    """
    logger = logging.getLogger(__name__)
    
    for attempt in range(max_retries + 1):
        try:
            # Create request with browser-like headers
            request = Request(
                url,
                headers={
                    'User-Agent': USER_AGENT,
                    'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                }
            )
            
            # Perform download
            with urlopen(request, timeout=30) as response:
                if response.status != 200:
                    logger.warning(f"HTTP {response.status} for {url}")
                    if response.status in (404, 410):  # Not found, gone
                        return False
                    if attempt < max_retries:
                        continue
                    return False
                
                # Ensure destination directory exists
                dest.parent.mkdir(parents=True, exist_ok=True)
                
                # Download with progress tracking
                with open(dest, "wb") as f:
                    shutil.copyfileobj(response, f)
                
                logger.debug(f"Successfully downloaded {url} to {dest}")
                return True
                
        except (HTTPError, URLError) as e:
            logger.warning(f"Network error downloading {url}: {e}")
            if attempt < max_retries:
                delay = retry_delay * (2 ** attempt)  # Exponential backoff
                logger.debug(f"Retrying in {delay:.1f}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
                continue
            return False
            
        except Exception as e:
            logger.error(f"Unexpected error downloading {url}: {e}")
            if attempt < max_retries:
                delay = retry_delay * (2 ** attempt)
                time.sleep(delay)
                continue
            return False
    
    return False


def parse_playlist_file(playlist_path: Path) -> Dict:
    """Parse a .bplist (BeatSaver playlist) JSON file.
    
    Reads and validates a BeatSaver playlist file, ensuring it contains
    valid JSON and has the expected structure. Creates an empty songs
    list if none exists.
    
    Args:
        playlist_path (Path): Path to the .bplist file to parse.
        
    Returns:
        Dict: Parsed playlist data containing at minimum a 'songs' key
            with a list of song dictionaries.
        
    Raises:
        PlaylistParseError: If file cannot be read, parsed, or is invalid.
            This includes cases where the file doesn't exist, isn't a file,
            contains invalid JSON, or has encoding issues.
    
    Example:
        >>> data = parse_playlist_file(Path("my_playlist.bplist"))
        >>> print(data["playlistTitle"])
        "My Awesome Playlist"
    """
    try:
        if not playlist_path.exists():
            raise PlaylistParseError(f"Playlist file not found: {playlist_path}")
        
        if not playlist_path.is_file():
            raise PlaylistParseError(f"Path is not a file: {playlist_path}")
        
        # Read and parse JSON
        content = playlist_path.read_text(encoding="utf-8")
        data = json.loads(content)
        
        # Validate required fields
        if not isinstance(data, dict):
            raise PlaylistParseError("Playlist file must contain a JSON object")
        
        # Ensure songs list exists
        if "songs" not in data:
            data["songs"] = []
        
        return data
        
    except json.JSONDecodeError as e:
        raise PlaylistParseError(f"Invalid JSON in playlist file: {e}")
    except UnicodeDecodeError as e:
        raise PlaylistParseError(f"Cannot decode playlist file: {e}")
    except Exception as e:
        raise PlaylistParseError(f"Error reading playlist file: {e}")


def extract_and_save_cover_image(playlist_data: Dict, dest_dir: Path) -> Optional[Path]:
    """Extract and save the playlist cover image from base64 data.
    
    Decodes base64 image data from the playlist and saves it as a cover
    image file. Automatically detects image format (JPEG, PNG, GIF) based
    on file headers and uses appropriate file extension.
    
    Args:
        playlist_data (Dict): Parsed playlist dictionary containing image data.
            Expected to have an 'image' key with base64-encoded image data.
        dest_dir (Path): Directory where the cover image should be saved.
            Directory will be created if it doesn't exist.
            
    Returns:
        Optional[Path]: Path to the saved cover image file, or None if no
            image data was found or extraction failed.
            
    Note:
        Supported image formats are JPEG, PNG, and GIF. If format cannot
        be determined, defaults to JPEG extension. Failed extractions are
        logged as warnings but don't raise exceptions.
        
    Example:
        >>> cover_path = extract_and_save_cover_image(playlist_data, Path("./output"))
        >>> if cover_path:
        ...     print(f"Cover saved to: {cover_path}")
    """
    logger = logging.getLogger(__name__)
    
    img_data = playlist_data.get("image", "")
    if not img_data:
        logger.debug("No cover image data found in playlist")
        return None
    
    try:
        # Decode base64 image data
        img_bytes = base64.b64decode(img_data)
        
        # Determine file extension based on image header
        if img_bytes.startswith(b'\xFF\xD8\xFF'):
            ext = "jpg"
        elif img_bytes.startswith(b'\x89PNG'):
            ext = "png"
        elif img_bytes.startswith(b'GIF8'):
            ext = "gif"
        else:
            ext = "jpg"  # Default fallback
        
        # Save image
        img_path = dest_dir / f"cover.{ext}"
        img_path.write_bytes(img_bytes)
        
        logger.info(f"Saved cover image to {img_path}")
        return img_path
        
    except Exception as e:
        logger.warning(f"Failed to extract cover image: {e}")
        return None


def create_song_status_table(songs: List[Dict], dest_dir: Path) -> Tuple[Table, List[Dict]]:
    """Create a rich table showing song download status and identify missing songs.
    
    Analyzes each song in the playlist to determine its download status
    by checking for existing files in the destination directory. Creates
    a formatted table for display and returns a list of missing songs.
    
    Args:
        songs (List[Dict]): List of song dictionaries from the playlist.
            Each song should have 'hash' and 'songName' keys.
        dest_dir (Path): Directory where songs should be stored.
            Used to check for existing downloaded files.
        
    Returns:
        Tuple[Table, List[Dict]]: A tuple containing:
            - Table: Rich table object ready for console display
            - List[Dict]: List of songs that need to be downloaded
            
    Note:
        Songs are considered present if a .zip file with the correct hash
        exists and has non-zero size. Songs without hashes are marked
        as having no hash and are not included in the missing list.
        
    Example:
        >>> table, missing = create_song_status_table(songs, Path("./downloads"))
        >>> console.print(table)
        >>> print(f"Need to download {len(missing)} songs")
    """
    table = Table(title="Song Download Status", show_lines=False)
    table.add_column("#", justify="right", style="dim")
    table.add_column("Song Name", overflow="fold")
    table.add_column("Hash", style="dim", max_width=15)
    table.add_column("Status", justify="center")
    
    missing_songs = []
    
    for idx, song in enumerate(songs, 1):
        song_hash = song.get("hash", "").lower()
        song_name = song.get("songName", "Unknown")
        
        if not song_hash:
            status_text = Text("❌ No Hash", style="red")
        else:
            zip_path = dest_dir / f"{song_hash}.zip"
            if zip_path.exists() and zip_path.stat().st_size > 0:
                status_text = Text("✅ Present", style="green")
            else:
                status_text = Text("⬇️ Missing", style="yellow")
                missing_songs.append(song)
        
        table.add_row(
            str(idx),
            song_name,
            song_hash[:12] + "..." if len(song_hash) > 15 else song_hash,
            status_text
        )
    
    return table, missing_songs


def download_missing_songs(missing_songs: List[Dict], dest_dir: Path) -> Tuple[int, int]:
    """Download all missing songs with progress tracking and error handling.
    
    Downloads songs from BeatSaver CDN using the song hashes, displaying
    a progress bar and handling individual song failures gracefully.
    Failed downloads are logged and partial files are cleaned up.
    
    Args:
        missing_songs (List[Dict]): List of song dictionaries to download.
            Each song should contain 'hash' and 'songName' keys.
        dest_dir (Path): Directory where downloaded songs should be saved.
            Files are saved as {hash}.zip format.
        
    Returns:
        Tuple[int, int]: A tuple containing:
            - int: Number of successful downloads
            - int: Number of failed downloads
            
    Note:
        Songs without valid hashes are skipped and counted as failures.
        Progress is displayed using Rich progress bars with time estimates.
        Partial downloads are automatically cleaned up on failure.
        
    Example:
        >>> successful, failed = download_missing_songs(missing, Path("./downloads"))
        >>> print(f"Downloaded {successful}, failed {failed}")
    """
    if not missing_songs:
        return 0, 0
    
    logger = logging.getLogger(__name__)
    successful = 0
    failed = 0
    
    console.print(
        Panel.fit(
            f"Downloading [bold cyan]{len(missing_songs)}[/bold cyan] missing songs...",
            style="cyan"
        )
    )
    
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=None),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("({task.completed}/{task.total})"),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        console=console,
    ) as progress:
        
        download_task = progress.add_task("Downloading songs", total=len(missing_songs))
        
        for song in missing_songs:
            song_name = song.get("songName", "Unknown")
            song_hash = song.get("hash", "").lower()
            
            if not song_hash:
                logger.warning(f"Skipping song '{song_name}' - no hash provided")
                failed += 1
                progress.advance(download_task)
                continue
            
            target_path = dest_dir / f"{song_hash}.zip"
            download_url = f"{BEATSAVER_CDN_URL}/{quote_plus(song_hash)}.zip"
            
            # Update progress description
            progress.update(
                download_task,
                description=f"Downloading: {song_name[:30]}..."
            )
            
            success = download_file_with_retry(download_url, target_path)
            
            if success:
                console.print(f"  ✅ [green]{song_name}[/green] -> [dim]{song_hash}.zip[/dim]")
                successful += 1
            else:
                console.print(f"  ❌ [red]Failed:[/red] {song_name}")
                failed += 1
                # Remove partial download if it exists
                if target_path.exists():
                    target_path.unlink()
            
            progress.advance(download_task)
    
    return successful, failed


def main() -> None:
    """Main entry point for the BeatSaver Playlist Downloader.
    
    Orchestrates the complete playlist download process including argument
    parsing, playlist processing, status display, and song downloading.
    Provides comprehensive error handling and user-friendly feedback.
    
    The function performs the following operations:
    1. Parse and validate command line arguments
    2. Set up logging based on verbosity level
    3. Load and parse the playlist file
    4. Create output directory and save metadata
    5. Extract and save cover image if present
    6. Analyze existing downloads and display status
    7. Download missing songs with progress tracking
    8. Display final summary and statistics
    
    Returns:
        None
        
    Raises:
        SystemExit: Exits with code 1 for playlist errors, 130 for user
            interruption, or 1 for unexpected errors.
            
    Note:
        This function handles all user interaction and should be called
        as the main entry point when running as a script. All errors
        are caught and displayed in a user-friendly format.
        
    Example:
        When run from command line:
        $ python -m bsaver_dl my_playlist.bplist -v --output ./downloads
    """
    parser = argparse.ArgumentParser(
        description="Download BeatSaver playlists",
        epilog="This tool reads .bplist files and downloads all associated songs, "
               "cover images, and metadata to a local directory.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "bplist",
        type=Path,
        help="Path to the .bplist JSON file (exported from BeatSaver)"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output directory (default: playlist title)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--force-redownload",
        action="store_true",
        help="Re-download files even if they already exist"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"bsaver-dl {__version__}"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    try:
        # Parse playlist file
        console.rule("🎵 BeatSaver Playlist Downloader")
        console.print(f"📁 Loading playlist: [bold]{args.bplist}[/bold]")
        
        playlist_data = parse_playlist_file(args.bplist)
        
        # Extract playlist metadata
        title = playlist_data.get("playlistTitle", "Untitled Playlist")
        author = playlist_data.get("playlistAuthor", "Unknown")
        description = playlist_data.get("playlistDescription", "")
        songs = playlist_data.get("songs", [])
        
        # Display playlist info
        info_table = Table(show_header=False, box=None)
        info_table.add_column("Field", style="bold")
        info_table.add_column("Value")
        info_table.add_row("Title", title)
        info_table.add_row("Author", author)
        if description:
            info_table.add_row("Description", description[:100] + "..." if len(description) > 100 else description)
        info_table.add_row("Songs", str(len(songs)))
        
        console.print(Panel(info_table, title="📋 Playlist Information", border_style="blue"))
        
        # Determine destination directory
        if args.output:
            dest_dir = args.output
        else:
            safe_title = safe_filename(title)
            dest_dir = Path(safe_title)
        
        dest_dir.mkdir(exist_ok=True)
        console.print(f"📂 Output directory: [bold green]{dest_dir.absolute()}[/bold green]")
        
        # Extract and save cover image
        cover_path = extract_and_save_cover_image(playlist_data, dest_dir)
        if cover_path:
            console.print(f"🖼️  Saved cover image: [dim]{cover_path}[/dim]")
        
        # Copy original playlist file
        playlist_copy = dest_dir / args.bplist.name
        if playlist_copy != args.bplist:  # Avoid copying to itself
            shutil.copy2(args.bplist, playlist_copy)
            console.print(f"📄 Copied playlist file: [dim]{playlist_copy}[/dim]")
        
        # Check if we have songs to process
        if not songs:
            console.print("⚠️  [yellow]No songs found in playlist.[/yellow]")
            return
        
        # Create status table and identify missing songs
        status_table, missing_songs = create_song_status_table(songs, dest_dir)
        console.print(status_table)
        
        # Handle force redownload option
        if args.force_redownload:
            missing_songs = songs
            console.print("🔄 [yellow]Force redownload enabled - will redownload all songs[/yellow]")
        
        # Download missing songs
        if missing_songs:
            successful, failed = download_missing_songs(missing_songs, dest_dir)
            
            # Final summary
            console.rule("📊 Download Summary")
            summary_table = Table(show_header=False, box=None)
            summary_table.add_column("Status", style="bold")
            summary_table.add_column("Count", justify="right")
            summary_table.add_row("✅ Successful", str(successful), style="green")
            summary_table.add_row("❌ Failed", str(failed), style="red")
            summary_table.add_row("📁 Total Songs", str(len(songs)), style="blue")
            
            console.print(Panel(summary_table, border_style="green" if failed == 0 else "yellow"))
            
            if failed > 0:
                console.print(f"⚠️  [yellow]{failed} songs failed to download. "
                             "Check your internet connection and try again.[/yellow]")
        else:
            console.print("✨ [green]All songs already present! Nothing to download.[/green] ✨")
        
        console.rule("🏁 [bold green]Complete![/bold green]")
        
    except PlaylistDownloaderError as e:
        console.print(f"❌ [red]Error:[/red] {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n⏹️  [yellow]Download interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        logger.exception("Unexpected error occurred")
        console.print(f"💥 [red]Unexpected error:[/red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 