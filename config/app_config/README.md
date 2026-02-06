# AppConfigManager Developer Guide

This guide explains how to manage and modify the **Multi-Project Configuration** for the automation framework.

## Directory Structure
```text
config/app_config/
├── app_config_manager.py   # The Singleton Manager
├── settings.env            # Persistent storage (Stores DEFAULT_PROJECT)
└── projects/               # Directory containing Project Configurations
    ├── ferrari.env         # Configuration for Ferrari project
    ├── audi.env            # Configuration for Audi project
    └── ...
```

## 1. Projects
Each project has its own `.env` file located in the `projects/` directory.

### Adding a New Project
1. Create a new file `projects/<project_name>.env`.
2. Add your configuration sections and keys.

### Configuration Format
Files use a standard `KEY=VALUE` format with **Section Headers**.

```ini
# =========================
# Device Configuration
# =========================
ADB_DEVICE_1_ID=4B091VDAQ000F3

# =========================
# Project Configuration
# =========================
EXECUTE_GROUP=FERRARI_PCTS
<!-- SOME_KEY=IGNORED_VALUE -->   <-- XML-style comments are ignored
```

## 2. Dynamic Switching
The `AppConfigManager` supports switching projects at runtime. The selection is **persistent** (saved to `settings.env`).

### API Usage
```python
from config.app_config.app_config_manager import AppConfigManager

config = AppConfigManager()

# 1. Get List of Available Projects
# Returns: ['ferrari', 'audi']
projects = config.get_available_projects()

# 2. Switch Project
# This updates settings.env and reloads the configuration immediately.
config.set_default_project("audi")

# 3. Access Config Values
print(config.ProjectConfiguration.EXECUTE_GROUP)
```

## 3. Class Names Logic
The Manager dynamically creates classes based on Section Headers in the loaded `.env` file.
- `# Device Configuration` -> `config.DeviceConfiguration`
- `# Project Configuration` -> `config.ProjectConfiguration`

## 4. Data Types
The manager automatically detects:
- **Booleans**: `TRUE`, `FALSE`, `YES`, `NO`, `ON`, `OFF` (case-insensitive).
- **Integers**: `123`, `0`.
- **Floats**: `12.34`.
- **Strings**: Everything else.
