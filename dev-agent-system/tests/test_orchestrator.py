"""
Tests for ADOS Orchestrator
"""

import pytest
from pathlib import Path
import sys
import os

# Add the parent directory to the path so we can import from dev-agent-system
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrator.main import ADOSOrchestrator
from orchestrator.agent_factory import AgentFactory
from orchestrator.crew_factory import CrewFactory
from config.config_loader import ConfigLoader


class TestADOSOrchestrator:
    """Test cases for ADOS Orchestrator"""
    
    def test_orchestrator_initialization(self):
        """Test that the orchestrator can be initialized"""
        orchestrator = ADOSOrchestrator()
        assert orchestrator is not None
        assert not orchestrator.is_initialized
        assert orchestrator.config_loader is not None
        assert orchestrator.agent_factory is not None
        assert orchestrator.crew_factory is not None
    
    def test_orchestrator_full_initialization(self):
        """Test full orchestrator initialization"""
        orchestrator = ADOSOrchestrator()
        
        # Test initialization
        success = orchestrator.initialize()
        assert success
        assert orchestrator.is_initialized
        
        # Test system status
        status = orchestrator.get_system_status()
        assert status["initialized"] == True
        assert status["crews"]["total"] > 0
        assert status["agents"]["total"] > 0
        
        # Test crew and agent access
        crews = orchestrator.list_crews()
        agents = orchestrator.list_agents()
        assert len(crews) > 0
        assert len(agents) > 0
        
        # Test getting specific crew
        if "orchestrator" in crews:
            crew = orchestrator.get_crew("orchestrator")
            assert crew is not None
        
        # Test getting specific agent
        if agents:
            agent = orchestrator.get_agent(agents[0])
            assert agent is not None
        
        # Test system validation
        validation = orchestrator.validate_system()
        assert validation["orchestrator_initialized"] == True
        
        # Cleanup
        orchestrator.shutdown()
        assert not orchestrator.is_initialized
    
    def test_orchestrator_task_execution(self):
        """Test basic task execution"""
        orchestrator = ADOSOrchestrator()
        
        # Initialize orchestrator
        success = orchestrator.initialize()
        assert success
        
        # Test simple task execution
        result = orchestrator.execute_simple_task("Test task", "orchestrator")
        # Note: This might return None due to mock tools, but shouldn't crash
        
        # Cleanup
        orchestrator.shutdown()
    
    def test_agent_factory(self):
        """Test agent factory functionality"""
        config_loader = ConfigLoader()
        agent_factory = AgentFactory(config_loader)
        
        # Test agent creation
        agents_config = config_loader.load_agents_config()
        if agents_config:
            agent_name = list(agents_config.keys())[0]
            agent_config = agents_config[agent_name]
            
            agent = agent_factory.create_agent(agent_name, agent_config)
            assert agent is not None
            assert agent.role == agent_config.role
            assert agent.goal == agent_config.goal
            assert agent.backstory == agent_config.backstory
            
            # Test agent caching
            cached_agent = agent_factory.get_agent(agent_name)
            assert cached_agent is agent
            
            # Test agent info
            info = agent_factory.get_agent_info(agent_name)
            assert info is not None
            assert info["name"] == agent_name
            assert info["role"] == agent_config.role
    
    def test_crew_factory(self):
        """Test crew factory functionality"""
        config_loader = ConfigLoader()
        agent_factory = AgentFactory(config_loader)
        crew_factory = CrewFactory(config_loader, agent_factory)
        
        # Test crew creation
        crews_config = config_loader.load_crews_config()
        if crews_config:
            crew_name = list(crews_config.keys())[0]
            crew_config = crews_config[crew_name]
            
            crew = crew_factory.create_crew(crew_name, crew_config)
            assert crew is not None
            assert len(crew.agents) > 0
            assert len(crew.tasks) > 0
            
            # Test crew caching
            cached_crew = crew_factory.get_crew(crew_name)
            assert cached_crew is crew
            
            # Test crew info
            info = crew_factory.get_crew_info(crew_name)
            assert info is not None
            assert info["name"] == crew_name
            assert info["goal"] == crew_config.goal


def test_configuration_loading():
    """Test that configuration files can be loaded"""
    config_loader = ConfigLoader()
    
    # Test crew configuration loading
    crews = config_loader.load_crews_config()
    assert len(crews) > 0
    
    # Test agent configuration loading
    agents = config_loader.load_agents_config()
    assert len(agents) > 0
    
    # Test configuration validation
    validation = config_loader.validate_config_integrity()
    assert validation["valid"] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])