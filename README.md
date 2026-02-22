# S.T.A.L.K.E.R. 2 Ultimate Modpack Builder by Saymonn

**A comprehensive tool for creating custom modpacks for S.T.A.L.K.E.R. 2: Heart of Chornobyl**

## Overview

The S.T.A.L.K.E.R. 2 Ultimate Modpack Builder is a powerful Python application that allows players to easily create and install custom modpacks for S.T.A.L.K.E.R. 2. This tool combines multiple popular mods into a single, easy-to-use interface, letting you customize your game experience with just a few clicks.

### Key Features

- **Multiple Game Modifications**: Combine carry weight, weapon durability, stamina usage, day length, and trader behavior modifications
- **User-Friendly Interface**: Simple command-line interface suitable for both technical and non-technical users
- **Automatic Game File Extraction**: Extracts and modifies game files automatically
- **Custom and Preset Configurations**: Choose from predefined settings or create your own custom values
- **One-Click Installation**: Automatically installs mods to your game directory
- **Update-Resistant**: Built on game version 1.5.2 but adapts to newer versions by modifying current game files rather than relying on fixed templates

## Requirements

This mod requires a working Python 3 environment to function properly.

## Installation Guide

### Step 1: Install Python 3

1. **Download Python**: Go to [https://www.python.org/downloads/](https://www.python.org/downloads/)

2. **Get the Latest Version**: Click the yellow button "Download Python 3.x" (e.g., "Download Python 3.13.6")

3. **Run the Installer**: After downloading, run the Python installer

4. **Configure Installation**: When the installer opens, make sure to check these checkboxes:

   - ☑ **Use admin privileges when installing py.exe**
   - ☑ **Add python.exe to PATH**

5. **Install**: Click "Install Now"

6. **Verify Installation**: Open Command Prompt or PowerShell and type `python --version` to confirm Python is installed correctly

### Step 2: Download and Run the Modpack Builder

1. Download the S.T.A.L.K.E.R. 2 Ultimate Modpack Builder
2. Extract the files to a folder of your choice
3. Run the application by either:
   - **Double-clicking** on `main.py`
   - Or opening Windows PowerShell in the folder and running:
     ```
     python .\main.py
     ```

## How It Works

### Initial Setup

When you first run the application, it will:

1. **Locate Your Game**: The tool will ask you to locate your S.T.A.L.K.E.R. 2 installation directory
2. **Extract Game Files**: Extract the main game files (pakchunk0-Windows.pak) - this process takes 5-15 minutes and extracts ~300,000 files (~7GB of data)
3. **Ready to Mod**: Once extraction is complete, you can start creating modpacks

### Available Modules

#### 1. **Carry Weight Modifier**

- **Purpose**: Adjusts your maximum carrying capacity
- **Options**:
  - Preset weights from 81kg to 10,000kg
  - Custom weight configuration
  - Automatic threshold adjustments for movement penalties
- **Based on**: Adjustable Carry Weight mod by NickMillion

#### 2. **Weapon Durability Modifier**

- **Purpose**: Changes how quickly weapons degrade
- **Options**:
  - 2x, 3x, 5x, or 10x more durable weapons
  - Custom durability multipliers
  - Affects all weapon types
- **Based on**: Reasonable Weapon Degradation mod by VAXIS

#### 3. **Stamina Usage Modifier**

- **Purpose**: Adjusts stamina consumption for various actions
- **Configurable Actions**:
  - Sprinting
  - Jumping
  - Melee attacks (normal, strong, butstock)
  - Vaulting over obstacles
- **Based on**: Better Stamina Usage mod by J412536987

#### 4. **Day Length Modifier**

- **Purpose**: Changes the speed of in-game time passage
- **Options**:
  - Real-time (1:1 ratio)
  - Various preset speeds
  - Custom time coefficients
  - Affects day/night cycles
- **Based on**: Even Longer Days mod by JCaleb

#### 5. **Trader Durability Requirements**

- **Purpose**: Changes minimum item condition traders will accept
- **Options**:
  - Accept completely broken items (0% minimum)
  - Various durability thresholds
  - Custom percentage settings
- **Based on**: Sell Damaged Stuff mod by StalkerBoss

### Creating a Modpack

1. **Select Modules**: Choose which modifications you want to include
2. **Configure Each Module**: Set parameters for each selected module using either:
   - **Preset Configurations**: Pre-made settings for common preferences
   - **Custom Configurations**: Manually set specific values
3. **Build Modpack**: The tool automatically:
   - Applies all selected modifications
   - Creates a .pak file for easy installation
   - Generates an unpacked version for manual installation
4. **Install**: Optionally install the modpack directly to your game directory

### File Conflict Handling

The tool intelligently handles conflicts when multiple modules modify the same game files. When conflicts are detected, modules apply changes incrementally, with later modules preserving changes made by earlier ones.

## Troubleshooting

### "Mod Doesn't Work After Game Update?"

The modpack builder is designed to be update-resistant by working with your current game files rather than using fixed templates. However, if you experience issues after a game update:

1. **Re-extract Game Files**: Run the extraction process again to get the latest game files
2. **Rebuild Your Modpack**: Create your modpack again using the new extracted files
3. **Check Game Version**: Use the built-in game version checker to verify compatibility
4. **Clear Cache**: Use the "Clear Cache" option in settings if you encounter persistent issues

### Common Issues

**Python Not Found Error**:

- Ensure Python is properly installed and added to PATH
- Try running `python --version` in Command Prompt to verify installation

**Game Path Not Detected**:

- Manually set your game path in Settings
- Ensure you're pointing to the correct S.T.A.L.K.E.R. 2 installation folder

**Extraction Failed**:

- Ensure you have sufficient disk space (~7GB free)
- Run the application as administrator
- Check that your game files are not corrupted

**Mod Not Working In-Game**:

- Verify the .pak file is in the correct location: `[Game Directory]/Stalker2/Content/Paks/~mods/`
- Ensure no conflicting mods are installed
- Check that the game version matches your extracted files

## Acknowledgments

This tool is built upon the excellent work of several modding community members. Special thanks to:

### Original Mod Authors

**Better Stamina Usage (Longer Sprinting – Stamina Overhaul)**

- Author: J412536987
- Original Modification: [Nexus Mods Link](https://www.nexusmods.com/stalker2heartofchornobyl/mods/433)

**Even Longer Days**

- Author: JCaleb
- Original Modification: [Nexus Mods Link](https://www.nexusmods.com/stalker2heartofchornobyl/mods/47)

**Adjustable Carry Weight (Updated for Patch 1.1.2)**

- Author: NickMillion
- Original Modification: [Nexus Mods Link](https://www.nexusmods.com/stalker2heartofchornobyl/mods/53)

**Sell Damaged Stuff (UPDATED for 1.5.1)**

- Author: StalkerBoss
- Original Modification: [Nexus Mods Link](https://www.nexusmods.com/stalker2heartofchornobyl/mods/87)

**Reasonable Weapon Degradation**

- Author: VAXIS
- Original Modification: [Nexus Mods Link](https://www.nexusmods.com/stalker2heartofchornobyl/mods/33)

### Tools and Libraries

**repak**

- Author: trumank (Truman Kilen)
- Repository: [GitHub Link](https://github.com/trumank/repak)
- Description: A Rust library and CLI tool for working with Unreal Engine .pak files. Enables reading and writing .pak files with faster unpacking than standard UnrealPak and safe unpack/pack operations, including encryption and compression support.

## License and Legal

This tool is for educational and personal use only. All original mod concepts and implementations belong to their respective authors. The S.T.A.L.K.E.R. 2 game and all related assets are property of GSC Game World.

## Support

For issues, questions, or suggestions, please refer to the troubleshooting section above or check the application's built-in help system.

---

**Enjoy your enhanced S.T.A.L.K.E.R. 2 experience!**
