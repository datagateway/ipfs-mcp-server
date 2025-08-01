# Contributing to IPFS MCP Server

We welcome contributions! This document guides you through the process of contributing to this project.

## Development Setup

1. Fork and clone the repository
2. Create a virtual environment:
   ```bash
   uv venv
   # or
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install in development mode:
   ```bash
   uv pip install -e .
   uv pip install -r requirements-dev.txt
   # or
   pip install -e .
   pip install -r requirements-dev.txt
   ```

## Making Changes

1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes

3. Run tests:
   ```bash
   pytest tests/ -v
   ```

4. Format your code:
   ```bash
   black .
   ruff check . --fix
   ```

5. Commit your changes:
   ```bash
   git add .
   git commit -m "Add your descriptive commit message"
   ```

## Pull Request Process

1. Push your branch to your fork
2. Open a pull request from your branch to `main`
3. Describe your changes in the PR description
4. Wait for review and address any feedback

## Code Style

- We use `black` for code formatting
- We use `ruff` for linting
- Follow PEP 8 guidelines
- Add type hints where possible

## Testing

- Write tests for new features
- Ensure all tests pass before submitting a PR
- Aim for good test coverage

## Documentation

- Update README.md if you change functionality
- Add docstrings to new functions and classes
- Update docs/ if you add new features
