# Contributing to Solar Panel Detection

Thank you for your interest in contributing to the Solar Panel Detection project!

## How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/solar-panel-detection.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest

# Run linting
flake8 src/
black src/ --check
```

## Code Style

- Follow PEP 8
- Use type hints where applicable
- Add docstrings to all functions and classes
- Write unit tests for new features

## Reporting Issues

Please use the issue templates for bug reports and feature requests.
