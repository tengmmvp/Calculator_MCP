#!/bin/bash

# Calculator MCP Server Development Setup Script
# This script sets up the development environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "🔧 Calculator MCP Server Development Setup"
echo "=========================================="

# Check Python version
print_info "Checking Python version..."
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
print_info "Found Python $python_version"

# Check if we have a suitable Python version
if python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"; then
    print_success "Python version is compatible (>= 3.9)"
else
    print_error "Python 3.9 or higher is required. Found: $python_version"
    exit 1
fi

# Create virtual environment
print_info "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_info "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
print_info "Installing dependencies..."
pip install -r requirements.txt

# Install development dependencies
print_info "Installing development dependencies..."
pip install pytest pytest-cov pytest-asyncio black flake8 bandit safety mypy

# Install pre-commit hooks (optional)
if command -v pre-commit &> /dev/null; then
    print_info "Installing pre-commit hooks..."
    pre-commit install || print_warning "Pre-commit not configured"
fi

# Make scripts executable
print_info "Making scripts executable..."
chmod +x scripts/*.sh

# Create basic development configuration files
print_info "Creating development configuration files..."

# Create pytest.ini if it doesn't exist
if [ ! -f "pytest.ini" ]; then
    cat > pytest.ini << 'EOF'
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --verbose
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=src
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=80
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests
    mcp_compliance: MCP compliance tests
EOF
    print_success "Created pytest.ini"
fi

# Create pyproject.toml if it doesn't exist
if [ ! -f "pyproject.toml" ]; then
    cat > pyproject.toml << 'EOF'
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "calculator-mcp-server"
version = "1.0.0"
description = "A complete Model Context Protocol (MCP) compliant mathematical calculation server"
readme = "README.md"
license = {text = "MIT"}
authors = [
    {name = "Calculator MCP Team", email = "admin@tengmmvp.cn"}
]
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Scientific/Engineering :: Mathematics",
    "Topic :: Software Development :: Libraries :: Python Modules",
]
requires-python = ">=3.9"
dependencies = [
    "fastmcp>=2.13.0",
    "mcp>=1.22.0",
    "pydantic>=2.11.7",
]

[project.optional-dependencies]
dev = [
    "pytest>=6.0",
    "pytest-asyncio>=0.18",
    "pytest-cov>=4.0",
    "black>=21.0",
    "flake8>=3.8",
    "bandit>=1.7",
    "safety>=2.0",
    "mypy>=1.0",
]
math = [
    "sympy>=1.12.0",
    "numpy>=1.24.0",
]

# [project.scripts]
# calculator-mcp-server = "server:main"

[project.urls]
Homepage = "https://github.com/tengmmvp/Calculator_MCP"
Documentation = "https://github.com/tengmmvp/Calculator_MCP#readme"
Repository = "https://github.com/tengmmvp/Calculator_MCP"
"Bug Tracker" = "https://github.com/tengmmvp/Calculator_MCP/issues"

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-dir]
"" = "src"

[tool.black]
line-length = 88
target-version = ['py39']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''

[tool.flake8]
max-line-length = 88
extend-ignore = ["E203", "W503"]
exclude = [
    ".git",
    "__pycache__",
    "build",
    "dist",
    ".venv",
    ".eggs",
    "*.egg-info",
]

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

[[tool.mypy.overrides]]
module = [
    "fastmcp.*",
    "mcp.*",
]
ignore_missing_imports = true

[tool.coverage.run]
source = ["src"]
omit = [
    "*/tests/*",
    "*/test_*",
    "setup.py",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
show_missing = true
precision = 2
EOF
    print_success "Created pyproject.toml"
fi

# Create basic test structure
print_info "Creating basic test structure..."
mkdir -p tests
if [ ! -f "tests/__init__.py" ]; then
    touch tests/__init__.py
fi

if [ ! -f "tests/conftest.py" ]; then
    cat > tests/conftest.py << 'EOF'
"""
pytest configuration and fixtures for Calculator MCP Server tests.
"""

import asyncio
from typing import Any, Dict

import pytest


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_numbers():
    """Sample numbers for testing mathematical operations."""
    return [1, 2, 3, 4, 5]


@pytest.fixture
def sample_calculation_args():
    """Sample calculation arguments for batch operations."""
    return [
        {"tool": "add", "args": {"numbers": [1, 2, 3]}},
        {"tool": "multiply", "args": {"numbers": [2, 3]}},
        {"tool": "divide", "args": {"numerator": 10, "denominator": 2}},
    ]
EOF
    print_success "Created tests/conftest.py"
fi

# Create .env.example if it doesn't exist
if [ ! -f ".env.example" ]; then
    cat > .env.example << 'EOF'
# Calculator MCP Server Environment Variables

# Development settings
DEBUG=false
LOG_LEVEL=INFO

# MCP Server settings
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8080

# Optional: External service configurations
# OPENAI_API_KEY=your_openai_api_key_here
# ANTHROPIC_API_KEY=your_anthropic_api_key_here
EOF
    print_success "Created .env.example"
fi

print_success "Development environment setup completed!"
echo
print_info "Next steps:"
echo "  1. Activate the virtual environment: source venv/bin/activate"
echo "  2. Copy .env.example to .env and configure as needed"
echo "  3. Run the server: python src/server.py"
echo "  4. Run tests: pytest"
echo "  5. Format code: black src/"
echo "  6. Lint code: flake8 src/"
echo
print_info "For development commands, see: ./scripts/release.sh --help"