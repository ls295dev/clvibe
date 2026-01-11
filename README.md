# 🎮 clvibe

**CLI Game Manager for AI-Generated Games**

A versatile package manager and runtime launcher for command-line games written by AI in various programming languages. Think of it as `npm` or `pip`, but for CLI games across multiple languages.

> **🤖 AI-Generated Tool:** This tool was created by AI (Claude) and is designed to run games that are also typically AI-generated. While functional and useful, this comes with inherent risks when executing code from unknown sources.

---

## 💬 Community Discord

**Discord Server:** https://discord.gg/cynUyS2PQ8

The central hub for sharing AI-generated games. Think of it as a very irresponsible repository where games are shared directly.

⚠️ **Extra caution advised** - Games shared in Discord are completely unvetted. Always review code thoroughly before installing.

---

## ⚠️ IMPORTANT SECURITY WARNING

**THIS TOOL EXECUTES ARBITRARY CODE FROM THIRD-PARTY SOURCES**

🚨 **STRONGLY RECOMMENDED: Run in a containerized environment**

```bash
# Example: Run in Docker with isolated home directory
docker run -it --rm \
  -v $(pwd)/clvibe-home:/home/user/.clvibe \
  -v $(pwd)/games:/games:ro \
  python:3.11 bash

# Inside container, install and use clvibe safely
```

**Why containerization is important:**
- AI-generated games may contain bugs or unintended behavior
- Third-party code could access your file system
- Games have full access to your home directory by default
- Isolation limits potential damage from malicious or buggy code

**If you must run on your host system:**
- Create a separate user account with limited privileges
- Use a dedicated home directory: `HOME=/tmp/clvibe-home clvibe play game`
- Review all code before execution
- Never run as root/administrator
- Keep important data backed up

---

## ✨ Features

- 🎯 **Multi-Language Support** - Run games in 13+ languages (PHP, Python, Lua, JavaScript, Ruby, Perl, and more)
- 📦 **Package Management** - Install, uninstall, list, and organize games
- 🌐 **URL Downloads** - Install games directly from URLs or collections
- 💾 **Automatic Backups** - Keep zip backups of all installed games
- 🔄 **Sync & Restore** - Restore games from backups, sync your library
- 📚 **Collections** - Install multiple games at once from a single archive
- 🎨 **Smart Organization** - Handles name collisions with author/version suffixes
- ✅ **Runtime Detection** - Checks which language runtimes are available

---

## 🚀 Quick Start

### Installation

1. **Clone or download the repository:**
   ```bash
   git clone https://github.com/yourusername/clvibe.git
   cd clvibe
   ```

2. **Run the installer:**
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

3. **Verify installation:**
   ```bash
   clvibe check
   ```

4. **If it didn't work: Add to PATH**:
   ```bash
   export PATH="$PATH:$HOME/.local/bin"
   ```

### First Steps

```bash
# Check available language runtimes
clvibe check

# Install a game from a directory
clvibe install ./my-game/

# Install from a zip file
clvibe install ./my-game.zip

# Install from a URL
clvibe install https://example.com/game.zip

# List installed games
clvibe list

# Play a game (by name or number)
clvibe play "Semantic Labyrinth"
clvibe play 1
```

---

## 📖 Usage Guide

### Installing Games

**The `install` command automatically detects what you're installing:**

```bash
# Single game from directory
clvibe install ./my-game/

# Single game from zip
clvibe install ./my-game.zip

# Single game from URL
clvibe install https://example.com/game.zip

# Collection from directory (auto-detected: multiple game.json files)
clvibe install ./my-games-folder/

# Collection from zip (auto-detected)
clvibe install ./game-collection.zip

# Collection from URL (auto-detected)
clvibe install https://example.com/collection.zip

# Force as collection (install all games found, even if just one)
clvibe install ./games/ --collection
clvibe install ./games.zip -c
```

**Automatic detection:**
- If source contains 1 game.json → installs as single game
- If source contains 2+ game.json files → installs as collection
- Works with directories, zips, and URLs
- Use `--collection` or `-c` flag to force collection mode

**Batch installation (for multiple separate files/URLs):**
```bash
clvibe batch-install ./games/               # Install all game directories
clvibe batch-install ./zipped-games/ -z     # Install all zip files
clvibe batch-install urls.txt               # Install from URL list
```

### Managing Games

**List games:**
```bash
clvibe list           # Simple list
clvibe list -v        # Verbose with details
```

**Play a game:**
```bash
clvibe play "Game Name"    # By name
clvibe play 1              # By index
```

**Uninstall:**
```bash
clvibe uninstall "Game Name"
clvibe uninstall 1
```

### Backup & Restore

**List backups:**
```bash
clvibe list-zipped
```

**Restore from backup:**
```bash
clvibe restore "Game Name"
clvibe restore 1
```

**Sync backups:**
```bash
clvibe sync    # Create missing backups, remove orphaned ones
```

### Exporting

**Export single game:**
```bash
clvibe export "Game Name"              # Export as zip
clvibe export 1 -o my-game.zip         # Custom filename
```

**Export all games:**
```bash
clvibe batch-export ./exported/        # Export all as zips
clvibe batch-export ./exported/ -u     # Export as directories
```

---

## 📁 Directory Structure

```
~/.clvibe/
├── games/              # Installed games (unzipped)
│   ├── game-1/
│   ├── game-2/
│   └── ...
├── zipped/             # Zip backups
│   ├── game-1.zip
│   ├── game-2.zip
│   └── ...
└── config.json         # Configuration
```

---

## 🎯 Game Format

Each game must have a `game.json` file:

```json
{
    "name": "My Awesome Game",
    "author": "YourName",
    "llm": "Claude Sonnet 4",
    "version": "1.0",
    "lang": "python",
    "lang-version": "3.8+",
    "path": ""
}
```

**Required fields:**
- `name` - Game title
- `lang` - Programming language (lowercase)

**Optional fields:**
- `author` - Creator name
- `llm` - AI model used to generate
- `version` - Game version
- `lang-version` - Required language version
- `path` - Subdirectory containing the main file

**Main file naming:**
The tool will automatically look for:
- `main.<ext>` (e.g., `main.py`, `main.lua`)
- `index.<ext>`
- `game.<ext>`
- `start.<ext>`

---

## 🌐 Creating Collections

A collection is a zip file containing multiple games:

```
my-collection.zip
├── game-1/
│   ├── game.json
│   └── main.py
├── game-2/
│   ├── game.json
│   └── main.js
└── game-3/
    ├── game.json
    └── main.lua
```

**To create a collection:**
```bash
# Export all games as directories
clvibe batch-export ~/my-collection/ -u

# Zip the collection
cd ~/my-collection/
zip -r game-collection.zip *

# Share or install
clvibe install-collection game-collection.zip
```

---

## 🔧 Supported Languages

| Language   | Command      | Extension | Status |
|------------|--------------|-----------|--------|
| Python     | `python3`    | `.py`     | ✅     |
| JavaScript | `node`       | `.js`     | ✅     |
| Lua        | `lua`        | `.lua`    | ✅     |
| PHP        | `php`        | `.php`    | ✅     |
| Ruby       | `ruby`       | `.rb`     | ✅     |
| Perl       | `perl`       | `.pl`     | ✅     |
| Bash       | `bash`       | `.sh`     | ✅     |
| PowerShell | `pwsh`       | `.ps1`    | ✅     |
| R          | `Rscript`    | `.R`      | ✅     |
| Julia      | `julia`      | `.jl`     | ✅     |
| Tcl        | `tclsh`      | `.tcl`    | ✅     |
| Groovy     | `groovy`     | `.groovy` | ✅     |
| Dart       | `dart`       | `.dart`   | ✅     |

Check available runtimes on your system:
```bash
clvibe check
```

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Adding New Language Support

Edit `clvibe.py` and add to the `runtimes` dictionary:

```python
self.runtimes = {
    # ... existing languages ...
    "newlang": {"cmd": "newlang-interpreter", "ext": ".nl"},
}
```

### Creating Games

1. Write your game in any supported language
2. Use the vibify command or manually create a `game.json` with required metadata
3. Test it works with `clvibe install ./your-game/`
4. Share it with the community!

### Reporting Issues

Found a bug? Have a feature request? Make your own version of the manager using Claude Sonnet 4.5!

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## ⚠️ Security & Safety

**IMPORTANT:** This tool executes code from games you install. Additionally, both this tool and the games it runs are typically AI-generated, which carries specific risks.

### 🤖 AI-Generated Code Risks

**This tool was written by AI (Claude), and games are expected to be AI-generated:**

- 🐛 **Unpredictable bugs** - AI may generate code with subtle errors or edge cases
- 🔓 **Security gaps** - AI doesn't always follow security best practices
- 💥 **Unintended behavior** - AI-generated code may do unexpected things
- 📝 **Documentation gaps** - Features may not work as described
- 🎲 **Variable quality** - Code quality varies greatly between generations

### 🛡️ Mandatory Security Practices

**DO NOT run this tool directly on your main system. Use containerization:**

```bash
# Docker example
docker run -it --rm \
  --name clvibe-sandbox \
  -v $(pwd)/clvibe-games:/home/user/.clvibe \
  -v $(pwd)/downloads:/downloads:ro \
  --network none \
  python:3.11-slim bash

# Install clvibe inside container
pip install --user --no-index /path/to/clvibe

# Podman example (recommended)
podman run -it --rm \
  -v ./clvibe-data:/home/user/.clvibe:Z \
  python:3.11 bash
```

**If containerization is not available:**

1. **Create isolated user:**
   ```bash
   sudo useradd -m -s /bin/bash clvibe-user
   sudo su - clvibe-user
   ```

2. **Use temporary home directory:**
   ```bash
   mkdir /tmp/clvibe-sandbox
   HOME=/tmp/clvibe-sandbox clvibe play game
   ```

3. **Restrict file access:**
   ```bash
   # Run with limited permissions
   sudo -u nobody env HOME=/tmp/clvibe-home clvibe play game
   ```

### 📋 Safety Checklist

Before installing/running any game:

- [ ] Are you running in a container or isolated environment?
- [ ] Have you reviewed the game's source code?
- [ ] Do you trust the source/author?
- [ ] Have you checked for suspicious file operations?
- [ ] Have you backed up important data?
- [ ] Are you using a non-privileged account?
- [ ] Have you limited network access if needed?

### 🚫 Never Do This

- ❌ Run as root/administrator
- ❌ Run on your main system without isolation
- ❌ Install games without reviewing code
- ❌ Trust code just because it's AI-generated
- ❌ Share your actual home directory with games
- ❌ Run games with access to sensitive data
- ❌ Assume AI-generated code is safe or correct

### ✅ Best Practices

- ✅ Always use containers (Docker, Podman, etc.)
- ✅ Use read-only mounts for game sources
- ✅ Disable network access unless required
- ✅ Review all game.json files and main scripts
- ✅ Test games in throwaway environments first
- ✅ Keep clvibe and games in separate, isolated directories
- ✅ Monitor system resources during gameplay
- ✅ Report suspicious behavior immediately

---

## 📄 Vibe Coder License

**Copyright © 2025 clvibe contributors**

**Permission is hereby granted**, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

**The above copyright notice and this permission notice** shall be included in all copies or substantial portions of the Software.

**⚠️ CAUTION NOTICE:**

This Software is designed to execute third-party code and content from various sources, primarily AI-generated games and applications. **The Software itself was also created by AI (Claude).** Users must exercise extreme caution and understand the following:

1. **AI-Generated Code Risks**: Both this Software and the content it executes are AI-generated, which introduces unique risks:
   - AI-generated code may contain subtle bugs, security vulnerabilities, or logic errors
   - AI does not always follow security best practices or understand all edge cases
   - Code behavior may be unpredictable or differ from documented functionality
   - AI-generated games may perform unexpected file operations or system calls

2. **Expected Isolation**: Users ARE EXPECTED TO run this Software in an isolated environment:
   - **Containerization is strongly recommended** (Docker, Podman, etc.)
   - Use a separate, non-privileged user account at minimum
   - Never run on your primary system without isolation
   - Never run as root or with administrative privileges
   - Use temporary or dedicated home directories, not your actual home directory

3. **Third-Party Risk**: The Software executes games and programs created by third parties. The authors of this Software do not review, approve, or guarantee the safety, security, or functionality of any third-party content.

4. **User Responsibility**: Users are solely responsible for:
   - Implementing appropriate isolation (containers, VMs, separate users)
   - Reviewing and verifying the safety of any games or content before installation
   - Understanding the code they choose to execute
   - Any consequences resulting from running this Software or third-party code
   - Ensuring compliance with applicable laws and regulations
   - Maintaining backups of important data
   - Monitoring system resources and behavior during execution

5. **No Security Guarantees**: While the Software provides tools for managing and running games, it makes absolutely no security guarantees about:
   - The safety of its own code (being AI-generated)
   - The content it executes
   - The behavior of installed games
   - Protection against malicious or buggy code

6. **Required Actions**:
   - Run this Software only in containerized or heavily isolated environments
   - Review all source code before execution when possible
   - Use dedicated, isolated directories for all clvibe operations
   - Implement network restrictions when appropriate
   - Never grant access to sensitive data or directories
   - Treat all AI-generated code (including this tool) as potentially unsafe

7. **Recommendations**: Users are strongly encouraged to:
   - Use Docker/Podman with read-only mounts for game files
   - Disable network access unless absolutely required
   - Only install games from sources you personally trust
   - Test games in completely throwaway environments first
   - Monitor system behavior during and after game execution
   - Report any suspicious behavior to the community immediately

**THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED**, including but not limited to the warranties of merchantability, fitness for a particular purpose, and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or in connection with the Software or the use or other dealings in the Software.

**By using this Software, you acknowledge that you have read this license, understand the risks involved in executing third-party code, and agree to take full responsibility for your use of the Software.**

---

## 🙏 Acknowledgments

- 🤖 **Created by AI** - This tool was generated by Claude (Anthropic)
- 🎮 **For AI Games** - Designed for the AI-generated game community
- 📦 Inspired by package managers like npm, pip, and cargo
- 🙏 Thanks to all contributors and game creators
- ⚠️ Special thanks to the security-conscious community for emphasizing safe practices

**Remember:** Both this tool and the games it runs are AI-generated. Always prioritize security through isolation and careful code review.

---

## 📞 Support

- **Discord**: https://discord.gg/cynUyS2PQ8 (Central hub for game sharing)
- **Documentation**: This README
- **Issues**: use AI

---

## 🎮 Happy Gaming!

Start building and sharing AI-generated CLI games today. The only limit is your imagination (and your LLM's context window)!

```bash
clvibe check
clvibe install https://example.com/awesome-game.zip
clvibe play 1
```

**Let the games begin! 🚀**