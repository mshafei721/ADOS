"""
Tests for ADOS Configuration Loader
"""

import pytest
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config_loader import ConfigLoader, CrewConfig, load_config


class TestConfigLoader:
    """Test suite for configuration loader"""
    
    def test_load_crews_config(self):
        """Test loading crews configuration"""
        loader = ConfigLoader()
        crews = loader.load_crews_config()
        
        # Verify all 6 crews are loaded
        assert len(crews) == 6
        assert all(crew in crews for crew in [
            'orchestrator', 'backend', 'security', 
            'quality', 'integration', 'deployment'
        ])
        
        # Verify crew structure
        for crew_name, crew_config in crews.items():
            assert isinstance(crew_config, CrewConfig)
            assert crew_config.goal
            assert len(crew_config.constraints) > 0
            assert len(crew_config.tools) > 0
    
    def test_orchestrator_crew_config(self):
        """Test specific orchestrator crew configuration"""
        loader = ConfigLoader()
        orchestrator = loader.get_crew_config('orchestrator')
        
        assert orchestrator is not None
        assert "Master coordination" in orchestrator.goal
        assert len(orchestrator.dependencies) == 0  # No dependencies
        assert 'task_decomposer' in orchestrator.tools
        assert 'memory_writer' in orchestrator.tools
    
    def test_backend_crew_dependencies(self):
        """Test backend crew dependencies"""
        loader = ConfigLoader()
        backend = loader.get_crew_config('backend')
        
        assert backend is not None
        assert 'security' in backend.dependencies
        assert 'orchestrator' in backend.dependencies
        assert 'codegen.fastapi_boilerplate' in backend.tools
    
    def test_config_validation(self):
        """Test configuration validation"""
        loader = ConfigLoader()
        validation = loader.validate_config_integrity()
        
        assert validation['valid'] == True
        assert len(validation['errors']) == 0
        
        # Warnings are expected at this stage (no agents.yaml yet)
        # Just verify the structure is correct
        assert isinstance(validation['warnings'], list)
    
    def test_get_all_config(self):
        """Test getting all configuration"""
        loader = ConfigLoader()
        all_config = loader.get_all_config()
        
        assert 'crews' in all_config
        assert 'agents' in all_config
        assert 'tech_stack' in all_config
        assert 'system_settings' in all_config
        assert 'validation' in all_config
        
        assert len(all_config['crews']) == 6


if __name__ == "__main__":
    # Run basic tests
    test = TestConfigLoader()
    
    print("Testing crews configuration loading...")
    test.test_load_crews_config()
    print("✓ Crews loaded successfully")
    
    print("\nTesting orchestrator configuration...")
    test.test_orchestrator_crew_config()
    print("✓ Orchestrator config validated")
    
    print("\nTesting backend dependencies...")
    test.test_backend_crew_dependencies()
    print("✓ Backend dependencies validated")
    
    print("\nTesting configuration validation...")
    test.test_config_validation()
    print("✓ Configuration validation passed")
    
    print("\nTesting get all config...")
    test.test_get_all_config()
    print("✓ All config retrieval successful")
    
    print("\n✅ All tests passed!")