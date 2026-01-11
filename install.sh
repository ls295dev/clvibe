#!/bin/bash
# clvibe installation script
# Installs clvibe as a global command

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# Check if Python 3 is installed
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        print_success "Python 3 found: $PYTHON_VERSION"
        return 0
    else
        print_error "Python 3 is not installed"
        echo "Please install Python 3.6 or higher to use clvibe"
        return 1
    fi
}

# Install clvibe
install_clvibe() {
    local OS=$(detect_os)
    
    echo ""
    echo "╔════════════════════════════════════════╗"
    echo "║     clvibe Installation Script         ║"
    echo "║  CLI Game Manager for AI Games         ║"
    echo "╚════════════════════════════════════════╝"
    echo ""
    
    print_info "Detected OS: $OS"
    echo ""
    
    # Check Python
    if ! check_python; then
        exit 1
    fi
    
    # Determine installation directory
    if [[ "$OS" == "windows" ]]; then
        INSTALL_DIR="$HOME/AppData/Local/clvibe"
        BIN_DIR="$HOME/AppData/Local/bin"
    else
        INSTALL_DIR="$HOME/.local/share/clvibe"
        BIN_DIR="$HOME/.local/bin"
    fi
    
    print_info "Installation directory: $INSTALL_DIR"
    print_info "Binary directory: $BIN_DIR"
    echo ""
    
    # Create directories
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$BIN_DIR"
    
    # Download or copy clvibe.py
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    if [[ -f "$SCRIPT_DIR/clvibe.py" ]]; then
        print_info "Copying clvibe.py..."
        cp "$SCRIPT_DIR/clvibe.py" "$INSTALL_DIR/clvibe.py"
        chmod +x "$INSTALL_DIR/clvibe.py"
        print_success "Copied clvibe.py"
    else
        print_error "clvibe.py not found in current directory"
        echo "Please ensure clvibe.py is in the same directory as this install script"
        exit 1
    fi
    
    # Create launcher script
    print_info "Creating launcher script..."
    
    if [[ "$OS" == "windows" ]]; then
        # Create batch file for Windows
        cat > "$BIN_DIR/clvibe.bat" << EOF
@echo off
python3 "$INSTALL_DIR\\clvibe.py" %*
EOF
        print_success "Created launcher: $BIN_DIR/clvibe.bat"
    else
        # Create shell script for Unix-like systems
        cat > "$BIN_DIR/clvibe" << EOF
#!/bin/bash
python3 "$INSTALL_DIR/clvibe.py" "\$@"
EOF
        chmod +x "$BIN_DIR/clvibe"
        print_success "Created launcher: $BIN_DIR/clvibe"
    fi
    
    echo ""
    
    # Check if BIN_DIR is in PATH
    if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
        print_warning "Warning: $BIN_DIR is not in your PATH"
        echo ""
        echo "To use 'clvibe' command, add this line to your shell configuration:"
        echo ""
        
        if [[ "$OS" == "macos" ]] || [[ "$OS" == "linux" ]]; then
            if [[ -f "$HOME/.zshrc" ]]; then
                SHELL_CONFIG="~/.zshrc"
            elif [[ -f "$HOME/.bashrc" ]]; then
                SHELL_CONFIG="~/.bashrc"
            else
                SHELL_CONFIG="~/.profile"
            fi
            
            echo "  export PATH=\"\$PATH:$BIN_DIR\""
            echo ""
            echo "Run this command to add it automatically:"
            echo "  echo 'export PATH=\"\$PATH:$BIN_DIR\"' >> $SHELL_CONFIG"
            echo ""
            echo "Then reload your shell:"
            echo "  source $SHELL_CONFIG"
        elif [[ "$OS" == "windows" ]]; then
            echo "  Add $BIN_DIR to your system PATH in Environment Variables"
        fi
        
        echo ""
        print_info "Or run directly: $BIN_DIR/clvibe"
    else
        print_success "$BIN_DIR is already in PATH"
    fi
    
    echo ""
    print_success "Installation complete!"
    echo ""
    echo "Quick start:"
    echo "  clvibe check              # Check available language runtimes"
    echo "  clvibe install <path>     # Install a game"
    echo "  clvibe list               # List installed games"
    echo "  clvibe play <game>        # Play a game"
    echo ""
    print_info "Configuration stored in: ~/.clvibe/"
    echo ""
}

# Uninstall clvibe
uninstall_clvibe() {
    local OS=$(detect_os)
    
    echo ""
    print_warning "Uninstalling clvibe..."
    echo ""
    
    if [[ "$OS" == "windows" ]]; then
        INSTALL_DIR="$HOME/AppData/Local/clvibe"
        BIN_DIR="$HOME/AppData/Local/bin"
        LAUNCHER="$BIN_DIR/clvibe.bat"
    else
        INSTALL_DIR="$HOME/.local/share/clvibe"
        BIN_DIR="$HOME/.local/bin"
        LAUNCHER="$BIN_DIR/clvibe"
    fi
    
    # Remove launcher
    if [[ -f "$LAUNCHER" ]]; then
        rm "$LAUNCHER"
        print_success "Removed launcher"
    fi
    
    # Remove installation directory
    if [[ -d "$INSTALL_DIR" ]]; then
        rm -rf "$INSTALL_DIR"
        print_success "Removed installation directory"
    fi
    
    # Ask about game data
    if [[ -d "$HOME/.clvibe" ]]; then
        echo ""
        read -p "Remove game data from ~/.clvibe? [y/N]: " -n 1 -r
        echo ""clivibe/install.sh
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$HOME/.clvibe"
            print_success "Removed game data"
        else
            print_info "Game data preserved in ~/.clvibe"
        fi
    fi
    
    echo ""
    print_success "Uninstallation complete"
    echo ""
}

# Main script
main() {
    if [[ "$1" == "uninstall" ]]; then
        uninstall_clvibe
    elif [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
        echo "Usage: $0 [uninstall]"
        echo ""
        echo "Install clvibe as a global command"
        echo ""
        echo "Options:"
        echo "  uninstall    Remove clvibe from your system"
        echo "  --help, -h   Show this help message"
    else
        install_clvibe
    fi
}

main "$@"