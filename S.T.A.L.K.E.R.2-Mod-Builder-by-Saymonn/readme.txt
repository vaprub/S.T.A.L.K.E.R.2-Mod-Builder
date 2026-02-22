S.T.A.L.K.E.R. 2 Ultimate Modpack Builder by Saymonn

A comprehensive tool for creating custom modpacks for S.T.A.L.K.E.R. 2: Heart of Chornobyl

Overview

The S.T.A.L.K.E.R. 2 Ultimate Modpack Builder is a powerful Python application that allows players to easily create and install custom modpacks for S.T.A.L.K.E.R. 2. This tool combines multiple popular mods into a single, easy-to-use interface, letting you customize your game experience with just a few clicks.

Key Features

- Multiple Game Modifications: Combine carry weight, weapon durability, stamina usage, day length, and trader behavior modifications
- User-Friendly Interface: Simple command-line interface suitable for both technical and non-technical users
- Automatic Game File Extraction: Extracts and modifies game files automatically
- Custom and Preset Configurations: Choose from predefined settings or create your own custom values
- One-Click Installation: Automatically installs mods to your game directory
- Update-Resistant: Built on game version 1.5.2 but adapts to newer versions by modifying current game files rather than relying on fixed templates

Requirements

This mod requires a working Python 3 environment to function properly.

Installation Guide

Step 1: Install Python 3

1. Download Python from: https://www.python.org/downloads/
2. Get the latest version (e.g., "Download Python 3.13.6")
3. Run the installer
4. Configure installation:
   - Use admin privileges when installing py.exe
   - Add python.exe to PATH
5. Click "Install Now"
6. Verify installation: open Command Prompt or PowerShell and run:
   python --version

Step 2: Download and Run the Modpack Builder

1. Download the S.T.A.L.K.E.R. 2 Ultimate Modpack Builder
2. Extract the files to a folder
3. Run the application by:
   - Double-clicking main.py
   - Or opening PowerShell in the folder and running:
     python .\main.py

How It Works

Initial Setup

When first run, the application will:
1. Locate your S.T.A.L.K.E.R. 2 installation directory
2. Extract main game files (pakchunk0-Windows.pak) — about 300,000 files (~7GB), taking 5-15 minutes
3. Allow you to start creating modpacks

Available Modules

1. Carry Weight Modifier
   - Adjusts maximum carrying capacity
   - Options: preset weights 81kg–10,000kg, custom, automatic penalty adjustments
   - Based on: Adjustable Carry Weight by NickMillion

2. Weapon Durability Modifier
   - Changes weapon degradation rate
   - Options: 2x, 3x, 5x, 10x durability, or custom
   - Based on: Reasonable Weapon Degradation by VAXIS

3. Stamina Usage Modifier
   - Adjusts stamina consumption
   - Actions: sprint, jump, melee, vault
   - Based on: Better Stamina Usage by J412536987

4. Day Length Modifier
   - Adjusts in-game time speed
   - Options: real-time, presets, custom coefficients
   - Based on: Even Longer Days by JCaleb

5. Trader Durability Requirements
   - Changes minimum item condition traders accept
   - Options: accept broken items (0%), thresholds, custom %
   - Based on: Sell Damaged Stuff by StalkerBoss

Creating a Modpack

1. Select modules
2. Configure each module (preset or custom)
3. Build modpack — tool applies modifications, creates .pak, and optional unpacked version
4. Install — optionally to game directory

File Conflict Handling

Conflicts between modules modifying the same file are resolved incrementally, preserving earlier changes.

Troubleshooting

Mod Doesn't Work After Game Update?
- Re-extract game files
- Rebuild modpack
- Check game version
- Clear cache in settings

Common Issues:

Python Not Found:
- Ensure Python is installed and in PATH
- Check with: python --version

Game Path Not Detected:
- Set manually in Settings
- Point to correct installation folder

Extraction Failed:
- Ensure ~7GB free space
- Run as administrator
- Verify game files integrity

Mod Not Working:
- Verify .pak file is in [Game Directory]/Stalker2/Content/Paks/~mods/
- Remove conflicting mods
- Match game version to extracted files

Acknowledgments

Original Mod Authors:
- Better Stamina Usage (J412536987)
- Even Longer Days (JCaleb)
- Adjustable Carry Weight (NickMillion)
- Sell Damaged Stuff (StalkerBoss)
- Reasonable Weapon Degradation (VAXIS)

Tools and Libraries:
- repak by trumank (Truman Kilen), Rust-based Unreal Engine .pak file tool
  https://github.com/trumank/repak

License and Legal
For educational and personal use only. All mod concepts and implementations belong to original authors. S.T.A.L.K.E.R. 2 and assets are property of GSC Game World.

Support
Refer to troubleshooting or in-app help system.

Enjoy your enhanced S.T.A.L.K.E.R. 2 experience!
