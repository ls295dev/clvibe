#!/usr/bin/env python3
"""
clvibe - CLI Game Manager for AI-generated games
A package manager and runtime launcher for CLI games in various languages
"""

import os
import sys
import json
import subprocess
import shutil
import zipfile
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Optional, List, Dict
import argparse

class ClvibeManager:
    def __init__(self):
        self.home_dir = Path.home() / ".clvibe"
        self.games_dir = self.home_dir / "games"
        self.zipped_dir = self.home_dir / "zipped"
        self.config_file = self.home_dir / "config.json"
        
        # Language runtime configurations
        self.runtimes = {
            "php": {"cmd": "php", "ext": ".php"},
            "python": {"cmd": "python3", "ext": ".py"},
            "lua": {"cmd": "lua", "ext": ".lua"},
            "js": {"cmd": "node", "ext": ".js"},
            "ruby": {"cmd": "ruby", "ext": ".rb"},
            "perl": {"cmd": "perl", "ext": ".pl"},
            "bash": {"cmd": "bash", "ext": ".sh"},
            "powershell": {"cmd": "pwsh", "ext": ".ps1"},
            "r": {"cmd": "Rscript", "ext": ".R"},
            "julia": {"cmd": "julia", "ext": ".jl"},
            "tcl": {"cmd": "tclsh", "ext": ".tcl"},
            "groovy": {"cmd": "groovy", "ext": ".groovy"},
            "dart": {"cmd": "dart", "ext": ".dart"},
        }
        
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary directories if they don't exist"""
        self.home_dir.mkdir(exist_ok=True)
        self.games_dir.mkdir(exist_ok=True)
        self.zipped_dir.mkdir(exist_ok=True)
    
    def _find_main_file(self, game_path: Path, lang: str) -> Optional[Path]:
        """Find the main file for a game based on language"""
        runtime = self.runtimes.get(lang.lower())
        if not runtime:
            return None
        
        ext = runtime["ext"]
        
        # Common main file names
        main_names = [f"main{ext}", f"index{ext}", f"game{ext}", f"start{ext}"]
        
        for name in main_names:
            main_file = game_path / name
            if main_file.exists():
                return main_file
        
        # If not found, search for any file with the right extension
        files = list(game_path.glob(f"*{ext}"))
        return files[0] if files else None
    
    def _check_runtime(self, lang: str) -> bool:
        """Check if runtime for language is available"""
        runtime = self.runtimes.get(lang.lower())
        if not runtime:
            return False
        
        try:
            subprocess.run(
                [runtime["cmd"], "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5
            )
            return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def list_games(self, verbose: bool = False):
        """List all installed games"""
        games = self._get_all_games()
        
        if not games:
            print("No games installed. Use 'clvibe install <path>' to add games.")
            return
        
        print(f"📚 Installed Games ({len(games)}):\n")
        
        for idx, game in enumerate(games, 1):
            name = game["metadata"].get("name", "Unknown")
            author = game["metadata"].get("author", "Unknown")
            version = game["metadata"].get("version", "?")
            lang = game["metadata"].get("lang", "Unknown")
            llm = game["metadata"].get("llm", "Unknown")
            
            runtime_available = self._check_runtime(lang)
            status = "✓" if runtime_available else "✗"
            
            # Check if backed up
            slug = game["path"].name
            zip_exists = (self.zipped_dir / f"{slug}.zip").exists()
            backup_indicator = "💾" if zip_exists else "  "
            
            # Always show version, author, and LLM
            print(f"  [{idx}] {status} {backup_indicator} {name}")
            print(f"      v{version} • by {author} • {llm}")
            
            if verbose:
                print(f"      Language: {lang}")
                print(f"      Path: {game['path']}")
                if zip_exists:
                    print(f"      Backup: {self.zipped_dir / f'{slug}.zip'}")
                if not runtime_available:
                    print(f"      ⚠️  Runtime not available: {self.runtimes.get(lang.lower(), {}).get('cmd', lang)}")
                print()
    
    def _get_all_games(self) -> List[Dict]:
        """Get list of all games with their metadata"""
        games = []
        
        for game_dir in self.games_dir.iterdir():
            if not game_dir.is_dir():
                continue
            
            game_json = game_dir / "game.json"
            if not game_json.exists():
                continue
            
            try:
                with open(game_json, 'r') as f:
                    metadata = json.load(f)
                    games.append({
                        "path": game_dir,
                        "metadata": metadata,
                        "name": metadata.get("name", game_dir.name)
                    })
            except json.JSONDecodeError:
                print(f"⚠️  Invalid game.json in {game_dir.name}")
        
        return sorted(games, key=lambda x: x["name"].lower())
    
    def _find_game(self, identifier: str) -> Optional[Dict]:
        """Find game by name or index"""
        games = self._get_all_games()
        
        # Try as index
        try:
            idx = int(identifier) - 1
            if 0 <= idx < len(games):
                return games[idx]
        except ValueError:
            pass
        
        # Try as name (case-insensitive partial match)
        identifier_lower = identifier.lower()
        for game in games:
            if identifier_lower in game["name"].lower():
                return game
        
        return None
    
    def play_game(self, identifier: str):
        """Launch a game by name or index"""
        game = self._find_game(identifier)
        
        if not game:
            print(f"❌ Game '{identifier}' not found.")
            print("Use 'clvibe list' to see available games.")
            return
        
        metadata = game["metadata"]
        lang = metadata.get("lang", "").lower()
        game_path = game["path"]
        
        # Check runtime availability
        if not self._check_runtime(lang):
            runtime_cmd = self.runtimes.get(lang, {}).get("cmd", lang)
            print(f"❌ Runtime not available: {runtime_cmd}")
            print(f"Please install {lang} to play this game.")
            return
        
        # Find main file
        if metadata.get("path"):
            subpath = game_path / metadata["path"]
            if subpath.exists() and subpath.is_dir():
                game_path = subpath
        
        main_file = self._find_main_file(game_path, lang)
        
        if not main_file:
            print(f"❌ Could not find main file for {lang} in {game_path}")
            return
        
        # Launch the game
        runtime = self.runtimes[lang]
        print(f"🎮 Launching: {metadata['name']}")
        print(f"   Language: {lang}")
        print(f"   Command: {runtime['cmd']} {main_file.name}\n")
        print("=" * 60)
        
        try:
            subprocess.run(
                [runtime["cmd"], str(main_file)],
                cwd=str(game_path)
            )
        except KeyboardInterrupt:
            print("\n\n🛑 Game interrupted by user.")
        except Exception as e:
            print(f"\n❌ Error running game: {e}")
    
    def install_game(self, source_path: str, force_collection: bool = False):
        """Install a game from a directory, zip file, or URL
        
        Automatically detects:
        - Single games (one game.json)
        - Collections (multiple game.json files)
        - Directories, zip files, or URLs
        """
        # Check if it's a URL
        if source_path.startswith(('http://', 'https://')):
            self._install_from_url(source_path, force_collection=force_collection)
            return
        
        source = Path(source_path)
        
        if not source.exists():
            print(f"❌ Path not found: {source_path}")
            return
        
        # Handle zip files
        if source.is_file() and source.suffix == ".zip":
            if not zipfile.is_zipfile(source):
                print(f"❌ Not a valid zip file")
                return
            
            # Check if it's a collection (2+ game.json files)
            is_collection = self._is_collection_zip(source)
            
            if force_collection or is_collection:
                if is_collection:
                    print(f"📦 Detected collection (multiple games found)")
                else:
                    print(f"📦 Installing as collection (forced)")
                self._install_collection_from_zip(source)
            else:
                print(f"📦 Installing single game")
                self._install_from_zip(source)
        elif source.is_dir():
            # Check if directory contains multiple games (collection)
            game_jsons = list(source.rglob("game.json"))
            
            if len(game_jsons) > 1:
                print(f"📦 Detected collection with {len(game_jsons)} game(s)")
                self._install_collection_from_directory(source)
            elif len(game_jsons) == 1:
                if force_collection:
                    print(f"📦 Installing as collection (forced)")
                    self._install_collection_from_directory(source)
                else:
                    # Single game - find the directory containing game.json
                    game_dir = game_jsons[0].parent
                    self._install_from_directory(game_dir)
            else:
                print(f"❌ No game.json found in directory")
        else:
            print("❌ Source must be a directory, .zip file, or URL")
    
    def _install_from_url(self, url: str, force_collection: bool = False):
        """Download and install game from URL"""
        print(f"🌐 Downloading from: {url}")
        
        # Parse filename from URL
        parsed_url = urllib.parse.urlparse(url)
        filename = Path(parsed_url.path).name
        
        if not filename:
            filename = "downloaded_game.zip"
        
        # If no extension, assume .zip
        if not filename.endswith('.zip'):
            filename += '.zip'
        
        # Download to temp directory
        temp_dir = self.home_dir / "temp_downloads"
        temp_dir.mkdir(exist_ok=True)
        temp_file = temp_dir / filename
        
        try:
            # Download with progress indication
            def report_progress(block_num, block_size, total_size):
                downloaded = block_num * block_size
                if total_size > 0:
                    percent = min(downloaded * 100 / total_size, 100)
                    mb_downloaded = downloaded / (1024 * 1024)
                    mb_total = total_size / (1024 * 1024)
                    print(f"\r📥 Progress: {percent:.1f}% ({mb_downloaded:.2f}/{mb_total:.2f} MB)", end='', flush=True)
            
            urllib.request.urlretrieve(url, temp_file, reporthook=report_progress)
            print()  # New line after progress
            
            file_size_mb = temp_file.stat().st_size / (1024 * 1024)
            print(f"✅ Downloaded: {filename} ({file_size_mb:.2f} MB)")
            
            # Verify it's a valid zip
            if not zipfile.is_zipfile(temp_file):
                print(f"❌ Downloaded file is not a valid zip archive")
                temp_file.unlink()
                return
            
            # Check if it's a collection (2+ game.json files)
            is_collection = self._is_collection_zip(temp_file)
            
            if force_collection or is_collection:
                if is_collection:
                    print(f"📦 Detected collection (multiple games found)")
                else:
                    print(f"📦 Installing as collection (forced)")
                self._install_collection_from_zip(temp_file)
            else:
                print(f"📦 Installing single game")
                self._install_from_zip(temp_file)
            
        except urllib.error.HTTPError as e:
            print(f"\n❌ HTTP Error {e.code}: {e.reason}")
            print(f"   Could not download from: {url}")
        except urllib.error.URLError as e:
            print(f"\n❌ URL Error: {e.reason}")
            print(f"   Could not connect to: {url}")
        except Exception as e:
            print(f"\n❌ Download failed: {e}")
        finally:
            # Clean up temp file
            if temp_file.exists():
                temp_file.unlink()
            # Clean up temp directory if empty
            if temp_dir.exists() and not any(temp_dir.iterdir()):
                temp_dir.rmdir()
    
    def _get_unique_slug(self, base_slug: str, metadata: Dict) -> str:
        """Generate a unique slug, considering author and version if needed"""
        slug = base_slug
        dest_dir = self.games_dir / slug
        
        # If no collision, use base slug
        if not dest_dir.exists():
            return slug
        
        # Check if it's the exact same game (same author + version)
        existing_json = dest_dir / "game.json"
        if existing_json.exists():
            try:
                with open(existing_json, 'r') as f:
                    existing_meta = json.load(f)
                
                # Same author and version = update
                if (existing_meta.get("author") == metadata.get("author") and
                    existing_meta.get("version") == metadata.get("version")):
                    return slug
            except json.JSONDecodeError:
                pass
        
        # Different game with same name - add author suffix
        author = metadata.get("author", "unknown")
        author_slug = author.lower().replace(" ", "-")[:20]  # Limit length
        slug_with_author = f"{base_slug}-by-{author_slug}"
        
        if not (self.games_dir / slug_with_author).exists():
            return slug_with_author
        
        # Still collision - add version
        version = metadata.get("version", "1.0").replace(".", "")
        slug_with_version = f"{slug_with_author}-v{version}"
        
        if not (self.games_dir / slug_with_version).exists():
            return slug_with_version
        
        # Last resort - add number suffix
        counter = 2
        while (self.games_dir / f"{slug_with_version}-{counter}").exists():
            counter += 1
        
        return f"{slug_with_version}-{counter}"
    
    def _install_from_directory(self, source_dir: Path):
        """Install game from directory"""
        game_json = source_dir / "game.json"
        
        if not game_json.exists():
            print(f"❌ No game.json found in {source_dir}")
            return
        
        try:
            with open(game_json, 'r') as f:
                metadata = json.load(f)
        except json.JSONDecodeError:
            print("❌ Invalid game.json format")
            return
        
        game_name = metadata.get("name", source_dir.name)
        base_slug = game_name.lower().replace(" ", "-")
        slug = self._get_unique_slug(base_slug, metadata)
        dest_dir = self.games_dir / slug
        
        # Check if updating existing game
        if dest_dir.exists():
            print(f"⚠️  Updating existing game: {game_name}")
            response = input("Overwrite? [y/N]: ")
            if response.lower() != 'y':
                print("Installation cancelled.")
                return
            shutil.rmtree(dest_dir)
        elif slug != base_slug:
            print(f"ℹ️  Name collision detected. Installing as: {slug}")
        
        shutil.copytree(source_dir, dest_dir)
        print(f"✅ Installed: {game_name}")
        
        # Create zip backup
        zip_path = self.zipped_dir / f"{slug}.zip"
        self._create_zip(dest_dir, zip_path)
        print(f"📦 Backed up to: {zip_path}")
    
    def _install_from_zip(self, zip_path: Path):
        """Install single game from zip file (for zips with only 1 game.json)"""
        # Extract to temporary location first to read metadata
        temp_extract = self.home_dir / "temp_extract"
        temp_extract.mkdir(exist_ok=True)
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(temp_extract)
            
            # Find game.json (might be in subdirectory)
            game_json = None
            for root, dirs, files in os.walk(temp_extract):
                if "game.json" in files:
                    game_json = Path(root) / "game.json"
                    break
            
            if not game_json:
                print(f"❌ No game.json found in zip file")
                return
            
            with open(game_json, 'r') as f:
                metadata = json.load(f)
            
            game_name = metadata.get("name", zip_path.stem)
            base_slug = game_name.lower().replace(" ", "-")
            slug = self._get_unique_slug(base_slug, metadata)
            
            # Copy zip to zipped directory with proper name
            dest_zip = self.zipped_dir / f"{slug}.zip"
            shutil.copy2(zip_path, dest_zip)
            print(f"📦 Stored zip: {dest_zip.name}")
            
            # Extract to games directory
            extract_dir = self.games_dir / slug
            
            # Check if updating existing game
            if extract_dir.exists():
                print(f"⚠️  Updating existing game: {game_name}")
                response = input("Overwrite? [y/N]: ")
                if response.lower() != 'y':
                    print("Installation cancelled.")
                    dest_zip.unlink()  # Remove copied zip
                    return
                shutil.rmtree(extract_dir)
            elif slug != base_slug:
                print(f"ℹ️  Name collision detected. Installing as: {slug}")
            
            # Move from temp to final location
            game_source = game_json.parent
            shutil.move(str(game_source), str(extract_dir))
            
            print(f"✅ Installed: {game_name}")
            
        finally:
            # Clean up temp directory
            if temp_extract.exists():
                shutil.rmtree(temp_extract)
    
    def _is_collection_zip(self, zip_path: Path) -> bool:
        """Check if zip contains multiple games (collection)"""
        game_json_count = 0
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                for name in zf.namelist():
                    if name.endswith('game.json'):
                        game_json_count += 1
                        if game_json_count > 1:
                            return True
        except Exception:
            return False
        
        return False
    
    def _install_collection_from_directory(self, source_dir: Path):
        """Install multiple games from a directory containing multiple game.json files"""
        # Find all game directories
        game_dirs = []
        for root, dirs, files in os.walk(source_dir):
            if "game.json" in files:
                game_dirs.append(Path(root))
        
        if not game_dirs:
            print(f"❌ No games found in directory")
            return
        
        print(f"🎮 Found {len(game_dirs)} game(s) in collection:\n")
        
        # Preview games
        game_names = []
        for game_dir in game_dirs:
            try:
                with open(game_dir / "game.json", 'r') as f:
                    metadata = json.load(f)
                    name = metadata.get("name", game_dir.name)
                    game_names.append(name)
                    print(f"  • {name}")
            except Exception:
                print(f"  • {game_dir.name} (could not read metadata)")
        
        print()
        response = input(f"Install all {len(game_dirs)} games? [y/N]: ")
        
        if response.lower() != 'y':
            print("Cancelled.")
            return
        
        print()
        successful = 0
        failed = 0
        
        # Install each game
        for i, game_dir in enumerate(game_dirs, 1):
            name = game_names[i-1] if i-1 < len(game_names) else game_dir.name
            print(f"[{i}/{len(game_dirs)}] Installing: {name}")
            try:
                self._install_from_directory(game_dir)
                successful += 1
            except Exception as e:
                print(f"  ❌ Failed: {e}")
                failed += 1
            print()
        
        print("=" * 60)
        print(f"✅ Successfully installed: {successful}")
        if failed > 0:
            print(f"❌ Failed: {failed}")
        print()
    
    def _install_collection_from_zip(self, zip_path: Path):
        """Install multiple games from a collection zip file"""
        temp_extract = self.home_dir / "temp_collection"
        
        try:
            # Extract collection
            print(f"📂 Extracting collection...")
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(temp_extract)
            
            # Find all game directories
            game_dirs = []
            for root, dirs, files in os.walk(temp_extract):
                if "game.json" in files:
                    game_dirs.append(Path(root))
            
            if not game_dirs:
                print(f"❌ No games found in collection")
                return
            
            print(f"🎮 Found {len(game_dirs)} game(s) in collection:\n")
            
            # Preview games
            game_names = []
            for game_dir in game_dirs:
                try:
                    with open(game_dir / "game.json", 'r') as f:
                        metadata = json.load(f)
                        name = metadata.get("name", game_dir.name)
                        game_names.append(name)
                        print(f"  • {name}")
                except Exception:
                    print(f"  • {game_dir.name} (could not read metadata)")
            
            print()
            response = input(f"Install all {len(game_dirs)} games? [y/N]: ")
            
            if response.lower() != 'y':
                print("Cancelled.")
                return
            
            print()
            successful = 0
            failed = 0
            
            # Install each game
            for i, game_dir in enumerate(game_dirs, 1):
                name = game_names[i-1] if i-1 < len(game_names) else game_dir.name
                print(f"[{i}/{len(game_dirs)}] Installing: {name}")
                try:
                    self._install_from_directory(game_dir)
                    successful += 1
                except Exception as e:
                    print(f"  ❌ Failed: {e}")
                    failed += 1
                print()
            
            print("=" * 60)
            print(f"✅ Successfully installed: {successful}")
            if failed > 0:
                print(f"❌ Failed: {failed}")
            print()
            
        finally:
            # Clean up temp extraction
            if temp_extract.exists():
                shutil.rmtree(temp_extract)
    
    def batch_install(self, source_path: str, zipped: bool = False):
        """Install multiple games from a directory or from URLs file"""
        # Check if it's a URL list file
        source = Path(source_path)
        if source.is_file() and source.suffix in ['.txt', '.list']:
            self._batch_install_from_urls(source)
            return
        
        if not source.exists() or not source.is_dir():
            print(f"❌ Directory not found: {source_path}")
            return
        
        print(f"🔍 Scanning for games in: {source}\n")
        
        games_found = []
        
        if zipped:
            # Install from zip files
            for zip_file in source.glob("*.zip"):
                games_found.append(zip_file)
        else:
            # Install from directories with game.json
            for item in source.iterdir():
                if item.is_dir() and (item / "game.json").exists():
                    games_found.append(item)
        
        if not games_found:
            file_type = "zip files" if zipped else "game directories"
            print(f"❌ No {file_type} found in {source}")
            return
        
        print(f"Found {len(games_found)} game(s):\n")
        
        for i, game_path in enumerate(games_found, 1):
            print(f"  [{i}] {game_path.name}")
        
        print()
        response = input(f"Install all {len(games_found)} games? [y/N]: ")
        
        if response.lower() != 'y':
            print("Cancelled.")
            return
        
        print()
        successful = 0
        failed = 0
        
        for game_path in games_found:
            print(f"Installing: {game_path.name}")
            try:
                self.install_game(str(game_path))
                successful += 1
            except Exception as e:
                print(f"  ❌ Failed: {e}")
                failed += 1
            print()
        
        print("=" * 50)
        print(f"✅ Successfully installed: {successful}")
        if failed > 0:
            print(f"❌ Failed: {failed}")
        print()
    
    def _batch_install_from_urls(self, urls_file: Path):
        """Install multiple games from a list of URLs"""
        print(f"📋 Reading URLs from: {urls_file}\n")
        
        try:
            with open(urls_file, 'r') as f:
                urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        except Exception as e:
            print(f"❌ Could not read file: {e}")
            return
        
        if not urls:
            print("❌ No URLs found in file")
            return
        
        print(f"Found {len(urls)} URL(s):\n")
        
        for i, url in enumerate(urls, 1):
            print(f"  [{i}] {url}")
        
        print()
        response = input(f"Download and install all {len(urls)} games? [y/N]: ")
        
        if response.lower() != 'y':
            print("Cancelled.")
            return
        
        print()
        successful = 0
        failed = 0
        
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] Processing: {url}")
            print("-" * 60)
            try:
                self._install_from_url(url)
                successful += 1
            except Exception as e:
                print(f"❌ Failed: {e}")
                failed += 1
        
        print("\n" + "=" * 60)
        print(f"✅ Successfully installed: {successful}")
        if failed > 0:
            print(f"❌ Failed: {failed}")
        print()
    
    def batch_export(self, output_dir: str, zipped: bool = True):
        """Export all games to a directory"""
        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)
        
        games = self._get_all_games()
        
        if not games:
            print("❌ No games to export.")
            return
        
        print(f"📦 Exporting {len(games)} game(s) to: {output}\n")
        
        successful = 0
        failed = 0
        
        for game in games:
            game_name = game["name"]
            slug = game_name.lower().replace(" ", "-")
            
            try:
                if zipped:
                    # Export as zip
                    zip_path = output / f"{slug}.zip"
                    self._create_zip(game["path"], zip_path)
                    print(f"✅ {game_name} → {zip_path.name}")
                else:
                    # Copy directory
                    dest_dir = output / slug
                    if dest_dir.exists():
                        shutil.rmtree(dest_dir)
                    shutil.copytree(game["path"], dest_dir)
                    print(f"✅ {game_name} → {dest_dir.name}/")
                
                successful += 1
            except Exception as e:
                print(f"❌ {game_name}: {e}")
                failed += 1
        
        print()
        print("=" * 50)
        print(f"✅ Successfully exported: {successful}")
        if failed > 0:
            print(f"❌ Failed: {failed}")
        print(f"📁 Location: {output}")
        print()
    
    def export_game(self, identifier: str, output_path: Optional[str] = None):
        """Export a game as a zip file"""
        game = self._find_game(identifier)
        
        if not game:
            print(f"❌ Game '{identifier}' not found.")
            return
        
        if not output_path:
            slug = game["name"].lower().replace(" ", "-")
            output_path = f"{slug}.zip"
        
        output = Path(output_path)
        self._create_zip(game["path"], output)
        print(f"✅ Exported to: {output}")
    
    def _create_zip(self, source_dir: Path, zip_path: Path):
        """Create a zip file from directory"""
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file in source_dir.rglob('*'):
                if file.is_file():
                    zf.write(file, file.relative_to(source_dir))
    
    def uninstall_game(self, identifier: str):
        """Uninstall a game"""
        game = self._find_game(identifier)
        
        if not game:
            print(f"❌ Game '{identifier}' not found.")
            return
        
        game_name = game["name"]
        slug = game["path"].name
        zip_path = self.zipped_dir / f"{slug}.zip"
        
        # Show what will be deleted
        print(f"Game: {game_name}")
        print(f"Path: {game['path']}")
        if zip_path.exists():
            print(f"Backup: {zip_path}")
        
        # Confirm deletion
        print()
        response = input(f"Uninstall '{game_name}'? [y/N]: ")
        if response.lower() != 'y':
            print("Cancelled.")
            return
        
        # Remove game directory
        shutil.rmtree(game["path"])
        print(f"✅ Removed game files")
        
        # Ask about zip backup
        if zip_path.exists():
            response = input(f"Also delete zip backup? [y/N]: ")
            if response.lower() == 'y':
                zip_path.unlink()
                print(f"✅ Removed backup")
            else:
                print(f"💾 Kept backup: {zip_path}")
        
        print(f"\n✅ Uninstalled: {game_name}")
    
    def restore_from_zip(self, identifier: str):
        """Restore a game from its zip backup"""
        # Find zip file
        zip_files = list(self.zipped_dir.glob("*.zip"))
        
        if not zip_files:
            print("❌ No zip backups found.")
            return
        
        # Try to find by name or index
        selected_zip = None
        
        try:
            idx = int(identifier) - 1
            if 0 <= idx < len(zip_files):
                selected_zip = sorted(zip_files)[idx]
        except ValueError:
            # Search by name
            identifier_lower = identifier.lower()
            for zip_file in zip_files:
                if identifier_lower in zip_file.stem.lower():
                    selected_zip = zip_file
                    break
        
        if not selected_zip:
            print(f"❌ Zip backup '{identifier}' not found.")
            print("\nAvailable backups:")
            for i, zf in enumerate(sorted(zip_files), 1):
                print(f"  [{i}] {zf.stem}")
            return
        
        print(f"📦 Restoring from: {selected_zip.name}")
        self._install_from_zip(selected_zip)
    
    def list_zipped(self):
        """List all zip backups"""
        zip_files = sorted(self.zipped_dir.glob("*.zip"))
        
        if not zip_files:
            print("📦 No zip backups found.")
            return
        
        print(f"📦 Zip Backups ({len(zip_files)}):\n")
        
        installed_games = {g["path"].name for g in self._get_all_games()}
        
        for idx, zip_file in enumerate(zip_files, 1):
            slug = zip_file.stem
            installed = "✓" if slug in installed_games else " "
            size_mb = zip_file.stat().st_size / (1024 * 1024)
            
            print(f"  [{idx}] {installed} {zip_file.stem} ({size_mb:.2f} MB)")
        
        print(f"\n✓ = Currently installed")
        print(f"Total backup size: {sum(f.stat().st_size for f in zip_files) / (1024 * 1024):.2f} MB")
    
    def sync_zips(self):
        """Sync zip backups - create missing zips, remove orphaned zips"""
        games = self._get_all_games()
        zip_files = {zf.stem: zf for zf in self.zipped_dir.glob("*.zip")}
        
        print("🔄 Syncing zip backups...\n")
        
        created = 0
        removed = 0
        
        # Create missing zips
        for game in games:
            slug = game["path"].name
            if slug not in zip_files:
                zip_path = self.zipped_dir / f"{slug}.zip"
                self._create_zip(game["path"], zip_path)
                print(f"📦 Created backup: {game['name']}")
                created += 1
        
        # Find orphaned zips (no corresponding game)
        installed_slugs = {g["path"].name for g in games}
        orphaned = [slug for slug in zip_files.keys() if slug not in installed_slugs]
        
        if orphaned:
            print(f"\n⚠️  Found {len(orphaned)} orphaned zip(s) (no matching game):")
            for slug in orphaned:
                print(f"  - {slug}.zip")
            
            response = input("\nDelete orphaned zips? [y/N]: ")
            if response.lower() == 'y':
                for slug in orphaned:
                    zip_files[slug].unlink()
                    print(f"🗑️  Deleted: {slug}.zip")
                    removed += 1
        
        print(f"\n✅ Sync complete:")
        print(f"   Created: {created}")
        print(f"   Removed: {removed}")
    
    def _compute_game_hash(self, game_json_path: Path) -> str:
        """Compute a hash of the game.json content for duplicate detection"""
        import hashlib
        try:
            with open(game_json_path, 'r') as f:
                # Sort keys to ensure consistent hashing
                metadata = json.load(f)
                # Create normalized string representation
                normalized = json.dumps(metadata, sort_keys=True)
                return hashlib.md5(normalized.encode()).hexdigest()
        except Exception:
            return ""
    
    def find_duplicates(self):
        """Find and optionally remove duplicate games (identical game.json)"""
        games = self._get_all_games()
        
        if len(games) < 2:
            print("ℹ️  Need at least 2 games to check for duplicates.")
            return
        
        print("🔍 Scanning for duplicate games...\n")
        
        # Group games by their game.json hash
        hash_to_games = {}
        for game in games:
            game_json = game["path"] / "game.json"
            game_hash = self._compute_game_hash(game_json)
            
            if game_hash:
                if game_hash not in hash_to_games:
                    hash_to_games[game_hash] = []
                hash_to_games[game_hash].append(game)
        
        # Find duplicates
        duplicates = {h: g for h, g in hash_to_games.items() if len(g) > 1}
        
        if not duplicates:
            print("✅ No duplicate games found.")
            return
        
        print(f"⚠️  Found {len(duplicates)} set(s) of duplicates:\n")
        
        total_dupes = 0
        for game_hash, dupe_games in duplicates.items():
            name = dupe_games[0]["metadata"].get("name", "Unknown")
            author = dupe_games[0]["metadata"].get("author", "Unknown")
            version = dupe_games[0]["metadata"].get("version", "?")
            
            print(f"📦 {name} v{version} by {author}")
            print(f"   Found in {len(dupe_games)} locations:")
            
            for i, game in enumerate(dupe_games, 1):
                slug = game["path"].name
                print(f"   [{i}] {slug}")
            
            total_dupes += len(dupe_games) - 1  # Don't count the one we'll keep
            print()
        
        print(f"Total duplicate copies: {total_dupes}\n")
        
        response = input("Remove duplicates? (keeps first instance of each) [y/N]: ")
        
        if response.lower() != 'y':
            print("Cancelled.")
            return
        
        print()
        removed = 0
        
        for game_hash, dupe_games in duplicates.items():
            name = dupe_games[0]["metadata"].get("name", "Unknown")
            
            # Keep the first one, remove the rest
            keep = dupe_games[0]
            to_remove = dupe_games[1:]
            
            print(f"📦 {name}")
            print(f"   Keeping: {keep['path'].name}")
            
            for game in to_remove:
                slug = game["path"].name
                game_path = game["path"]
                zip_path = self.zipped_dir / f"{slug}.zip"
                
                # Remove game directory
                shutil.rmtree(game_path)
                
                # Remove zip backup if exists
                if zip_path.exists():
                    zip_path.unlink()
                
                print(f"   Removed: {slug}")
                removed += 1
            
            print()
        
        print("=" * 50)
        print(f"✅ Removed {removed} duplicate(s)")
        print(f"💾 Kept {len(duplicates)} unique game(s)")
    
    def check_runtimes(self):
        """Check which language runtimes are available"""
        print("🔧 Language Runtime Status:\n")
        
        for lang, config in sorted(self.runtimes.items()):
            available = self._check_runtime(lang)
            status = "✓ Available" if available else "✗ Not found"
            print(f"  {lang.ljust(12)} ({config['cmd'].ljust(10)}) - {status}")
    
    def vibify(self, directory: str):
        """Convert a directory into a clvibe game by creating game.json"""
        game_dir = Path(directory)
        
        if not game_dir.exists() or not game_dir.is_dir():
            print(f"❌ Directory not found: {directory}")
            return
        
        game_json = game_dir / "game.json"
        if game_json.exists():
            print(f"⚠️  game.json already exists in {game_dir.name}")
            response = input("Overwrite? [y/N]: ")
            if response.lower() != 'y':
                print("Cancelled.")
                return
        
        print("✨ Let's vibify this game! ✨\n")
        print("🎮 Game Vibification Questionnaire\n")
        print("=" * 50)
        
        # Detect language by scanning for script files
        detected_lang = self._detect_language(game_dir)
        
        if detected_lang:
            print(f"📝 Detected language: {detected_lang}")
            lang = detected_lang
        else:
            print("⚠️  Could not auto-detect language")
            print("\nAvailable languages:")
            for i, (lang_name, config) in enumerate(sorted(self.runtimes.items()), 1):
                print(f"  {i}. {lang_name} ({config['ext']})")
            
            lang_choice = input("\nEnter language name or number: ").strip()
            
            # Try as number first
            try:
                idx = int(lang_choice) - 1
                lang_names = sorted(self.runtimes.keys())
                if 0 <= idx < len(lang_names):
                    lang = lang_names[idx]
                else:
                    print("❌ Invalid selection")
                    return
            except ValueError:
                # Use as language name
                if lang_choice.lower() in self.runtimes:
                    lang = lang_choice.lower()
                else:
                    print(f"❌ Unknown language: {lang_choice}")
                    return
        
        print()
        
        # Find script files for the detected/selected language
        ext = self.runtimes[lang]["ext"]
        script_files = sorted([f for f in game_dir.rglob(f"*{ext}") if f.is_file()])
        
        if not script_files:
            print(f"❌ No {ext} files found in directory")
            return
        
        # Select main file
        print(f"📂 Found {len(script_files)} {lang} file(s):\n")
        
        for i, script in enumerate(script_files, 1):
            rel_path = script.relative_to(game_dir)
            print(f"  {i}. {rel_path}")
        
        print()
        
        if len(script_files) == 1:
            main_file = script_files[0]
            print(f"✓ Auto-selected: {main_file.relative_to(game_dir)}")
        else:
            main_choice = input("Select main file (number or filename): ").strip()
            
            # Try as number
            try:
                idx = int(main_choice) - 1
                if 0 <= idx < len(script_files):
                    main_file = script_files[idx]
                else:
                    print("❌ Invalid selection")
                    return
            except ValueError:
                # Try as filename
                matches = [f for f in script_files if main_choice in str(f)]
                if len(matches) == 1:
                    main_file = matches[0]
                elif len(matches) > 1:
                    print(f"❌ Ambiguous filename. Multiple matches found.")
                    return
                else:
                    print(f"❌ File not found: {main_choice}")
                    return
        
        # Determine path field (if main file is in subdirectory)
        main_rel = main_file.relative_to(game_dir)
        if len(main_rel.parts) > 1:
            subpath = str(main_rel.parent)
        else:
            subpath = ""
        
        print()
        print("=" * 50)
        print("Now let's add some metadata! ✨\n")
        
        # Game name
        default_name = game_dir.name.replace("-", " ").replace("_", " ").title()
        game_name = input(f"Game name [{default_name}]: ").strip()
        if not game_name:
            game_name = default_name
        
        # Author
        author = input("Your name/handle [Anonymous]: ").strip()
        if not author:
            author = "Anonymous"
        
        # LLM used
        print("\nWhich AI helped create this game?")
        print("  1. Claude (Anthropic)")
        print("  2. GPT (OpenAI)")
        print("  3. Gemini (Google)")
        print("  4. Other")
        print("  5. Human-written (no AI)")
        
        llm_choice = input("\nSelect [1]: ").strip()
        
        llm_map = {
            "1": "Claude",
            "2": "GPT",
            "3": "Gemini",
            "4": None,
            "5": "Human"
        }
        
        if llm_choice in llm_map:
            llm = llm_map[llm_choice]
            if llm is None:
                llm = input("Enter AI name: ").strip() or "Unknown"
        else:
            llm = "Claude"  # Default
        
        # Version
        version = input("Version [1.0]: ").strip()
        if not version:
            version = "1.0"
        
        # Language version (optional)
        lang_version = input(f"Required {lang} version (optional): ").strip()
        
        # Create game.json
        metadata = {
            "name": game_name,
            "author": author,
            "llm": llm,
            "version": version,
            "lang": lang,
            "lang-version": lang_version,
            "path": subpath
        }
        
        print()
        print("=" * 50)
        print("📄 Generated game.json:\n")
        print(json.dumps(metadata, indent=2))
        print()
        
        response = input("Save this game.json? [Y/n]: ").strip().lower()
        if response and response != 'y':
            print("Cancelled.")
            return
        
        # Save game.json
        with open(game_json, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✅ Created: {game_json}")
        print()
        print("🎉 Game vibified! ✨")
        print()
        
        # Ask to install
        response = input("Install this game now? [Y/n]: ").strip().lower()
        if not response or response == 'y':
            print()
            self.install_game(str(game_dir))
    
    def _detect_language(self, directory: Path) -> Optional[str]:
        """Auto-detect programming language from files in directory"""
        # Count files by extension
        ext_counts = {}
        
        for file in directory.rglob("*"):
            if file.is_file():
                ext = file.suffix.lower()
                ext_counts[ext] = ext_counts.get(ext, 0) + 1
        
        # Find which language has the most matching files
        lang_scores = {}
        for lang, config in self.runtimes.items():
            ext = config["ext"]
            if ext in ext_counts:
                lang_scores[lang] = ext_counts[ext]
        
        if not lang_scores:
            return None
        
        # Return language with most files
        return max(lang_scores, key=lang_scores.get)


def main():
    parser = argparse.ArgumentParser(
        description="clvibe - CLI Game Manager for AI-generated games",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List installed games")
    list_parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed information")
    
    # Play command
    play_parser = subparsers.add_parser("play", help="Play a game")
    play_parser.add_argument("game", help="Game name or index number")
    
    # Install command
    install_parser = subparsers.add_parser("install", help="Install game(s) from any source")
    install_parser.add_argument("path", help="Path to game/collection directory, zip file, or URL")
    install_parser.add_argument("-c", "--collection", action="store_true", default=False, help="Force treat as collection (install all games found)")
    
    # Batch install command
    batch_install_parser = subparsers.add_parser("batch-install", help="Install multiple games")
    batch_install_parser.add_argument("path", help="Directory with games or text file with URLs")
    batch_install_parser.add_argument("-z", "--zipped", action="store_true", help="Install from zip files instead of directories")
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export a game as zip")
    export_parser.add_argument("game", help="Game name or index number")
    export_parser.add_argument("-o", "--output", help="Output zip file path")
    
    # Batch export command
    batch_export_parser = subparsers.add_parser("batch-export", help="Export all games to a directory")
    batch_export_parser.add_argument("output", help="Output directory path")
    batch_export_parser.add_argument("-u", "--unzipped", action="store_true", help="Export as directories instead of zip files")
    
    # Uninstall command
    uninstall_parser = subparsers.add_parser("uninstall", help="Uninstall a game")
    uninstall_parser.add_argument("game", help="Game name or index number")
    
    # Restore command
    restore_parser = subparsers.add_parser("restore", help="Restore a game from zip backup")
    restore_parser.add_argument("game", help="Game name or index number")
    
    # List zipped command
    subparsers.add_parser("list-zipped", help="List all zip backups")
    
    # Sync command
    subparsers.add_parser("sync", help="Sync zip backups with installed games")
    
    # Dedupe command
    subparsers.add_parser("dedupe", help="Find and remove duplicate games")
    
    # Vibify command
    vibify_parser = subparsers.add_parser("vibify", help="Convert a directory into a clvibe game")
    vibify_parser.add_argument("directory", help="Directory containing your game")
    
    # Check command
    subparsers.add_parser("check", help="Check available language runtimes")
    
    args = parser.parse_args()
    
    manager = ClvibeManager()
    
    if args.command == "list":
        manager.list_games(verbose=args.verbose)
    elif args.command == "play":
        manager.play_game(args.game)
    elif args.command == "install":
        force_coll = getattr(args, 'collection', False)
        manager.install_game(args.path, force_collection=force_coll)
    elif args.command == "batch-install":
        manager.batch_install(args.path, zipped=args.zipped)
    elif args.command == "export":
        manager.export_game(args.game, args.output)
    elif args.command == "batch-export":
        manager.batch_export(args.output, zipped=not args.unzipped)
    elif args.command == "uninstall":
        manager.uninstall_game(args.game)
    elif args.command == "restore":
        manager.restore_from_zip(args.game)
    elif args.command == "list-zipped":
        manager.list_zipped()
    elif args.command == "sync":
        manager.sync_zips()
    elif args.command == "dedupe":
        manager.find_duplicates()
    elif args.command == "check":
        manager.check_runtimes()
    elif args.command == "vibify":
        manager.vibify(args.directory)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()