# Contributing to BeatSaver Playlist Downloader

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-cristiangauma/bsaver-dl.git
   cd bsaver-dl
   ```
3. **Set up the development environment**:
   ```bash
   ./bsaver-dl --install
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

## 🛠️ Development Setup

The project uses:
- **Python 3.7+** (required)
- **Rich** for CLI interface
- **Virtual environment** for dependency isolation

## 📝 Code Style

- Follow **PEP 8** style guidelines
- Use **type hints** where appropriate
- Write **comprehensive docstrings** following PEP 257
- Keep functions focused and well-documented

## 🧪 Testing

Before submitting changes:
1. **Test the installation process**:
   ```bash
   ./bsaver-dl --clean
   ./bsaver-dl --install
   ```
2. **Test basic functionality**:
   ```bash
   ./bsaver-dl --help
   ./bsaver-dl --help-download
   ```
3. **Test with a real playlist** if possible

## 📋 Pull Request Process

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. **Make your changes** with clear, focused commits
3. **Update documentation** if needed
4. **Test thoroughly** on your platform
5. **Submit a pull request** with:
   - Clear description of changes
   - Why the change is needed
   - How to test the changes

## 🐛 Bug Reports

When reporting bugs, please include:
- **Operating system** and version
- **Python version**
- **Complete error message** or output
- **Steps to reproduce** the issue
- **Playlist file** if relevant (anonymized if needed)

## 💡 Feature Requests

For new features:
- **Describe the use case** clearly
- **Explain why** it would be valuable
- **Consider implementation complexity**
- **Check existing issues** first

## 📚 Documentation

Help improve documentation by:
- Fixing typos or unclear explanations
- Adding examples or use cases
- Improving installation instructions
- Updating help text

## 🤝 Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help newcomers learn and contribute
- Keep discussions on-topic

## 📞 Questions?

- **Open an issue** for bugs or feature requests
- **Start a discussion** for questions or ideas
- **Check existing issues** before creating new ones

Thank you for contributing! 🎵 