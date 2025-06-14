#!/usr/bin/env python3
"""
BeatSaver Playlist Downloader - Cross-Platform Installer

This script provides a unified installation experience across Windows, macOS, and Linux.
It creates a virtual environment, installs dependencies, and provides usage instructions.

Usage:
    python install.py              # Install dependencies
    python install.py --clean      # Remove virtual environment
    python install.py --help       # Show this help
"""

import argparse
import os
import platform
import subprocess
import sys
from pathlib import Path


class Colors:
    """ANSI color codes for cross-platform colored output.
    
    Provides ANSI escape codes for terminal colors with automatic detection
    of color support. On Windows, attempts to enable colorama for ANSI support.
    Falls back to empty strings when colors are not supported.
    
    Attributes:
        ENABLED (bool): Whether color output is supported on this platform.
        RED (str): ANSI code for red text.
        GREEN (str): ANSI code for green text.
        YELLOW (str): ANSI code for yellow text.
        BLUE (str): ANSI code for blue text.
        CYAN (str): ANSI code for cyan text.
        WHITE (str): ANSI code for white text.
        BOLD (str): ANSI code for bold text.
        END (str): ANSI code to reset formatting.
        
    Note:
        All color codes are empty strings when ENABLED is False,
        making it safe to use them unconditionally in print statements.
        
    Example:
        >>> print(f"{Colors.GREEN}Success!{Colors.END}")
        >>> print(f"{Colors.RED}Error!{Colors.END}")
    """
    if platform.system() == "Windows":
        # Try to enable ANSI colors on Windows
        try:
            import colorama
            colorama.init()
            ENABLED = True
        except ImportError:
            ENABLED = False
    else:
        ENABLED = True
    
    if ENABLED:
        RED = '\033[91m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        BLUE = '\033[94m'
        CYAN = '\033[96m'
        WHITE = '\033[97m'
        BOLD = '\033[1m'
        END = '\033[0m'
    else:
        RED = GREEN = YELLOW = BLUE = CYAN = WHITE = BOLD = END = ''


def print_colored(message, color=Colors.WHITE):
    """Print a colored message to the console.
    
    Outputs text with the specified color using ANSI escape codes.
    Automatically handles platforms that don't support colors by
    falling back to plain text output.
    
    Args:
        message (str): The message to print.
        color (str): ANSI color code from Colors class (default: Colors.WHITE).
        
    Returns:
        None
        
    Example:
        >>> print_colored("Installation complete!", Colors.GREEN)
        >>> print_colored("Warning: Check your setup", Colors.YELLOW)
    """
    print(f"{color}{message}{Colors.END}")


def print_header():
    """Print the installer header with branding.
    
    Displays a formatted header for the installation process using
    colored output when available. Provides visual separation and
    branding for the installer interface.
    
    Returns:
        None
        
    Example:
        >>> print_header()
        # Displays:
        # 🎵 BeatSaver Playlist Downloader - Cross-Platform Installer
        # ============================================================
    """
    print_colored("🎵 BeatSaver Playlist Downloader - Cross-Platform Installer", Colors.CYAN + Colors.BOLD)
    print_colored("=" * 60, Colors.CYAN)
    print()


def check_python_version():
    """Check if Python version meets minimum requirements.
    
    Verifies that the current Python interpreter is version 3.7 or higher,
    which is required for the application. Exits the program with an error
    message if the version is insufficient.
    
    Returns:
        None
        
    Raises:
        SystemExit: Exits with code 1 if Python version is below 3.7.
        
    Note:
        This function prints a success message for adequate versions
        and detailed error information for inadequate versions.
        
    Example:
        >>> check_python_version()
        ✅ Python 3.9.0 found
    """
    if sys.version_info < (3, 7):
        print_colored("❌ Error: Python 3.7 or higher is required.", Colors.RED)
        print_colored(f"   Current version: {sys.version}", Colors.YELLOW)
        sys.exit(1)
    
    print_colored(f"✅ Python {sys.version.split()[0]} found", Colors.GREEN)


def get_venv_paths():
    """Get virtual environment paths for the current platform.
    
    Determines the correct file paths for virtual environment components
    based on the operating system. Windows uses Scripts/ subdirectory
    while Unix-like systems use bin/ subdirectory.
    
    Returns:
        Tuple[Path, Path, Path, Path]: A tuple containing:
            - Path: Virtual environment directory
            - Path: Python executable path  
            - Path: Pip executable path
            - Path: Activation script path
            
    Note:
        Paths are returned regardless of whether they actually exist.
        The virtual environment directory is always named 'venv' in
        the current working directory.
        
    Example:
        >>> venv_dir, python_exe, pip_exe, activate = get_venv_paths()
        >>> print(f"Python will be at: {python_exe}")
    """
    venv_dir = Path("venv")
    
    if platform.system() == "Windows":
        python_exe = venv_dir / "Scripts" / "python.exe"
        pip_exe = venv_dir / "Scripts" / "pip.exe"
        activate_script = venv_dir / "Scripts" / "activate.bat"
    else:
        python_exe = venv_dir / "bin" / "python"
        pip_exe = venv_dir / "bin" / "pip"
        activate_script = venv_dir / "bin" / "activate"
    
    return venv_dir, python_exe, pip_exe, activate_script


def create_virtual_environment():
    """Create a virtual environment for the application.
    
    Creates a new Python virtual environment using the venv module.
    If the virtual environment already exists, returns the existing
    paths without recreating it. Exits on creation failure.
    
    Returns:
        Tuple[Path, Path, Path, Path]: Virtual environment paths
            (venv_dir, python_exe, pip_exe, activate_script).
            
    Raises:
        SystemExit: Exits with code 1 if virtual environment creation fails.
        
    Note:
        The virtual environment is created in a 'venv' subdirectory
        of the current working directory. Existing environments are
        detected and reused to avoid unnecessary recreation.
        
    Example:
        >>> paths = create_virtual_environment()
        🔧 Creating virtual environment...
        ✅ Virtual environment created
    """
    venv_dir, python_exe, pip_exe, activate_script = get_venv_paths()
    
    if venv_dir.exists():
        print_colored("📦 Virtual environment already exists", Colors.YELLOW)
        return venv_dir, python_exe, pip_exe, activate_script
    
    print_colored("🔧 Creating virtual environment...", Colors.BLUE)
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print_colored("✅ Virtual environment created", Colors.GREEN)
    except subprocess.CalledProcessError as e:
        print_colored(f"❌ Failed to create virtual environment: {e}", Colors.RED)
        sys.exit(1)
    
    return venv_dir, python_exe, pip_exe, activate_script


def install_dependencies(pip_exe):
    """Install dependencies and package using pip.
    
    Performs the complete package installation process including:
    1. Upgrading pip to the latest version
    2. Installing requirements from requirements.txt
    3. Installing the package in editable mode
    
    Args:
        pip_exe (Path): Path to the pip executable in the virtual environment.
        
    Returns:
        None
        
    Raises:
        SystemExit: Exits with code 1 if any installation step fails.
        
    Note:
        The function temporarily changes to the setup directory to install
        the package, then restores the original working directory. This
        ensures setup.py is found correctly.
        
    Example:
        >>> install_dependencies(Path("venv/bin/pip"))
        📥 Installing dependencies and package...
        ✅ Package and dependencies installed successfully
    """
    print_colored("📥 Installing dependencies and package...", Colors.BLUE)
    
    try:
        # Upgrade pip
        subprocess.run([str(pip_exe), "install", "--upgrade", "pip"], check=True)
        
        # Install requirements
        subprocess.run([str(pip_exe), "install", "-r", "setup/requirements.txt"], check=True)
        
        # Install package in editable mode (creates console scripts)
        # Change to setup directory and install from current directory where setup.py is
        original_cwd = os.getcwd()
        # Resolve the pip path before changing directories
        pip_exe_abs = pip_exe.resolve()
        try:
            os.chdir("setup")
            subprocess.run([str(pip_exe_abs), "install", "-e", "."], check=True)
        finally:
            os.chdir(original_cwd)
        
        print_colored("✅ Package and dependencies installed successfully", Colors.GREEN)
    except subprocess.CalledProcessError as e:
        print_colored(f"❌ Failed to install package: {e}", Colors.RED)
        sys.exit(1)


def print_usage_instructions():
    """Print usage instructions for the installed tool.
    
    Displays comprehensive usage information including:
    - Basic command usage examples
    - Virtual environment activation instructions
    - Platform-specific activation commands
    - Cleanup instructions
    
    Returns:
        None
        
    Note:
        Instructions are tailored to the current platform, showing
        the correct activation script path for Windows vs Unix-like systems.
        
    Example:
        >>> print_usage_instructions()
        🎉 Installation complete!
        
        You can now run the downloader with:
          bsaver-dl your_playlist.bplist
        ...
    """
    print()
    print_colored("🎉 Installation complete!", Colors.GREEN + Colors.BOLD)
    print()
    print_colored("You can now run the downloader with:", Colors.WHITE + Colors.BOLD)
    print_colored("  bsaver-dl your_playlist.bplist", Colors.CYAN)
    print()
    print_colored("Or use Python module directly:", Colors.WHITE)
    print_colored("  python -m bsaver_dl your_playlist.bplist", Colors.CYAN)
    print()
    print_colored("For help:", Colors.WHITE + Colors.BOLD)
    print_colored("  bsaver-dl --help", Colors.CYAN)
    print()
    print_colored("Note:", Colors.YELLOW + Colors.BOLD)
    print_colored("  Make sure to activate the virtual environment first:", Colors.YELLOW)
    
    if platform.system() == "Windows":
        print_colored("  venv\\Scripts\\activate", Colors.CYAN)
    else:
        print_colored("  source venv/bin/activate", Colors.CYAN)
    
    print()
    print_colored("To remove the installation:", Colors.WHITE + Colors.BOLD)
    print_colored("  python install.py --clean", Colors.CYAN)


def clean_installation():
    """Remove the virtual environment and uninstall the package.
    
    Performs complete cleanup of the installation including:
    1. Uninstalling the package from the virtual environment
    2. Removing the entire virtual environment directory
    
    Returns:
        None
        
    Raises:
        SystemExit: Exits with code 1 if cleanup fails.
        
    Note:
        Package uninstallation is attempted first but failures are ignored
        since the entire virtual environment will be removed anyway.
        This ensures cleanup works even if the package installation is corrupted.
        
    Example:
        >>> clean_installation()
        📤 Uninstalling package...
        🧹 Removing virtual environment...
        ✅ Virtual environment removed!
    """
    venv_dir, _, pip_exe, _ = get_venv_paths()
    
    if not venv_dir.exists():
        print_colored("📁 No virtual environment found", Colors.YELLOW)
        return
    
    # Try to uninstall the package first
    if pip_exe.exists():
        try:
            print_colored("📤 Uninstalling package...", Colors.BLUE)
            subprocess.run([str(pip_exe), "uninstall", "bsaver-dl", "-y"], 
                          check=True, capture_output=True)
            print_colored("✅ Package uninstalled", Colors.GREEN)
        except subprocess.CalledProcessError:
            # Package might not be installed, continue with cleanup
            pass
    
    print_colored("🧹 Removing virtual environment...", Colors.BLUE)
    try:
        import shutil
        shutil.rmtree(venv_dir)
        print_colored("✅ Virtual environment removed!", Colors.GREEN)
    except Exception as e:
        print_colored(f"❌ Failed to remove virtual environment: {e}", Colors.RED)
        sys.exit(1)


def install():
    """Main installation function.
    
    Orchestrates the complete installation process including:
    1. Displaying the installer header
    2. Checking Python version compatibility
    3. Creating the virtual environment
    4. Installing dependencies and the package
    5. Displaying usage instructions
    
    Returns:
        None
        
    Note:
        This function coordinates all installation steps and provides
        comprehensive user feedback throughout the process. Any failures
        in individual steps will cause the program to exit.
        
    Example:
        >>> install()
        🎵 BeatSaver Playlist Downloader - Cross-Platform Installer
        ============================================================
        ✅ Python 3.9.0 found
        🔧 Creating virtual environment...
        ...
    """
    print_header()
    check_python_version()
    
    venv_dir, python_exe, pip_exe, activate_script = create_virtual_environment()
    install_dependencies(pip_exe)
    print_usage_instructions()


def main():
    """Main entry point for the installation script.
    
    Parses command line arguments and routes to the appropriate function
    (install or clean). Provides comprehensive help information and
    handles both installation and cleanup workflows.
    
    Command line options:
    - No arguments: Perform installation
    - --clean: Remove virtual environment and cleanup
    - --help: Show help information
    
    Returns:
        None
        
    Example:
        Called automatically when script is executed:
        $ python install.py           # Install
        $ python install.py --clean   # Cleanup
        $ python install.py --help    # Show help
    """
    parser = argparse.ArgumentParser(
        description="BeatSaver Playlist Downloader - Cross-Platform Installer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python install.py              Install dependencies
  python install.py --clean      Remove virtual environment
  python install.py --help       Show this help
        """
    )
    
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove virtual environment"
    )
    
    args = parser.parse_args()
    
    if args.clean:
        print_header()
        clean_installation()
    else:
        install()


if __name__ == "__main__":
    main() 