# Scripts Directory

## Overview

This directory, `scripts/`, contains various helper scripts that are not directly part of the application but can be useful for setting up or configuring the user's environment. These scripts are designed to assist users in tasks like system configuration, troubleshooting, or performing specific setup actions that enhance the usability and functionality of the main application.

## Available Scripts

### sound_device_list.py

- **Purpose**: Lists all available sound devices on the system.
- **Use Case**: This script is particularly helpful for environments where the default sound device might not be appropriate or needs to be explicitly set. For example, on macOS, the default sound device may differ from the expected one, and this script can assist in identifying the correct device.
- **How to Use**: Run this script to output a list of all sound devices recognized by the `sounddevice` module. The output includes device names and indices, which can be used to configure the `AUDIO_SETTINGS["SOUND_DEVICE_DEVICE"]` option in the application's configuration file.

## Adding New Scripts

This directory is open for additions. If you develop or come across a script that can aid in system configuration, environment setup, or provide utility functions beneficial for users of this application, feel free to add it here. Ensure that each new script is accompanied by:

- Clear comments within the script explaining its purpose and usage.
- An update to this README file detailing the script's functionality and instructions.

## Usage Guidelines

Please note that the scripts in this directory are provided as-is and may require modifications to work in your specific environment. Please be sure to review and understand a script before running it.
