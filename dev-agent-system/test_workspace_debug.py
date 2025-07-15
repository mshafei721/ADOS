"""
Debug workspace validation
"""

from pathlib import Path
import sys
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config.config_loader import ConfigLoader

loader = ConfigLoader()
validation = loader.validate_workspace_setup()

print("Workspace validation results:")
print(json.dumps(validation, indent=2))

print("\nWorkspace config:")
workspace_config = loader.get_workspace_config()
print(json.dumps(workspace_config, indent=2))

print("\nCommunication channels:")
channels = loader.get_communication_channels()
print(json.dumps(channels, indent=2))

print("\nChecking file existence:")
for channel_name, channel_path in channels.items():
    file_path = Path(channel_path)
    print(f"  {channel_name}: {channel_path} - exists: {file_path.exists()}")