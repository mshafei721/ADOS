"""
Test workspace configuration integration
"""

import pytest
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config_loader import ConfigLoader


class TestWorkspaceConfig:
    """Test suite for workspace configuration"""
    
    def test_workspace_config_loading(self):
        """Test loading workspace configuration"""
        loader = ConfigLoader()
        workspace_config = loader.get_workspace_config()
        
        assert workspace_config is not None
        assert workspace_config.get("directory") == "./workspace"
        assert "inheritance" in workspace_config
        assert workspace_config["inheritance"]["source"] == "../.devdocs/memory-bank"
    
    def test_communication_channels(self):
        """Test communication channels configuration"""
        loader = ConfigLoader()
        channels = loader.get_communication_channels()
        
        assert channels is not None
        assert channels.get("task_queue") == "./workspace/todo.md"
        assert channels.get("active_context") == "./workspace/activeContext.md"
        assert channels.get("progress_log") == "./workspace/progress.md"
        assert channels.get("tech_context") == "./workspace/techContext.md"
        assert channels.get("master_plan") == "../.devdocs/memory-bank/PLAN.md"
    
    def test_workspace_validation(self):
        """Test workspace validation"""
        loader = ConfigLoader()
        validation = loader.validate_workspace_setup()
        
        assert validation["valid"] == True
        assert validation["workspace_ready"] == True
        assert len(validation["errors"]) == 0
        
        # Should have minimal warnings since we just created the workspace
        print(f"Workspace validation warnings: {validation['warnings']}")
    
    def test_workspace_files_exist(self):
        """Test that workspace files exist"""
        workspace_dir = Path("./workspace")
        
        assert workspace_dir.exists(), "Workspace directory should exist"
        
        required_files = ["todo.md", "activeContext.md", "progress.md", "techContext.md"]
        for file_name in required_files:
            file_path = workspace_dir / file_name
            assert file_path.exists(), f"Workspace file {file_name} should exist"
    
    def test_integration_with_full_config(self):
        """Test workspace integration with full configuration"""
        loader = ConfigLoader()
        all_config = loader.get_all_config()
        
        assert "workspace" in all_config
        assert "communication_channels" in all_config
        assert "workspace_validation" in all_config
        
        # Check workspace validation results
        workspace_validation = all_config["workspace_validation"]
        assert workspace_validation["valid"] == True
        assert workspace_validation["workspace_ready"] == True
    
    def test_workspace_inheritance_config(self):
        """Test workspace inheritance configuration"""
        loader = ConfigLoader()
        workspace_config = loader.get_workspace_config()
        
        inheritance = workspace_config.get("inheritance", {})
        assert inheritance["source"] == "../.devdocs/memory-bank"
        assert inheritance["sync_interval_seconds"] == 30
        assert "PLAN.md" in inheritance["read_only_files"]
        assert "CLAUDE.md" in inheritance["read_only_files"]
        assert "ADOS_Framework.md" in inheritance["read_only_files"]


def test_workspace_content_inheritance():
    """Test that workspace files have proper content inheritance"""
    workspace_dir = Path("./workspace")
    
    # Test todo.md content
    todo_file = workspace_dir / "todo.md"
    with open(todo_file, 'r') as f:
        todo_content = f.read()
    assert "Agent Task Queue" in todo_content
    assert "inherited from the main PLAN.md" in todo_content
    
    # Test activeContext.md content
    context_file = workspace_dir / "activeContext.md"
    with open(context_file, 'r') as f:
        context_content = f.read()
    assert "Active Context - Agent Workspace" in context_content
    assert "Inherited from main" in context_content
    
    # Test progress.md content
    progress_file = workspace_dir / "progress.md"
    with open(progress_file, 'r') as f:
        progress_content = f.read()
    assert "Agent Progress Log" in progress_content
    assert "Inherits from" in progress_content
    
    # Test techContext.md content
    tech_file = workspace_dir / "techContext.md"
    with open(tech_file, 'r') as f:
        tech_content = f.read()
    assert "Technical Context - Agent Workspace" in tech_content
    assert "Inherited from" in tech_content


if __name__ == "__main__":
    # Run basic tests
    test = TestWorkspaceConfig()
    
    print("Testing workspace configuration loading...")
    test.test_workspace_config_loading()
    print("✓ Workspace config loaded successfully")
    
    print("\nTesting communication channels...")
    test.test_communication_channels()
    print("✓ Communication channels configured correctly")
    
    print("\nTesting workspace validation...")
    test.test_workspace_validation()
    print("✓ Workspace validation passed")
    
    print("\nTesting workspace files existence...")
    test.test_workspace_files_exist()
    print("✓ All workspace files exist")
    
    print("\nTesting integration with full config...")
    test.test_integration_with_full_config()
    print("✓ Workspace integration with full config works")
    
    print("\nTesting workspace inheritance configuration...")
    test.test_workspace_inheritance_config()
    print("✓ Workspace inheritance properly configured")
    
    print("\nTesting workspace content inheritance...")
    test_workspace_content_inheritance()
    print("✓ Workspace content inheritance validated")
    
    print("\n✅ All workspace tests passed!")