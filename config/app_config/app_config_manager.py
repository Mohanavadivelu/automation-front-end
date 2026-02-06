import os

class AppConfigManager:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AppConfigManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self.app_config_dir = os.path.dirname(os.path.abspath(__file__))
        self.projects_dir = os.path.join(self.app_config_dir, 'projects')
        self.settings_file = os.path.join(self.app_config_dir, 'settings.env')
        
        # Initial load
        default_project = self._get_persistent_default()
        self.load_project(default_project)
        
        self._initialized = True

    def _get_persistent_default(self):
        """Read settings.env to find DEFAULT_PROJECT."""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    for line in f:
                        if line.startswith("DEFAULT_PROJECT="):
                            return line.split("=", 1)[1].strip()
            except Exception:
                pass # Ignore errors, fallback
        
        # Fallback logic: return first available project or 'default'
        available = self.get_available_projects()
        if available:
            return available[0]
        return "default"

    def get_available_projects(self):
        """Return a list of available project names (files in projects/ dir)."""
        if not os.path.exists(self.projects_dir):
            return []
            
        projects = []
        for f in os.listdir(self.projects_dir):
            if f.endswith(".env"):
                projects.append(f[:-4]) # Remove .env extension
        return projects

    def set_default_project(self, project_name):
        """Update settings.env and reload configuration."""
        # 1. Update Persistent File
        with open(self.settings_file, 'w') as f:
            f.write(f"DEFAULT_PROJECT={project_name}\n")
            
        # 2. Reload
        self.load_project(project_name)

    def load_project(self, project_name):
        """Load configuration from specific project file."""
        config_path = os.path.join(self.projects_dir, f"{project_name}.env")
        
        # Reset current state
        self._global_map = {}
        # We need to clear old section attributes to avoid stale data
        # iterating over keys of __dict__ is unsafe while modifying, so list() it
        for attr in list(self.__dict__.keys()):
            # Crude way to clean up sections, assuming standard attributes start with _
            # or are specific system props. Better approach: track loaded sections.
            if not attr.startswith("_") and attr not in ['app_config_dir', 'projects_dir', 'settings_file']:
                delattr(self, attr)

        self._load_config_file(config_path)

    def _load_config_file(self, path):
        if not os.path.exists(path):
            # If explicit file missing, maybe warn? For now just return empty
            print(f"Warning: Config file not found at {path}")
            return

        current_section = None
        config_data = {}
        
        with open(path, 'r') as f:
            lines = f.readlines()
            
        in_comment = False
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Handle XML-style comments
            if in_comment:
                if "-->" in line:
                    in_comment = False
                continue

            if "<!--" in line:
                if "-->" in line:
                    # Inline/Single-line comment: Remove the comment part
                    start = line.find("<!--")
                    end = line.find("-->") + 3
                    line = (line[:start] + line[end:]).strip()
                    if not line:
                        continue
                else:
                    # Start of multi-line comment
                    in_comment = True
                    continue

            if line.startswith("#"):
                # Check for separator lines to ignore
                if "=====" in line:
                    continue
                
                # Parse section name from comment e.g., "# Device Configuration"
                section_title = line.lstrip("#").strip()
                if section_title:
                    # Remove spaces for class name compatibility
                    current_section = section_title.replace(" ", "")
                    # Reset/Init section data
                    if current_section not in config_data:
                        config_data[current_section] = {}
                continue

            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = self._parse_value(value.strip())
                
                # Add to global map for direct access
                self._global_map[key] = value
                
                # Add to section data
                if current_section:
                    config_data[current_section][key] = value

        # Create section classes and attach to self
        for section_name, data in config_data.items():
            # Create a dynamic class for the section
            section_class = type(section_name, (object,), data)
            setattr(self, section_name, section_class)

    def _parse_value(self, value):
        # Handle Booleans
        lower_val = value.lower()
        if lower_val in ('true', 'yes', 'on'):
            return True
        if lower_val in ('false', 'no', 'off'):
            return False
            
        # Handle Numbers
        if value.isdigit():
            return int(value)
        try:
            return float(value)
        except ValueError:
            pass
            
        # Return string
        return value

    def __call__(self, key):
        """Allow calling the instance to get a config value directly."""
        if key in self._global_map:
            return self._global_map[key]
        raise KeyError(f"Key '{key}' not found in configuration")
