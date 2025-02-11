#!/usr/bin/env python3
import argparse
import subprocess
import os
import sys
import shutil
import tempfile
from pathlib import Path

def install_oh_my_zsh_theme():
    """Install the Catppuccin theme and zsh plugins"""
    # Create directories
    themes_dir = os.path.expanduser("~/.oh-my-zsh/custom/themes")
    zsh_dir = os.path.expanduser("~/.zsh")
    plugins_dir = os.path.expanduser("~/.oh-my-zsh/custom/plugins")
    os.makedirs(themes_dir, exist_ok=True)
    os.makedirs(zsh_dir, exist_ok=True)
    os.makedirs(plugins_dir, exist_ok=True)
    
    # Clone Catppuccin theme repository
    catppuccin_dir = os.path.expanduser("~/.zsh/catppuccin-zsh-syntax-highlighting")
    if not os.path.exists(catppuccin_dir):
        print_step("Installing Catppuccin syntax highlighting theme")
        subprocess.run(["git", "clone", 
                       "https://github.com/catppuccin/zsh-syntax-highlighting.git",
                       catppuccin_dir], check=True)
        
        # Copy the mocha theme file
        subprocess.run(["cp", 
                       f"{catppuccin_dir}/themes/catppuccin_mocha-zsh-syntax-highlighting.zsh",
                       f"{zsh_dir}/catppuccin_mocha-zsh-syntax-highlighting.zsh"], check=True)

    # Install zsh-autosuggestions
    autosuggestions_dir = os.path.expanduser("~/.oh-my-zsh/custom/plugins/zsh-autosuggestions")
    if not os.path.exists(autosuggestions_dir):
        print_step("Installing zsh-autosuggestions plugin")
        subprocess.run(["git", "clone",
                       "https://github.com/zsh-users/zsh-autosuggestions.git",
                       autosuggestions_dir], check=True)

def install_oh_my_zsh():
    """Install Oh My Zsh if not already installed"""
    oh_my_zsh_dir = os.path.expanduser("~/.oh-my-zsh")
    zshrc_backup = os.path.expanduser("~/.zshrc.pre-oh-my-zsh")
    
    if not os.path.exists(oh_my_zsh_dir):
        print_step("Installing Oh My Zsh")
        
        # Backup existing .zshrc if it exists
        zshrc_path = os.path.expanduser("~/.zshrc")
        if os.path.exists(zshrc_path):
            print(f"Backing up existing .zshrc to {zshrc_backup}")
            shutil.copy2(zshrc_path, zshrc_backup)
        # First verify zsh version
        try:
            zsh_version = subprocess.check_output(["zsh", "--version"]).decode()
            print(f"Found ZSH: {zsh_version.strip()}")
        except subprocess.CalledProcessError:
            print("Error: ZSH is not properly installed")
            sys.exit(1)

        # Download the install script first for inspection
        install_script = "/tmp/install_ohmyzsh.sh"
        alternative_url = "https://install.ohmyz.sh"
        
        try:
            # Ensure wget is installed
            if not shutil.which("wget"):
                print("Installing wget...")
                subprocess.run(["sudo", "pacman", "-S", "--noconfirm", "wget"], check=True)

            print_step("Downloading Oh My Zsh installer")
            print("Downloading from:", alternative_url)
            subprocess.run(["wget", "-O", install_script, alternative_url], check=True)
            print("Download completed successfully")
        except subprocess.CalledProcessError:
            backup_url = "https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh"
            print("Failed to download from primary URL")
            print("Trying backup URL:", backup_url)
            subprocess.run(["wget", "-O", install_script, backup_url], check=True)
            print("Download completed successfully from backup URL")

        # Make the script executable
        os.chmod(install_script, 0o755)
        
        # Run the installer
        try:
            print_step("Running Oh My Zsh installer")
            subprocess.run([install_script, "--unattended"], check=True)
            
            # Remove the default .zshrc created by oh-my-zsh installation
            zshrc_path = os.path.expanduser("~/.zshrc")
            if os.path.exists(zshrc_path):
                # Compare with backup to see if it's the default oh-my-zsh config
                if os.path.exists(zshrc_backup):
                    with open(zshrc_path, 'r') as f1, open(zshrc_backup, 'r') as f2:
                        if f1.read() != f2.read():
                            print("Oh My Zsh created a new config, removing it")
                            os.remove(zshrc_path)
                        else:
                            print("Restoring original .zshrc")
                            shutil.copy2(zshrc_backup, zshrc_path)
                else:
                    os.remove(zshrc_path)
                
            # Clean up the installer
            os.remove(install_script)
        except subprocess.CalledProcessError as e:
            print(f"Error installing Oh My Zsh: {e}")
            sys.exit(1)
    else:
        print("Oh My Zsh is already installed")
        install_oh_my_zsh_theme()

def check_dependency(pkg):
    """Check if a package is installed"""
    if shutil.which(pkg):
        return True
    
    # Additional check for system packages
    if os.name != 'nt':  # Not Windows
        try:
            if subprocess.run(["which", pkg], 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE).returncode == 0:
                return True
        except:
            pass
    return False

def install_jetbrains_font():
    """Install JetBrains Mono Nerd Font if not already installed"""
    try:
        # Check if font is installed
        result = subprocess.run(["pacman", "-Qq", "ttf-jetbrains-mono-nerd"], 
                              capture_output=True)
        if result.returncode != 0:
            print_step("Installing JetBrains Mono Nerd Font")
            subprocess.check_call(["sudo", "pacman", "-S", "--noconfirm", "ttf-jetbrains-mono-nerd"])
            print("JetBrains Mono Nerd Font installed successfully")
        else:
            print("JetBrains Mono Nerd Font is already installed")
    except subprocess.CalledProcessError as e:
        print(f"Error installing JetBrains Mono Nerd Font: {e}")

def install_dependencies(system, args):
    """Install system dependencies based on the operating system."""
    system = system.lower()
    
    if system in ["arch", "archlinux"]:
        print_step("Installing dependencies on Arch Linux")
        
        # Install essential packages first
        print("Installing essential packages...")
        essential_packages = ["zsh", "tmux"]
        subprocess.run(["sudo", "pacman", "-S", "--needed", "--noconfirm"] + essential_packages, check=True)
        
        # Base packages for headless environment
        base_packages = [
            "neovim", "curl", "git", "wget",
            "ruby", "ruby-rake", "gcc",
            "ttf-jetbrains-mono-nerd"
        ]

        # Install zsh plugins separately to ensure they're found
        print("\nInstalling zsh plugins...")
        zsh_plugins = ["zsh-syntax-highlighting", "zsh-autosuggestions", "zsh-completions"]
        subprocess.run(["sudo", "pacman", "-S", "--needed", "--noconfirm"] + zsh_plugins, check=True)

        # Install zsh-autocomplete
        autocomplete_dir = os.path.expanduser("~/.zsh/zsh-autocomplete")
        if not os.path.exists(autocomplete_dir):
            print("\nInstalling zsh-autocomplete...")
            subprocess.run(["git", "clone", "--depth", "1",
                          "https://github.com/marlonrichert/zsh-autocomplete.git",
                          autocomplete_dir], check=True)

        # Install core packages
        core_packages = base_packages
        
        try:
            # Update package database first
            subprocess.run(["sudo", "pacman", "-Sy"], check=True)
            
            # Install all core packages in one command
            print("Installing core packages...")
            subprocess.run(["sudo", "pacman", "-S", "--needed", "--noconfirm"] + core_packages, check=True)
            
            # Check and install yay if needed
            if not shutil.which("yay"):
                print("\nInstalling yay AUR helper...")
                with tempfile.TemporaryDirectory() as tmpdir:
                    try:
                        subprocess.run(["git", "clone", "https://aur.archlinux.org/yay.git", tmpdir], check=True)
                        subprocess.run(["makepkg", "-si", "--noconfirm"], cwd=tmpdir, check=True)
                        print("yay installed successfully")
                    except subprocess.CalledProcessError:
                        print("Failed to install yay. Please install it manually.")
                        print("You can do this by running:")
                        print("git clone https://aur.archlinux.org/yay.git")
                        print("cd yay && makepkg -si")
                        return

            
            # Install colorls gem with proper permissions
            print("\nInstalling colorls gem...")
            try:
                subprocess.run(["gem", "install", "colorls", "--user-install"], check=True)
                # Create bin directory if it doesn't exist
                os.makedirs(os.path.expanduser("~/.local/share/gem/ruby/3.0.0/bin"), exist_ok=True)
                print("colorls installed successfully")
            except subprocess.CalledProcessError:
                print("Failed to install colorls. You may need to install it manually with:")
                print("gem install colorls --user-install")

            # No services to configure for headless setup

        except subprocess.CalledProcessError as e:
            print(f"Error during installation: {e}")
            print("Please check the error messages above and try to resolve any conflicts.")
            
    elif system in ["ubuntu", "debian"]:
        print("Ubuntu/Debian support not implemented yet")
        sys.exit(1)
    elif system in ["macos", "mac"]:
        print("MacOS support not implemented yet")
        sys.exit(1)
    elif system in ["windows"]:
        print("Windows support not implemented yet")
        sys.exit(1)
    else:
        print("Unknown system type. Please specify one of: ubuntu, arch, macos, or windows")
        sys.exit(1)

def ensure_line_in_file(file_path, line):
    """
    Helper function to ensure a given line is present in file_path.
    If not, appends it.
    """
    try:
        with open(file_path, "r+") as f:
            content = f.read()
            if line not in content:
                f.write("\n" + line + "\n")
                print(f"Appended line to {file_path}: {line}")
            else:
                print(f"Line already present in {file_path}: {line}")
    except Exception as e:
        print(f"Error updating {file_path}: {e}")

def ensure_local_bin_in_zshrc(zshrc_path):
    local_bin_line = 'export PATH="$HOME/.local/bin:$PATH"'
    ensure_line_in_file(zshrc_path, local_bin_line)

def clean_zshrc(zshrc_path):
    """Remove unwanted entries from zshrc"""
    try:
        with open(zshrc_path, "r") as f:
            lines = f.readlines()
        
        # Filter out conda references and other unwanted lines
        cleaned_lines = [line for line in lines if "conda" not in line]
        
        with open(zshrc_path, "w") as f:
            f.writelines(cleaned_lines)
        print("Cleaned up .zshrc file")
    except Exception as e:
        print(f"Error cleaning .zshrc: {e}")

def ensure_ruby_gem_bin_in_zshrc(zshrc_path):
    """
    Detects the Ruby gem bin directories and ensures they are added to the PATH
    in the dotfile (the source for ~/.zshrc).
    It uses two methods:
      1. The gem environment.
      2. Checks a local path under $HOME/.local/share/gem.
    """
    # First, try the gem environment.
    try:
        gem_dir = subprocess.check_output(["gem", "environment", "gemdir"]).decode().strip()
        gem_bin_dir = os.path.join(gem_dir, "bin")
        line = f'export PATH="{gem_bin_dir}:$PATH"'
        ensure_line_in_file(zshrc_path, line)
        print(f"Added Ruby gems bin directory to PATH (from gem environment): {gem_bin_dir}")
    except Exception as e:
        print(f"Skipping gem environment PATH update: {e}")

    # Next, check for a local gem installation directory.
    try:
        # Determine Ruby version
        ruby_version = subprocess.check_output(["ruby", "-e", "print RUBY_VERSION"]).decode().strip()
        local_gem_dir = os.path.join(os.path.expanduser("~"), ".local", "share", "gem", "ruby", ruby_version)
        local_gem_bin_dir = os.path.join(local_gem_dir, "bin")
        if os.path.isdir(local_gem_bin_dir):
            line = f'export PATH="{local_gem_bin_dir}:$PATH"'
            ensure_line_in_file(zshrc_path, line)
            print(f"Added local Ruby gems bin directory to PATH: {local_gem_bin_dir}")
    except Exception as e:
        print(f"Skipping local gem PATH update: {e}")

def create_symlinks(repo_dir, args):
    """Create symlinks for configuration files based on chosen environment"""
    home = os.path.expanduser("~")
    dotfiles_dir = os.path.join(repo_dir, "dotfiles")
    config_dir = os.path.join(repo_dir, "config")

    # Verify that the dotfiles directory exists.
    if not os.path.isdir(dotfiles_dir):
        print(f"Error: {dotfiles_dir} does not exist. Please check your repository.")
        sys.exit(1)
    
    # Create symlink for .zshrc.
    zshrc_src = os.path.abspath(os.path.join(dotfiles_dir, "zshrc"))
    zshrc_dest = os.path.join(home, ".zshrc")
    if os.path.exists(zshrc_dest) or os.path.islink(zshrc_dest):
        os.remove(zshrc_dest)
    os.symlink(zshrc_src, zshrc_dest)
    print(f"Created symlink: {zshrc_dest} -> {zshrc_src}")
    
    # Update and clean the source dotfile
    ensure_local_bin_in_zshrc(zshrc_src)
    ensure_ruby_gem_bin_in_zshrc(zshrc_src)
    clean_zshrc(zshrc_src)
    
    # Create symlink for .tmux.conf.
    tmux_src = os.path.abspath(os.path.join(dotfiles_dir, "tmux.conf"))
    tmux_dest = os.path.join(home, ".tmux.conf")
    if os.path.exists(tmux_dest) or os.path.islink(tmux_dest):
        os.remove(tmux_dest)
    os.symlink(tmux_src, tmux_dest)
    print(f"Created symlink: {tmux_dest} -> {tmux_src}")
    
    # Install tmux plugin manager if not already installed
    tpm_dir = os.path.expanduser("~/.tmux/plugins/tpm")
    if not os.path.exists(tpm_dir):
        print("Installing Tmux Plugin Manager (TPM)")
        subprocess.run(["git", "clone", "https://github.com/tmux-plugins/tpm", tpm_dir], check=True)
    
    # Source tmux config to load plugins
    try:
        subprocess.run(["tmux", "source", "~/.tmux.conf"], check=True)
        print("Tmux configuration sourced successfully")
    except subprocess.CalledProcessError:
        print("Note: Run 'tmux source ~/.tmux.conf' after starting tmux to load plugins")

    # Create symlink for Neovim config (placed in ~/.config/nvim).
    nvim_src = os.path.abspath(os.path.join(config_dir, "nvim"))
    nvim_dest = os.path.join(home, ".config", "nvim")
    os.makedirs(os.path.join(home, ".config"), exist_ok=True)
    if os.path.exists(nvim_dest) or os.path.islink(nvim_dest):
        if os.path.islink(nvim_dest):
            os.remove(nvim_dest)
        else:
            shutil.rmtree(nvim_dest)
    os.symlink(nvim_src, nvim_dest)
    print(f"Created symlink: {nvim_dest} -> {nvim_src}")

    # No DE-specific symlinks needed for headless setup

def set_default_shell(shell):
    if os.name != 'nt':
        # Get the current shell from /etc/passwd instead of environment
        try:
            import pwd
            current_shell = pwd.getpwuid(os.getuid()).pw_shell
            if shell == current_shell:
                print(f"Default shell is already {shell}")
            else:
                print_step(f"Changing default shell to {shell}")
                subprocess.check_call(["chsh", "-s", shell])
        except ImportError:
            print("Could not import pwd module, falling back to environment check")
            current_shell = os.environ.get("SHELL", "")
            if shell not in current_shell:
                print_step(f"Changing default shell to {shell}")
                subprocess.check_call(["chsh", "-s", shell])
            else:
                print(f"Default shell is already {shell}")
    else:
        print("Skipping default shell change on Windows.")

def check_symlinks():
    """Check all symlinks created by configs-cli"""
    home = os.path.expanduser("~")
    config_dir = os.path.join(home, ".config")
    
    # Define all expected symlinks
    home_links = {
        os.path.join(home, ".zshrc"): "zshrc",
        os.path.join(home, ".tmux.conf"): "tmux.conf",
    }
    
    config_links = {
        os.path.join(config_dir, "nvim"): "nvim config"
    }
    
    print_step("Checking symlinks status")
    
    def check_link_group(links, header):
        print(f"\n{header}:")
        for link_path, description in links.items():
            if os.path.exists(link_path):
                if os.path.islink(link_path):
                    target = os.path.realpath(link_path)
                    print(f"\033[92m✓\033[0m {description}: {link_path} -> {target}")
                else:
                    print(f"\033[93m⚠\033[0m {description}: {link_path} exists but is not a symlink")
            else:
                print(f"\033[91m✗\033[0m {description}: {link_path} does not exist")
    
    check_link_group(home_links, "Home directory symlinks")
    check_link_group(config_links, "Config directory symlinks")
    print()  # Add final newline for cleaner output

def print_source_commands():
    home = os.path.expanduser("~")
    print(f"source {os.path.join(home, '.zshrc')}")
    print("Also, if new executables are not found, try running 'rehash' in your shell.")

def configure_keyboard(repo_dir):
    """Configure keyboard settings using Xorg"""
    xorg_dir = "/etc/X11/xorg.conf.d"
    keyboard_conf = os.path.join(xorg_dir, "00-keyboard.conf")
    source_conf = os.path.join(repo_dir, "config/xorg/00-keyboard.conf")
    
    print_step("Configuring keyboard settings")
    
    # Create directory if it doesn't exist
    if not os.path.exists(xorg_dir):
        subprocess.run(["sudo", "mkdir", "-p", xorg_dir], check=True)
    
    # Copy the keyboard configuration file
    subprocess.run(["sudo", "cp", source_conf, keyboard_conf], check=True)
    subprocess.run(["sudo", "chmod", "644", keyboard_conf], check=True)
    
    print(f"Keyboard configuration copied to {keyboard_conf}")

def print_step(message):
    """Print a formatted step message"""
    print("\n" + "="*80)
    print(f">>> {message}")
    print("="*80 + "\n")

def setup_filesystem():
    """Create standard filesystem structure"""
    home = os.path.expanduser("~")
    
    # Define standard directories
    dirs = {
        "Documents": ["Projects", "Work", "Personal"],
        "Downloads": ["temp"],
        "Pictures": ["screenshots", "wallpapers"],
        "Videos": [],
        ".config": [],
        ".local/share": [],
        ".local/bin": [],
        ".cache": [],
        "Github": []
    }
    
    print_step("Setting up filesystem structure...")
    for parent, subdirs in dirs.items():
        parent_path = os.path.join(home, parent)
        os.makedirs(parent_path, exist_ok=True)
        print(f"Created: {parent_path}")
        
        for subdir in subdirs:
            subdir_path = os.path.join(parent_path, subdir)
            os.makedirs(subdir_path, exist_ok=True)
            print(f"Created: {subdir_path}")
    
    print("\nFilesystem structure created successfully!")

def main():
    print_step("Starting configs-cli setup tool")
    parser = argparse.ArgumentParser(
        description="Setup minimal headless development environment with zsh, neovim, and tmux"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: setup
    setup_parser = subparsers.add_parser("setup", help="Install dependencies and create symlinks")
    setup_parser.add_argument("--system", required=True, choices=["arch"],
                              help="Currently only Arch Linux is supported")
    
    # Use CONFIGS_REPO environment variable if set; otherwise, default to ~/.configs
    default_repo = os.environ.get("CONFIGS_REPO", os.path.join(os.path.expanduser("~"), ".configs"))
    setup_parser.add_argument("--repo", default=default_repo,
                              help="Path to your configs repository (or set CONFIGS_REPO)")
    setup_parser.add_argument("--repo-url", default=None,
                              help="Git URL of your repository (if not already cloned)")
    
    # Subcommand: check
    subparsers.add_parser("check", help="Check status of all config symlinks")
    
    # Subcommand: help
    help_parser = subparsers.add_parser("help", help="Show detailed help information")
    
    args = parser.parse_args()

    if args.command == "help":
        print("""
Configs CLI - Headless Development Environment Setup

This tool sets up a minimal development environment with:
- zsh (with Oh My Zsh)
- neovim
- tmux

Commands:
  setup   Install dependencies and create symlinks
    --system    Required. Currently only 'arch' is supported
    --repo      Path to configs repository (default: ~/.configs)
    --repo-url  Git URL to clone if repo doesn't exist
    
  check   Check status of all config symlinks
    
  help    Show this help message

Environment Variables:
  CONFIGS_REPO  Set default repository path

Quick Start:
  1. Clone your configs repository:
     git clone https://github.com/yourusername/configs.git ~/.configs

  2. Run the setup:
     configs-cli setup --system arch

  3. Start using your new environment:
     - Launch zsh
     - Start tmux
     - Open neovim
""")
        return

    if args.command == "setup":
        # Set up filesystem structure first
        setup_filesystem()
        
        # If the repository doesn't exist, attempt to clone it if --repo-url is provided.
        if not os.path.isdir(args.repo):
            if args.repo_url:
                print_step(f"Cloning repository from {args.repo_url}")
                subprocess.check_call(["git", "clone", args.repo_url, args.repo])
            else:
                print(f"Error: repository directory {args.repo} does not exist. "
                      f"Either clone it there or provide --repo-url to auto-clone it.")
                sys.exit(1)
        install_dependencies(args.system, args)
        if args.system != "windows":
            install_oh_my_zsh()
        create_symlinks(args.repo, args)
        if args.system != "windows":
            # Configure keyboard before shell changes
            if args.system in ["arch", "ubuntu"]:  # Only for Linux systems
                configure_keyboard(args.repo)
            
            zsh_path = shutil.which("zsh")
            if zsh_path:
                set_default_shell(zsh_path)
            else:
                print("zsh not found; please install it!")
        else:
            print("Default shell change skipped on Windows.")
    elif args.command == "source":
        print_source_commands()
    elif args.command == "check-links":
        check_symlinks()

if __name__ == "__main__":
    main()

