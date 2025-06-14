# BeatSaver Playlist Downloader

🎵 A comprehensive CLI tool for downloading BeatSaver playlists. This tool reads `.bplist` files (exported from BeatSaver), extracts metadata, downloads cover images, and fetches all associated song files (.zip) from BeatSaver's CDN.

## Features

- 🎵 **Rich CLI Interface**: Beautiful progress bars, status tables, and colored output
- 📁 **Automatic Organization**: Creates organized directories with playlist metadata
- 🖼️ **Cover Image Extraction**: Automatically extracts and saves playlist cover images
- ⚡ **Resume Downloads**: Skips already downloaded files (smart resume capability)
- 🔄 **Retry Logic**: Robust error handling with exponential backoff retry
- 🌍 **Cross-Platform**: Works on Windows, macOS, and Linux
- 📊 **Detailed Reporting**: Shows download status and statistics
- 🚀 **Fast Downloads**: Parallel processing and optimized network requests

## Quick Start

### One Command - Everything Automatic! 🚀

```bash
# Download a playlist (auto-installs if needed)
./bsaver-dl your_playlist.bplist

# Or using Python
python3 bsaver-dl your_playlist.bplist

# Show help
./bsaver-dl --help
python3 bsaver-dl --help

# Force install/reinstall
./bsaver-dl --install

# Clean up virtual environment
./bsaver-dl --clean
```

**That's it!** The script automatically:
- ✅ Detects if installation is needed
- ✅ Creates virtual environment if missing  
- ✅ Installs all dependencies
- ✅ Runs your command

**No manual installation steps required!**

## Advanced Usage

```bash
# Custom output directory
./bsaver-dl playlist.bplist -o /path/to/output

# Verbose logging
./bsaver-dl playlist.bplist -v  

# Force re-download all files
./bsaver-dl playlist.bplist --force-redownload

# Combine options
./bsaver-dl playlist.bplist -o "./downloads" -v

# Management commands
./bsaver-dl --install                    # Force install/reinstall
./bsaver-dl --clean                      # Clean up virtual environment
./bsaver-dl --help                       # Show general help
./bsaver-dl --help-download              # Show download options
```

## Installation & Usage

### 🚀 One Command - Everything Automatic!

```bash
# Download a playlist (auto-installs if needed)
./bsaver-dl your_playlist.bplist

# Or using Python
python3 bsaver-dl your_playlist.bplist

# Show help
./bsaver-dl --help
python3 bsaver-dl --help
```

**The smart `bsaver-dl` script automatically:**
- ✅ Detects if installation is needed
- ✅ Creates virtual environment if missing  
- ✅ Installs all dependencies and package
- ✅ Runs your command

**No manual installation steps required!**

### Direct Manual Installation (Alternative)

If you prefer to install manually:

```bash
# Install dependencies and package
python3 setup/install.py

# Clean up when done
python3 setup/install.py --clean
```

## Usage

### Basic Usage

**Simply run the smart script - it handles everything automatically:**

```bash
# Console script (recommended)
./bsaver-dl path/to/your/playlist.bplist
python3 bsaver-dl path/to/your/playlist.bplist

# Or as a Python module (if you want direct module access)
python -m bsaver_dl path/to/your/playlist.bplist
```

**Note:** The first time you run it, it will automatically install dependencies. Subsequent runs are instant!

### Advanced Usage Examples

```bash
# Specify custom output directory
./bsaver-dl playlist.bplist -o /path/to/output
python3 bsaver-dl playlist.bplist -o /path/to/output

# Enable verbose logging
./bsaver-dl playlist.bplist -v
python3 bsaver-dl playlist.bplist -v

# Force re-download all files
./bsaver-dl playlist.bplist --force-redownload
python3 bsaver-dl playlist.bplist --force-redownload

# Combine options
./bsaver-dl playlist.bplist -o "./downloads" -v
python3 bsaver-dl playlist.bplist -o "./downloads" -v

# Management commands
./bsaver-dl --install                    # Force install/reinstall
./bsaver-dl --clean                      # Clean up virtual environment
./bsaver-dl --help                       # Show general help
./bsaver-dl --help-download              # Show detailed download options
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `bplist` | Path to the .bplist JSON file (required) |
| `-o, --output` | Custom output directory (default: playlist title) |
| `-v, --verbose` | Enable detailed logging output |
| `--force-redownload` | Re-download files even if they already exist |
| `--install` | Force install/reinstall virtual environment and dependencies |
| `--clean` | Remove virtual environment and clean up |
| `--help` | Show general help message |
| `--help-download` | Show detailed download options and exit |

## How to Export Playlists from BeatSaver

1. Open BeatSaver
2. Go to the Playlists section
3. Select the playlist you want to download
4. Click the export button (usually a share or download icon)
5. Save the `.bplist` file to your computer
6. Use this tool to download all songs in the playlist

## Output Structure

The tool creates a directory structure like this:

```
Playlist Name/
├── cover.jpg                    # Playlist cover image
├── playlist.bplist             # Original playlist file
├── hash1.zip                   # Song files
├── hash2.zip
└── ...
```

## Features in Detail

### Smart Resume
- Automatically skips files that are already downloaded
- Checks file integrity (non-zero size)
- Only downloads missing or corrupted files

### Error Handling
- Exponential backoff retry for network errors
- Graceful handling of missing songs
- Detailed error reporting with suggestions

### Cross-Platform Compatibility
- Safe filename sanitization for all operating systems
- Unicode support for international playlist names
- Path handling works on Windows, macOS, and Linux

## Troubleshooting

### Common Issues

**"rich library not found"**
```bash
pip install rich
```

**"Permission denied" errors**
- Make sure you have write permissions to the output directory
- Try running with a different output directory: `-o ~/Downloads/playlists`

**Songs failing to download**
- Check your internet connection
- Some songs may have been removed from BeatSaver
- Try again later as it might be a temporary server issue

**Playlist file not found**
- Make sure the path to your .bplist file is correct
- Use quotes around paths with spaces: `"My Playlist.bplist"`

### Getting Help

If you encounter issues:

1. Run with verbose logging: `-v` flag
2. Check the error messages for specific guidance
3. Ensure you have the latest version of the tool
4. Verify your .bplist file is valid JSON

## Development

### Setting up Development Environment

```bash
# Clone and setup
git clone https://github.com/cristiangauma/bsaver-dl.git
cd bsaver-dl

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r setup/requirements.txt

# Install development dependencies (optional)
pip install pytest black flake8
```

### Code Structure

- `bsaver_dl/` - Main package directory
  - `main.py` - Core application logic
  - `__init__.py` - Package initialization
  - `__main__.py` - Entry point for module execution
- `setup/` - Setup files (hidden from root)
  - `install.py` - Cross-platform installer
  - `requirements.txt` - Python dependencies
  - `setup.py` - Package setup

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Project Structure

```
bsaver-dl/
├── bsaver_dl/                    # Main package
│   ├── __init__.py               # Package initialization
│   ├── __main__.py              # Entry point for python -m
│   └── main.py                  # Core application logic
├── setup/                       # Setup files (hidden from root)
│   ├── install.py              # Cross-platform installer
│   ├── requirements.txt        # Dependencies
│   └── setup.py               # Package setup
├── bsaver-dl                    # Smart entry point script
├── README.md                    # This comprehensive documentation
└── LICENSE                     # MIT License
```

## Manual Cleanup

```bash
# Clean up using the built-in command (recommended)
./bsaver-dl --clean

# Or remove virtual environment manually
rm -rf venv

# Or use the installer directly
python3 setup/install.py --clean
```

## Changelog

### v2.0.0 (Current)
- Complete rewrite with improved architecture
- Added comprehensive error handling and retry logic
- Enhanced CLI interface with Rich library
- Added verbose logging and better status reporting
- Improved cross-platform filename handling
- Added force re-download option
- Better playlist metadata extraction
- Smart auto-install entry point script

### v1.0.0 (Original)
- Basic playlist downloading functionality
- Simple CLI interface
- Cover image extraction

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- BeatSaver community for the amazing custom songs
- BeatSaver for hosting the song database
- Rich library for the beautiful CLI interface
- This project was developed with the assistance of **Cursor** - AI-powered code editor that made this comprehensive tool possible through intelligent code generation and collaboration
