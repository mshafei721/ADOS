"""
Integration tests for memory coordinator with orchestrator
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

from config.config_loader import ConfigLoader
from orchestrator.main import ADOSOrchestrator
from orchestrator.memory_coordinator import MemoryCoordinator


class TestMemoryIntegration:
    """Integration tests for memory system with orchestrator"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def mock_config_dir(self, temp_dir):
        """Create mock config directory with required files"""
        config_dir = temp_dir / "config"
        config_dir.mkdir()
        
        # Create system_settings.json
        system_settings = {
            "memory": {
                "vector_db": {
                    "provider": "chromadb",
                    "persist_directory": str(temp_dir / "memory" / "global_kb" / "chroma"),
                    "collection_name": "ados_memory"
                },
                "crew_memory": {
                    "type": "json",
                    "directory": str(temp_dir / "memory" / "crew_memory"),
                    "max_size_mb": 100
                },
                "session_memory": {
                    "enabled": True,
                    "max_entries": 1000
                }
            }
        }
        
        with open(config_dir / "system_settings.json", 'w') as f:
            import json
            json.dump(system_settings, f)
        
        # Create empty crews and agents config
        with open(config_dir / "crews.json", 'w') as f:
            json.dump({"test_crew": {"name": "test_crew", "description": "Test crew"}}, f)
        
        with open(config_dir / "agents.json", 'w') as f:
            json.dump({"test_agent": {"name": "test_agent", "role": "test", "crew": "test_crew"}}, f)
        
        return config_dir

    @patch('chromadb.PersistentClient')
    @patch('chromadb.Settings')
    def test_orchestrator_memory_initialization(self, mock_settings, mock_client_class, mock_config_dir):
        """Test that orchestrator properly initializes memory system"""
        # Setup mocks
        mock_client = Mock()
        mock_collection = Mock()
        mock_client_class.return_value = mock_client
        mock_client.create_collection.return_value = mock_collection
        mock_client.get_collection.side_effect = Exception("Collection not found")
        
        # Create orchestrator with mocked crews/agents
        orchestrator = ADOSOrchestrator(config_dir=mock_config_dir)
        
        # Mock crew and agent creation to avoid complex setup
        with patch.object(orchestrator, '_initialize_crews'), \
             patch.object(orchestrator, '_initialize_agents'), \
             patch.object(orchestrator, '_validate_configurations'):
            
            # Initialize orchestrator
            result = orchestrator.initialize()
            
            # Verify initialization success
            assert result is True
            assert orchestrator.is_initialized is True
            assert orchestrator.memory_coordinator.is_initialized is True
            
            # Verify memory coordinator was properly initialized
            assert orchestrator.memory_coordinator.vector_db == mock_client
            assert orchestrator.memory_coordinator.collection == mock_collection

    @patch('chromadb.PersistentClient')
    @patch('chromadb.Settings')
    def test_orchestrator_memory_status(self, mock_settings, mock_client_class, mock_config_dir):
        """Test that orchestrator system status includes memory information"""
        # Setup mocks
        mock_client = Mock()
        mock_collection = Mock()
        mock_collection.name = "ados_memory"
        mock_collection.count.return_value = 10
        mock_client_class.return_value = mock_client
        mock_client.create_collection.return_value = mock_collection
        mock_client.get_collection.side_effect = Exception("Collection not found")
        
        # Create orchestrator
        orchestrator = ADOSOrchestrator(config_dir=mock_config_dir)
        
        # Mock crew and agent creation
        with patch.object(orchestrator, '_initialize_crews'), \
             patch.object(orchestrator, '_initialize_agents'), \
             patch.object(orchestrator, '_validate_configurations'):
            
            # Initialize orchestrator
            orchestrator.initialize()
            
            # Get system status
            status = orchestrator.get_system_status()
            
            # Verify memory status is included
            assert "memory_status" in status
            assert status["memory_status"]["initialized"] is True
            assert "vector_db" in status["memory_status"]
            assert status["memory_status"]["vector_db"]["collection_name"] == "ados_memory"

    @patch('chromadb.PersistentClient')
    @patch('chromadb.Settings')
    def test_orchestrator_memory_synchronization_on_shutdown(self, mock_settings, mock_client_class, mock_config_dir):
        """Test that orchestrator synchronizes memory on shutdown"""
        # Setup mocks
        mock_client = Mock()
        mock_collection = Mock()
        mock_client_class.return_value = mock_client
        mock_client.create_collection.return_value = mock_collection
        mock_client.get_collection.side_effect = Exception("Collection not found")
        
        # Create orchestrator
        orchestrator = ADOSOrchestrator(config_dir=mock_config_dir)
        
        # Mock crew and agent creation
        with patch.object(orchestrator, '_initialize_crews'), \
             patch.object(orchestrator, '_initialize_agents'), \
             patch.object(orchestrator, '_validate_configurations'):
            
            # Initialize orchestrator
            orchestrator.initialize()
            
            # Add some test data to memory
            orchestrator.memory_coordinator.crew_memory["test_crew"] = {
                "entries": [{"timestamp": "2024-01-01", "content": "test"}]
            }
            
            # Mock the synchronize method to verify it's called
            with patch.object(orchestrator.memory_coordinator, 'synchronize_memory') as mock_sync:
                # Shutdown orchestrator
                orchestrator.shutdown()
                
                # Verify synchronize was called
                mock_sync.assert_called_once()

    def test_memory_coordinator_standalone_functionality(self, temp_dir):
        """Test memory coordinator functionality without orchestrator"""
        # Create config loader
        config_loader = Mock()
        config_loader.load_system_settings.return_value = {
            "memory": {
                "vector_db": {
                    "provider": "chromadb",
                    "persist_directory": str(temp_dir / "memory" / "global_kb" / "chroma"),
                    "collection_name": "ados_memory"
                },
                "crew_memory": {
                    "type": "json",
                    "directory": str(temp_dir / "memory" / "crew_memory"),
                    "max_size_mb": 100
                },
                "session_memory": {
                    "enabled": True,
                    "max_entries": 1000
                }
            }
        }
        
        # Create memory coordinator
        memory_coordinator = MemoryCoordinator(config_loader=config_loader, workspace_dir=temp_dir)
        
        # Test initialization
        with patch('chromadb.PersistentClient') as mock_client_class:
            mock_client = Mock()
            mock_collection = Mock()
            mock_client_class.return_value = mock_client
            mock_client.create_collection.return_value = mock_collection
            mock_client.get_collection.side_effect = Exception("Collection not found")
            
            result = memory_coordinator.initialize_memory()
            assert result is True
            assert memory_coordinator.is_initialized is True
        
        # Test memory operations
        assert memory_coordinator.write_memory("test_crew", "session", "test content") is True
        assert memory_coordinator.read_memory("test_crew", "session") is not None
        
        # Test synchronization
        result = memory_coordinator.synchronize_memory()
        assert result is True

    def test_memory_coordinator_error_handling(self, temp_dir):
        """Test memory coordinator error handling"""
        # Create config loader with invalid config
        config_loader = Mock()
        config_loader.load_system_settings.return_value = {
            "memory": {
                "vector_db": {
                    "provider": "invalid_provider",
                    "persist_directory": "/invalid/path",
                    "collection_name": "test"
                }
            }
        }
        
        # Create memory coordinator
        memory_coordinator = MemoryCoordinator(config_loader=config_loader, workspace_dir=temp_dir)
        
        # Test initialization failure
        with patch('chromadb.PersistentClient', side_effect=Exception("Connection failed")):
            result = memory_coordinator.initialize_memory()
            assert result is False
            assert memory_coordinator.is_initialized is False
        
        # Test operations when not initialized
        assert memory_coordinator.write_memory("test_crew", "session", "test") is False
        assert memory_coordinator.read_memory("test_crew", "session") is None

    def test_memory_coordinator_configuration_loading(self, temp_dir):
        """Test memory coordinator configuration loading"""
        # Test without config loader
        memory_coordinator = MemoryCoordinator(workspace_dir=temp_dir)
        assert memory_coordinator.memory_config == {}
        
        # Test with config loader that fails
        config_loader = Mock()
        config_loader.load_system_settings.side_effect = Exception("Config error")
        
        memory_coordinator = MemoryCoordinator(config_loader=config_loader, workspace_dir=temp_dir)
        assert memory_coordinator.memory_config == {}