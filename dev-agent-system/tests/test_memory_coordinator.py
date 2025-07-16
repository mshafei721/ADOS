"""
Test suite for MemoryCoordinator functionality
"""

import json
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from config.config_loader import ConfigLoader
from orchestrator.memory_coordinator import MemoryCoordinator


class TestMemoryCoordinator:
    """Test suite for MemoryCoordinator class"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def mock_config_loader(self):
        """Mock configuration loader"""
        config_loader = Mock(spec=ConfigLoader)
        config_loader.load_system_settings.return_value = {
            "memory": {
                "vector_db": {
                    "provider": "chromadb",
                    "persist_directory": "./memory/global_kb/chroma",
                    "collection_name": "ados_memory"
                },
                "crew_memory": {
                    "type": "json",
                    "directory": "./memory/crew_memory",
                    "max_size_mb": 100
                },
                "session_memory": {
                    "enabled": True,
                    "max_entries": 1000
                }
            }
        }
        return config_loader

    @pytest.fixture
    def memory_coordinator(self, mock_config_loader, temp_dir):
        """Create MemoryCoordinator instance for testing"""
        return MemoryCoordinator(
            config_loader=mock_config_loader,
            workspace_dir=temp_dir
        )

    def test_initialization(self, memory_coordinator):
        """Test MemoryCoordinator initialization"""
        assert memory_coordinator.workspace_dir.is_dir()
        assert memory_coordinator.config_loader is not None
        assert memory_coordinator.vector_db is None
        assert memory_coordinator.crew_memory == {}
        assert memory_coordinator.session_memory == {}
        assert not memory_coordinator.is_initialized

    def test_load_memory_config(self, memory_coordinator):
        """Test loading memory configuration"""
        assert "memory" in memory_coordinator.settings
        assert "vector_db" in memory_coordinator.memory_config
        assert "crew_memory" in memory_coordinator.memory_config
        assert "session_memory" in memory_coordinator.memory_config

    @patch('chromadb.PersistentClient')
    @patch('chromadb.Settings')
    def test_initialize_vector_db(self, mock_settings, mock_client_class, memory_coordinator):
        """Test vector database initialization"""
        # Setup mock
        mock_client = Mock()
        mock_collection = Mock()
        mock_collection.name = "ados_memory"
        mock_client_class.return_value = mock_client
        mock_client.create_collection.return_value = mock_collection
        mock_client.get_collection.side_effect = Exception("Collection not found")
        
        # Test initialization
        memory_coordinator._initialize_vector_db()
        
        # Verify calls
        mock_client_class.assert_called_once()
        mock_client.create_collection.assert_called_once()
        assert memory_coordinator.vector_db == mock_client
        assert memory_coordinator.collection == mock_collection

    def test_initialize_crew_memory(self, memory_coordinator, temp_dir):
        """Test crew memory initialization"""
        # Update memory config to use temp directory
        memory_coordinator.memory_config["crew_memory"] = {
            "directory": str(temp_dir / "memory" / "crew_memory")
        }
        
        # Create test crew memory file
        crew_dir = temp_dir / "memory" / "crew_memory"
        crew_dir.mkdir(parents=True, exist_ok=True)
        
        test_crew_file = crew_dir / "test_crew.json"
        test_data = {"entries": [{"timestamp": "2024-01-01", "content": "test"}]}
        with open(test_crew_file, 'w') as f:
            json.dump(test_data, f)
        
        # Test initialization
        memory_coordinator._initialize_crew_memory()
        
        # Verify crew memory loaded
        assert "test_crew" in memory_coordinator.crew_memory
        assert memory_coordinator.crew_memory["test_crew"] == test_data

    def test_initialize_session_memory(self, memory_coordinator):
        """Test session memory initialization"""
        memory_coordinator._initialize_session_memory()
        
        assert memory_coordinator.session_memory == {}
        assert memory_coordinator.session_max_entries == 1000

    @patch('chromadb.PersistentClient')
    @patch('chromadb.Settings')
    def test_initialize_memory_success(self, mock_settings, mock_client_class, memory_coordinator):
        """Test successful memory system initialization"""
        # Setup mock
        mock_client = Mock()
        mock_collection = Mock()
        mock_client_class.return_value = mock_client
        mock_client.create_collection.return_value = mock_collection
        mock_client.get_collection.side_effect = Exception("Collection not found")
        
        # Test initialization
        result = memory_coordinator.initialize_memory()
        
        assert result is True
        assert memory_coordinator.is_initialized is True

    def test_write_crew_memory(self, memory_coordinator):
        """Test writing crew memory"""
        memory_coordinator.is_initialized = True
        
        # Mock the save method
        with patch.object(memory_coordinator, '_save_crew_memory') as mock_save:
            result = memory_coordinator._write_crew_memory("test_crew", "test content")
            
            assert result is True
            assert "test_crew" in memory_coordinator.crew_memory
            assert "entries" in memory_coordinator.crew_memory["test_crew"]
            assert len(memory_coordinator.crew_memory["test_crew"]["entries"]) == 1
            assert memory_coordinator.crew_memory["test_crew"]["entries"][0]["content"] == "test content"
            mock_save.assert_called_once_with("test_crew")

    def test_write_session_memory(self, memory_coordinator):
        """Test writing session memory"""
        memory_coordinator.is_initialized = True
        memory_coordinator._initialize_session_memory()
        memory_coordinator.session_max_entries = 5
        
        # Add entries
        result = memory_coordinator._write_session_memory("test_crew", "content1")
        assert result is True
        assert len(memory_coordinator.session_memory["test_crew"]) == 1
        
        # Test max entries enforcement
        for i in range(2, 8):
            memory_coordinator._write_session_memory("test_crew", f"content{i}")
        
        # Should only keep last 5 entries
        assert len(memory_coordinator.session_memory["test_crew"]) == 5
        assert memory_coordinator.session_memory["test_crew"][0]["content"] == "content3"

    def test_read_crew_memory(self, memory_coordinator):
        """Test reading crew memory"""
        memory_coordinator.is_initialized = True
        
        # Setup test data
        memory_coordinator.crew_memory["test_crew"] = {
            "entries": [
                {"timestamp": "2024-01-01T10:00:00", "content": "first"},
                {"timestamp": "2024-01-01T11:00:00", "content": "second"}
            ]
        }
        
        result = memory_coordinator._read_crew_memory("test_crew")
        
        assert result is not None
        assert "first" in result
        assert "second" in result
        assert "2024-01-01T10:00:00" in result

    def test_read_session_memory(self, memory_coordinator):
        """Test reading session memory"""
        memory_coordinator.is_initialized = True
        
        # Setup test data
        memory_coordinator.session_memory["test_crew"] = [
            {"timestamp": "2024-01-01T10:00:00", "content": "session1"},
            {"timestamp": "2024-01-01T11:00:00", "content": "session2"}
        ]
        
        result = memory_coordinator._read_session_memory("test_crew")
        
        assert result is not None
        assert "session1" in result
        assert "session2" in result

    def test_write_vector_memory(self, memory_coordinator):
        """Test writing vector memory"""
        memory_coordinator.is_initialized = True
        
        # Setup mock collection
        mock_collection = Mock()
        memory_coordinator.collection = mock_collection
        
        result = memory_coordinator._write_vector_memory("test_crew", "test content")
        
        assert result is True
        mock_collection.add.assert_called_once()
        
        # Verify call arguments
        call_args = mock_collection.add.call_args
        assert len(call_args[1]["ids"]) == 1
        assert call_args[1]["documents"] == ["test content"]
        assert call_args[1]["metadatas"][0]["crew_name"] == "test_crew"

    def test_memory_status(self, memory_coordinator):
        """Test getting memory status"""
        memory_coordinator.is_initialized = True
        memory_coordinator._initialize_session_memory()
        
        # Mock collection to prevent attribute error
        mock_collection = Mock()
        mock_collection.name = "test_collection"
        mock_collection.count.return_value = 5
        memory_coordinator.collection = mock_collection
        
        # Add some test data
        memory_coordinator.crew_memory["test_crew"] = {
            "entries": [{"timestamp": "2024-01-01", "content": "test"}]
        }
        memory_coordinator.session_memory["test_crew"] = [
            {"timestamp": "2024-01-01", "content": "session"}
        ]
        
        status = memory_coordinator.get_memory_status()
        
        assert status["initialized"] is True
        assert "test_crew" in status["crew_memory"]
        assert "test_crew" in status["session_memory"]
        assert status["crew_memory"]["test_crew"]["entries_count"] == 1
        assert status["session_memory"]["test_crew"]["entries_count"] == 1

    def test_synchronize_memory(self, memory_coordinator):
        """Test memory synchronization"""
        memory_coordinator.is_initialized = True
        
        # Setup test data
        memory_coordinator.crew_memory["test_crew"] = {
            "entries": [{"timestamp": "2024-01-01", "content": "test"}]
        }
        
        # Mock vector db
        mock_vector_db = Mock()
        memory_coordinator.vector_db = mock_vector_db
        
        # Mock save method
        with patch.object(memory_coordinator, '_save_crew_memory') as mock_save:
            result = memory_coordinator.synchronize_memory()
            
            assert result is True
            mock_save.assert_called_once_with("test_crew")
            mock_vector_db.persist.assert_called_once()

    def test_write_memory_integration(self, memory_coordinator):
        """Test write_memory method integration"""
        memory_coordinator.is_initialized = True
        
        # Mock individual write methods
        with patch.object(memory_coordinator, '_write_crew_memory', return_value=True) as mock_crew, \
             patch.object(memory_coordinator, '_write_session_memory', return_value=True) as mock_session, \
             patch.object(memory_coordinator, '_write_vector_memory', return_value=True) as mock_vector:
            
            # Test crew memory
            result = memory_coordinator.write_memory("test_crew", "crew", "content")
            assert result is True
            mock_crew.assert_called_once_with("test_crew", "content")
            
            # Test session memory
            result = memory_coordinator.write_memory("test_crew", "session", "content")
            assert result is True
            mock_session.assert_called_once_with("test_crew", "content")
            
            # Test vector memory
            result = memory_coordinator.write_memory("test_crew", "vector", "content")
            assert result is True
            mock_vector.assert_called_once_with("test_crew", "content")

    def test_read_memory_integration(self, memory_coordinator):
        """Test read_memory method integration"""
        memory_coordinator.is_initialized = True
        
        # Mock individual read methods
        with patch.object(memory_coordinator, '_read_crew_memory', return_value="crew_result") as mock_crew, \
             patch.object(memory_coordinator, '_read_session_memory', return_value="session_result") as mock_session, \
             patch.object(memory_coordinator, '_read_vector_memory', return_value="vector_result") as mock_vector:
            
            # Test crew memory
            result = memory_coordinator.read_memory("test_crew", "crew")
            assert result == "crew_result"
            mock_crew.assert_called_once_with("test_crew")
            
            # Test session memory
            result = memory_coordinator.read_memory("test_crew", "session")
            assert result == "session_result"
            mock_session.assert_called_once_with("test_crew")
            
            # Test vector memory
            result = memory_coordinator.read_memory("test_crew", "vector", "query")
            assert result == "vector_result"
            mock_vector.assert_called_once_with("test_crew", "query")

    def test_memory_not_initialized_error(self, memory_coordinator):
        """Test error handling when memory not initialized"""
        memory_coordinator.is_initialized = False
        
        result = memory_coordinator.write_memory("test_crew", "crew", "content")
        assert result is False
        
        result = memory_coordinator.read_memory("test_crew", "crew")
        assert result is None

    def test_invalid_memory_type(self, memory_coordinator):
        """Test handling of invalid memory type"""
        memory_coordinator.is_initialized = True
        
        result = memory_coordinator.write_memory("test_crew", "invalid", "content")
        assert result is False
        
        result = memory_coordinator.read_memory("test_crew", "invalid")
        assert result is None