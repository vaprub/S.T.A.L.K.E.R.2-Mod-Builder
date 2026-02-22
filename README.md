# S.T.A.L.K.E.R. 2 Ultimate Modpack Builder by Saymonn

**A comprehensive tool for creating custom modpacks for S.T.A.L.K.E.R. 2: Heart of Chornobyl**

[![English](https://img.shields.io/badge/lang-English-blue.svg)](README.md)
[![Русский](https://img.shields.io/badge/lang-Русский-red.svg)](README.ru.md)

## 📢 News

- **Version 2.0 released!** Now with full Russian localization and improved binary file support for game version 1.8.1+
- **Translation system added** - Interface now available in multiple languages
- **Vortex support** - Automatic creation of Vortex-compatible ZIP archives

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [🌍 Localization](#-localization)
- [Requirements](#requirements)
- [Installation Guide](#installation-guide)
- [How It Works](#how-it-works)
- [Available Modules](#available-modules)
- [Creating a Modpack](#creating-a-modpack)
- [File Conflict Handling](#file-conflict-handling)
- [Output Structure](#output-structure)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)
- [Acknowledgments](#acknowledgments)
- [License](#license)
- [Version History](#version-history)

## Overview

The S.T.A.L.K.E.R. 2 Ultimate Modpack Builder is a powerful Python application that allows players to easily create and install custom modpacks for S.T.A.L.K.E.R. 2: Heart of Chornobyl. This tool combines multiple popular mods into a single, easy-to-use interface, letting you customize your game experience with just a few clicks.

Whether you're a seasoned stalker looking for a tougher challenge or a newcomer wanting a more forgiving experience, this builder lets you fine-tune every aspect of gameplay.

## Key Features

* Multiple Game Modifications: Combine carry weight, weapon durability, stamina usage, day length, and trader behavior modifications
* User-Friendly Interface: Simple command-line interface suitable for both technical and non-technical users
* Automatic Game File Extraction: Extracts and modifies game files automatically - no manual file hunting
* Custom and Preset Configurations: Choose from predefined settings or create your own custom values
* One-Click Installation: Automatically installs mods to your game directory
* Update-Resistant: Built for game version 1.5.2 but adapts to newer versions by modifying current game files rather than using fixed templates
* Full Russian Localization: Complete Russian translation of the interface
* Vortex Support: Automatically creates ZIP archives compatible with Vortex mod manager
* Intelligent Conflict Resolution: Automatically handles when multiple modules modify the same files

## 🌍 Localization

Supported languages:
* 🇬🇧 English (en) - default
* 🇷🇺 Русский (ru) - fully translated
* 🇺🇦 Українська (uk) - in development
* 🇩🇪 Deutsch (de) - in development
* 🇫🇷 Français (fr) - in development
* 🇪🇸 Español (es) - in development
* 🇵🇱 Polski (pl) - in development
* 🇨🇳 中文 (zh) - in development
* 🇯🇵 日本語 (ja) - in development
* 🇰🇷 한국어 (ko) - in development
* 🇮🇹 Italiano (it) - in development
* 🇨🇿 Čeština (cs) - in development

The language is automatically detected from your system. You can change it in Settings -> Language Settings.

## Requirements

* Python 3.6 or higher - [Download Python](https://www.python.org/downloads/)
* Windows 10/11 (primary support) or Linux/Mac (should work but not extensively tested)
* S.T.A.L.K.E.R. 2: Heart of Chornobyl installed
* ~7GB free disk space for file extraction

## Installation Guide

### Step 1: Install Python 3

1. Download Python: Go to [python.org](https://www.python.org/downloads/)
2. Get the Latest Version: Click the yellow button "Download Python 3.x" (e.g., "Download Python 3.13.6")
3. Run the Installer: After downloading, run the Python installer
4. Configure Installation: When the installer opens, make sure to check these checkboxes:
   * Use admin privileges when installing py.exe
   * Add python.exe to PATH
5. Install: Click "Install Now"
6. Verify Installation: Open Command Prompt or PowerShell and type python --version to confirm Python is installed correctly

### Step 2: Download and Run the Modpack Builder

1. Download the S.T.A.L.K.E.R. 2 Ultimate Modpack Builder from [GitHub](https://github.com/vaprub/S.T.A.L.K.E.R.2-Mod-Builder)
2. Extract the files to a folder of your choice
3. Run the application by either:
   * Double-clicking on main.py
   * Or using the provided launcher:
     - Windows: Double-click run.bat
     - Linux/Mac: Run ./run.sh in terminal
   * Or open terminal and run:

python main.py

## How It Works

### Initial Setup

When you first run the application, it will:

1. Locate Your Game: The tool will ask you to locate your S.T.A.L.K.E.R. 2 installation directory
2. Extract Game Files: Extract the main game files (pakchunk0-Windows.pak) - this process takes 5-15 minutes and extracts ~300,000 files (~7GB of data)
3. Ready to Mod: Once extraction is complete, you can start creating modpacks

## Available Modules

### 1. Carry Weight Modifier

* Purpose: Adjusts your maximum carrying capacity
* Options:
  - Preset weights from 81kg to 10,000kg
  - Custom weight configuration
  - Automatic threshold adjustments for movement penalties
* Based on: Adjustable Carry Weight mod by NickMillion

### 2. Weapon Durability Modifier

* Purpose: Changes how quickly weapons degrade
* Options:
  - 2x, 3x, 5x, or 10x more durable weapons
  - Custom durability multipliers
  - Affects all weapon types
* Based on: Reasonable Weapon Degradation mod by VAXIS

### 3. Stamina Usage Modifier

* Purpose: Adjusts stamina consumption for various actions
* Configurable Actions:
  - Sprinting
  - Jumping
  - Melee attacks (normal, strong, buttstock)
  - Vaulting over obstacles
* Based on: Better Stamina Usage mod by J412536987

### 4. Day Length Modifier

* Purpose: Changes the speed of in-game time passage
* Options:
  - Real-time (1:1 ratio)
  - Various preset speeds
  - Custom time coefficients
  - Affects day/night cycles
* Based on: Even Longer Days mod by JCaleb

### 5. Trader Durability Requirements

* Purpose: Changes minimum item condition traders will accept
* Options:
  - Accept completely broken items (0% minimum)
  - Various durability thresholds
  - Custom percentage settings
* Based on: Sell Damaged Stuff mod by StalkerBoss

## Creating a Modpack

1. Select Modules: Choose which modifications you want to include
2. Configure Each Module: Set parameters for each selected module using either:
   * Preset Configurations: Pre-made settings for common preferences
   * Custom Configurations: Manually set specific values
3. Build Modpack: The tool automatically:
   * Applies all selected modifications
   * Creates a .pak file for easy installation
   * Generates an unpacked version for manual installation
   * Creates a Vortex-compatible ZIP archive
4. Install: Optionally install the modpack directly to your game directory

## File Conflict Handling

The tool intelligently handles conflicts when multiple modules modify the same game files. When conflicts are detected, modules apply changes incrementally, with later modules preserving changes made by earlier ones.

## Output Structure

After building a modpack, you'll find the following in the output/ directory:
output/
├── paks/
│ └── YourModName.pak # Manual installation
├── mods/
│ └── YourModName/ # Unpacked version
└── vortex/
└── YourModName_Vortex.zip # Vortex-compatible archive

## Troubleshooting

### "Mod Doesn't Work After Game Update?"

The modpack builder is designed to be update-resistant by working with your current game files rather than using fixed templates. However, if you experience issues after a game update:

1. Re-extract Game Files: Run the extraction process again to get the latest game files
2. Rebuild Your Modpack: Create your modpack again using the new extracted files
3. Check Game Version: Use the built-in game version checker to verify compatibility
4. Clear Cache: Use the "Clear Cache" option in settings if you encounter persistent issues

### FAQ

Q: How much disk space is needed?
A: About 7GB for extraction.

Q: Is this safe for my saves?
A: Yes, mods don't affect save files.

Q: Can I use multiple mods at once?
A: Yes, the builder automatically merges selected modules.

Q: Will I get banned for using mods?
A: This is a single-player game, mods are allowed.

Q: How do I change the language?
A: Go to Settings -> Language Settings and select your preferred language.

Q: Can I contribute translations for my language?
A: Yes! Check the locales/ folder and see tools/compile_po.py for instructions.

### Common Issues

Python Not Found Error:

* Ensure Python is properly installed and added to PATH
* Try running python --version in Command Prompt to verify installation
* Use the provided run.bat (Windows) or run.sh (Linux/Mac) launchers

Game Path Not Detected:

* Manually set your game path in Settings
* Ensure you're pointing to the correct S.T.A.L.K.E.R. 2 installation folder
* The correct path should contain Stalker2/Binaries/Win64/Stalker2-Win64-Shipping.exe

Extraction Failed:

* Ensure you have sufficient disk space (~7GB free)
* Run the application as administrator
* Check that your game files are not corrupted
* Verify your game installation through Steam/Epic/GOG

Mod Not Working In-Game:

* Verify the .pak file is in the correct location: [Game Directory]/Stalker2/Content/Paks/~mods/
* Ensure no conflicting mods are installed
* Check that the game version matches your extracted files
* Try reinstalling the mod after clearing the cache

Translations Not Working:

* Run python tools/compile_po.py status to check translation status
* Ensure .mo files are compiled (run python tools/compile_po.py compile)
* Check that language files exist in locales/[lang]/LC_MESSAGES/

## Acknowledgments

This tool is built upon the excellent work of several modding community members. Special thanks to:

### Original Mod Authors

| Mod | Author | Original Work |
|-----|--------|---------------|
| Better Stamina Usage | J412536987 | [Nexus Mods Link](https://www.nexusmods.com/stalker2heartofchornobyl/mods/48) |
| Even Longer Days | JCaleb | [Nexus Mods Link](https://www.nexusmods.com/stalker2heartofchornobyl/mods/74) |
| Adjustable Carry Weight | NickMillion | [Nexus Mods Link](https://www.nexusmods.com/stalker2heartofchornobyl/mods/53) |
| Sell Damaged Stuff | StalkerBoss | [Nexus Mods Link](https://www.nexusmods.com/stalker2heartofchornobyl/mods/101) |
| Reasonable Weapon Degradation | VAXIS | [Nexus Mods Link](https://www.nexusmods.com/stalker2heartofchornobyl/mods/62) |

### Tools and Libraries

repak
* Author: trumank (Truman Kilen)
* Repository: [GitHub Link](https://github.com/trumank/repak)
* Description: A Rust library and CLI tool for working with Unreal Engine .pak files

### Translators

* Russian Translation: vaprub

## License and Legal

This tool is for educational and personal use only. All original mod concepts and implementations belong to their respective authors. The S.T.A.L.K.E.R. 2 game and all related assets are property of GSC Game World.

## Support

For issues, questions, or suggestions:

* Check the Troubleshooting section
* Use the built-in help system in the application
* Create an issue on [GitHub](https://github.com/vaprub/S.T.A.L.K.E.R.2-Mod-Builder/issues)
* Contact the maintainers

## Version History

v2.0 (February 2026)
* Added full Russian localization
* Improved binary file support for game version 1.8.1+
* Added Vortex-compatible ZIP creation
* Enhanced game version detection
* Multiple bug fixes and performance improvements

v1.0 (January 2026)
* Initial release
* Basic module support
* Game file extraction

---

**Enjoy your enhanced S.T.A.L.K.E.R. 2 experience!**

## Project Statistics

* Version: 2.0
* License: MIT
* Language: Python 100%
* Author: Saymonn
* Localization: vaprub
* GitHub: [vaprub/S.T.A.L.K.E.R.2-Mod-Builder](https://github.com/vaprub/S.T.A.L.K.E.R.2-Mod-Builder)

---

*Made with ❤️ for the S.T.A.L.K.E.R. community*
