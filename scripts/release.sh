#!/bin/bash

# Calculator MCP Server Release Script
# This script helps create a new release with proper versioning and changelog

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Function to check if we're on the main branch
check_branch() {
    local current_branch=$(git rev-parse --abbrev-ref HEAD)
    if [ "$current_branch" != "main" ]; then
        print_warning "You're not on the main branch (current: $current_branch)"
        read -p "Do you want to continue? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Release cancelled."
            exit 1
        fi
    fi
}

# Function to check if working directory is clean
check_clean() {
    if [ -n "$(git status --porcelain)" ]; then
        print_error "Working directory is not clean. Please commit or stash changes first."
        exit 1
    fi
}

# Function to get current version from git tags
get_current_version() {
    local latest_tag=$(git describe --tags --abbrev=0 2>/dev/null || echo "0.0.0")
    echo "$latest_tag"
}

# Function to validate version format
validate_version() {
    local version=$1
    if [[ ! $version =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        print_error "Invalid version format: $version"
        print_info "Version should be in format: X.Y.Z"
        exit 1
    fi
}

# Function to update version in pyproject.toml
update_version() {
    local version=$1
    print_info "Updating version to $version"

    # Update pyproject.toml if it exists
    if [ -f "pyproject.toml" ]; then
        sed -i.bak "s/version = \"[^\"]*\"/version = \"$version\"/" pyproject.toml
        rm pyproject.toml.bak
    fi

    # Update setup.py if it exists
    if [ -f "setup.py" ]; then
        sed -i.bak "s/version=\"[^\"]*\"/version=\"$version\"/" setup.py
        rm setup.py.bak
    fi

    # Update __init__.py if it contains version info
    if [ -f "src/__init__.py" ]; then
        sed -i.bak "s/__version__ = \"[^\"]*\"/__version__ = \"$version\"/" src/__init__.py 2>/dev/null || true
        rm -f src/__init__.py.bak
    fi
}

# Function to create changelog
create_changelog() {
    local version=$1
    local last_tag=$(get_current_version)

    print_info "Generating changelog since $last_tag"

    # Create changelog
    cat > CHANGELOG.md << EOF
# Changelog

## [$version] - $(date +%Y-%m-%d)

### Added
- Add your changes here

### Changed
- Add your changes here

### Fixed
- Add your changes here

### Deprecated
- Add your changes here

### Removed
- Add your changes here

### Security
- Add your changes here

---

EOF

    # If there's a previous changelog, append it
    if [ -f "CHANGELOG.md" ] && [ "$last_tag" != "0.0.0" ]; then
        # Backup existing changelog
        cp CHANGELOG.md CHANGELOG.md.bak
        # Add new version at the top
        cat > CHANGELOG.md << EOF
# Changelog

## [$version] - $(date +%Y-%m-%d)

### Added
- Version bump to $version

### Changed
- Updated dependencies and documentation

$(tail -n +2 CHANGELOG.md.bak)
EOF
        rm CHANGELOG.md.bak
    fi

    print_success "Changelog created: CHANGELOG.md"
    print_warning "Please edit CHANGELOG.md to add actual changes before committing."
}

# Function to create commit and tag
create_release_commit() {
    local version=$1

    print_info "Creating release commit"

    # Stage version files and changelog
    git add pyproject.toml setup.py src/__init__.py CHANGELOG.md 2>/dev/null || true

    # Create commit
    git commit -m "chore: Release v$version"

    # Create tag
    git tag -a "v$version" -m "Release v$version"

    print_success "Release commit and tag created"
}

# Function to push to remote
push_release() {
    local version=$1

    print_info "Pushing to remote repository"

    # Push commits
    git push origin main

    # Push tag
    git push origin "v$version"

    print_success "Release pushed to remote"
}

# Function to create GitHub release via CLI
create_github_release() {
    local version=$1

    if command -v gh &> /dev/null; then
        print_info "Creating GitHub release via CLI"

        # Read changelog
        local changelog_body=""
        if [ -f "CHANGELOG.md" ]; then
            # Extract the current version section from changelog
            changelog_body=$(sed -n "/## \[$version\]/,/^## /p" CHANGELOG.md | sed '$d')
        fi

        # Create release
        gh release create "v$version" \
            --title "Calculator MCP Server v$version" \
            --notes "$changelog_body" \
            --latest

        print_success "GitHub release created"
    else
        print_warning "GitHub CLI not found. Please create release manually at:"
        print_info "https://github.com/tengmmvp/Calculator_MCP/releases/new?tag=v$version"
    fi
}

# Main release function
main() {
    echo "🚀 Calculator MCP Server Release Script"
    echo "======================================"

    # Check prerequisites
    check_branch
    check_clean

    # Get current version
    local current_version=$(get_current_version)
    print_info "Current version: $current_version"

    # Get new version
    if [ -z "$1" ]; then
        read -p "Enter new version (e.g., 1.0.0): " version
    else
        version=$1
    fi

    # Validate version
    validate_version "$version"

    # Confirm release
    echo
    print_info "Release Summary:"
    echo "  Current version: $current_version"
    echo "  New version: $version"
    echo
    read -p "Do you want to continue with the release? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Release cancelled."
        exit 1
    fi

    # Execute release steps
    update_version "$version"
    create_changelog "$version"

    print_warning "Please review and edit CHANGELOG.md before proceeding."
    read -p "Press Enter to continue after editing changelog..."

    create_release_commit "$version"

    # Ask if user wants to push
    echo
    read -p "Do you want to push the release to remote? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        push_release "$version"
        create_github_release "$version"
    else
        print_info "Release committed locally. Push manually with:"
        print_info "  git push origin main"
        print_info "  git push origin v$version"
    fi

    print_success "Release v$version completed! 🎉"
}

# Run main function with all arguments
main "$@"