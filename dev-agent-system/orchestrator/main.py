"""
ADOS Main Orchestrator
Core orchestration system using CrewAI framework
"""

import os
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

from crewai import Agent, Crew, Task, Process
from crewai.project import CrewBase

from config.config_loader import ConfigLoader, AgentConfig, CrewConfig
from orchestrator.agent_factory import AgentFactory
from orchestrator.crew_factory import CrewFactory
from orchestrator.task_decomposer import TaskDecomposer
from orchestrator.memory_coordinator import MemoryCoordinator
from orchestrator.logging_service import LoggingService, initialize_logging
from crews.orchestrator.orchestrator_crew import OrchestratorCrew


class ADOSOrchestrator:
    """Main orchestrator for ADOS system using CrewAI framework"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize the ADOS orchestrator"""
        self.config_loader = ConfigLoader(config_dir)
        self.agent_factory = AgentFactory(self.config_loader)
        self.crew_factory = CrewFactory(self.config_loader, self.agent_factory)
        self.task_decomposer = TaskDecomposer()
        self.memory_coordinator = MemoryCoordinator(self.config_loader)
        self.orchestrator_crew = OrchestratorCrew(self.config_loader, self.agent_factory)
        
        # Configuration data
        self.crews_config: Dict[str, CrewConfig] = {}
        self.agents_config: Dict[str, AgentConfig] = {}
        self.initialized_crews: Dict[str, Crew] = {}
        self.initialized_agents: Dict[str, Agent] = {}
        
        # System state
        self.is_initialized = False
        
        # Initialize logging service
        self.logging_service = LoggingService(self.config_loader)
        self._setup_logging()
        
        # Get logger after logging service is initialized
        self.logger = self.logging_service.get_logger("ados_orchestrator")
    
    def _setup_logging(self):
        """Setup advanced logging configuration using LoggingService"""
        if not self.logging_service.initialize():
            # Fallback to basic logging if service fails
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.StreamHandler(),
                    logging.FileHandler('ados_orchestrator.log')
                ]
            )
            print("Warning: Logging service initialization failed, using basic logging")
    
    def initialize(self) -> bool:
        """Initialize the orchestrator by loading configurations and creating crews"""
        try:
            self.logger.info("Initializing ADOS Orchestrator...")
            
            # Load configurations
            self._load_configurations()
            
            # Validate configurations
            self._validate_configurations()
            
            # Initialize agents (lazy loading)
            self._initialize_agents()
            
            # Initialize crews
            self._initialize_crews()
            
            # Initialize memory coordinator
            self._initialize_memory()
            
            self.is_initialized = True
            self.logger.info("ADOS Orchestrator initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize orchestrator: {e}")
            self.is_initialized = False
            return False
    
    def _load_configurations(self):
        """Load all configuration files"""
        self.logger.info("Loading configurations...")
        
        # Load crews and agents configuration
        self.crews_config = self.config_loader.load_crews_config()
        self.agents_config = self.config_loader.load_agents_config()
        
        self.logger.info(f"Loaded {len(self.crews_config)} crews and {len(self.agents_config)} agents")
    
    def _validate_configurations(self):
        """Validate configuration integrity"""
        self.logger.info("Validating configurations...")
        
        # Validate overall configuration
        validation_results = self.config_loader.validate_config_integrity()
        
        if not validation_results["valid"]:
            raise ValueError(f"Configuration validation failed: {validation_results['errors']}")
        
        if validation_results["warnings"]:
            for warning in validation_results["warnings"]:
                self.logger.warning(warning)
        
        # Validate that all crews have at least one agent
        for crew_name in self.crews_config:
            crew_agents = [agent for agent in self.agents_config.values() if agent.crew == crew_name]
            if not crew_agents:
                raise ValueError(f"Crew '{crew_name}' has no agents defined")
        
        self.logger.info("Configuration validation passed")
    
    def _initialize_agents(self):
        """Initialize all agents using the agent factory"""
        self.logger.info("Initializing agents...")
        
        for agent_name, agent_config in self.agents_config.items():
            try:
                agent = self.agent_factory.create_agent(agent_name, agent_config)
                self.initialized_agents[agent_name] = agent
                self.logger.debug(f"Initialized agent: {agent_name}")
            except Exception as e:
                self.logger.error(f"Failed to initialize agent '{agent_name}': {e}")
                raise
        
        self.logger.info(f"Successfully initialized {len(self.initialized_agents)} agents")
    
    def _initialize_crews(self):
        """Initialize all crews using the crew factory"""
        self.logger.info("Initializing crews...")
        
        for crew_name, crew_config in self.crews_config.items():
            try:
                crew = self.crew_factory.create_crew(crew_name, crew_config)
                self.initialized_crews[crew_name] = crew
                self.logger.debug(f"Initialized crew: {crew_name}")
            except Exception as e:
                self.logger.error(f"Failed to initialize crew '{crew_name}': {e}")
                raise
        
        self.logger.info(f"Successfully initialized {len(self.initialized_crews)} crews")
    
    def _initialize_memory(self):
        """Initialize memory coordinator"""
        self.logger.info("Initializing memory coordinator...")
        
        try:
            if not self.memory_coordinator.initialize_memory():
                raise RuntimeError("Memory coordinator initialization failed")
            
            self.logger.info("Memory coordinator initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize memory coordinator: {e}")
            raise
    
    def get_crew(self, crew_name: str) -> Optional[Crew]:
        """Get a specific crew by name"""
        if not self.is_initialized:
            raise RuntimeError("Orchestrator not initialized. Call initialize() first.")
        
        return self.initialized_crews.get(crew_name)
    
    def get_agent(self, agent_name: str) -> Optional[Agent]:
        """Get a specific agent by name"""
        if not self.is_initialized:
            raise RuntimeError("Orchestrator not initialized. Call initialize() first.")
        
        return self.initialized_agents.get(agent_name)
    
    def get_crew_agents(self, crew_name: str) -> List[Agent]:
        """Get all agents for a specific crew"""
        if not self.is_initialized:
            raise RuntimeError("Orchestrator not initialized. Call initialize() first.")
        
        crew_agents = []
        for agent_name, agent_config in self.agents_config.items():
            if agent_config.crew == crew_name:
                agent = self.initialized_agents.get(agent_name)
                if agent:
                    crew_agents.append(agent)
        
        return crew_agents
    
    def list_crews(self) -> List[str]:
        """List all available crew names"""
        return list(self.crews_config.keys())
    
    def list_agents(self) -> List[str]:
        """List all available agent names"""
        return list(self.agents_config.keys())
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "initialized": self.is_initialized,
            "crews": {
                "total": len(self.crews_config),
                "initialized": len(self.initialized_crews),
                "names": list(self.crews_config.keys())
            },
            "agents": {
                "total": len(self.agents_config),
                "initialized": len(self.initialized_agents),
                "names": list(self.agents_config.keys())
            },
            "crew_distribution": {
                crew_name: len([a for a in self.agents_config.values() if a.crew == crew_name])
                for crew_name in self.crews_config.keys()
            },
            "configuration_status": self.config_loader.validate_config_integrity(),
            "memory_status": self.memory_coordinator.get_memory_status() if hasattr(self, 'memory_coordinator') else None,
            "logging_status": self.logging_service.get_logging_status() if hasattr(self, 'logging_service') else None
        }
    
    def execute_simple_task(self, task_description: str, crew_name: str = "orchestrator") -> Optional[str]:
        """Execute a simple task using the specified crew"""
        if not self.is_initialized:
            raise RuntimeError("Orchestrator not initialized. Call initialize() first.")
        
        crew = self.get_crew(crew_name)
        if not crew:
            raise ValueError(f"Crew '{crew_name}' not found")
        
        try:
            self.logger.info(f"Executing task with crew '{crew_name}': {task_description}")
            
            # Create a simple task
            task = Task(
                description=task_description,
                expected_output="Task completion confirmation",
                agent=crew.agents[0] if crew.agents else None
            )
            
            # Create a temporary crew for this task if needed
            if not crew.agents:
                crew_agents = self.get_crew_agents(crew_name)
                if not crew_agents:
                    raise ValueError(f"No agents available for crew '{crew_name}'")
                
                temp_crew = Crew(
                    agents=crew_agents,
                    tasks=[task],
                    process=Process.sequential,
                    verbose=True
                )
                result = temp_crew.kickoff()
            else:
                # Use existing crew structure
                result = crew.kickoff()
            
            self.logger.info(f"Task completed successfully")
            return str(result)
            
        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
            return None
    
    def execute_task(self, task_description: str, crew_name: str = "orchestrator") -> Optional[str]:
        """Execute a task using the specified crew (alias for execute_simple_task)"""
        return self.execute_simple_task(task_description, crew_name)
    
    def shutdown(self):
        """Shutdown the orchestrator and clean up resources"""
        self.logger.info("Shutting down ADOS Orchestrator...")
        
        # Synchronize memory before shutdown
        if hasattr(self, 'memory_coordinator') and self.memory_coordinator.is_initialized:
            try:
                self.memory_coordinator.synchronize_memory()
                self.logger.info("Memory synchronized before shutdown")
            except Exception as e:
                self.logger.warning(f"Failed to synchronize memory during shutdown: {e}")
        
        # Clear initialized crews and agents
        self.initialized_crews.clear()
        self.initialized_agents.clear()
        
        # Reset state
        self.is_initialized = False
        
        self.logger.info("ADOS Orchestrator shutdown complete")
        
        # Shutdown logging service
        if hasattr(self, 'logging_service'):
            self.logging_service.shutdown()
    
    def decompose_and_execute_task(self, task_description: str) -> Dict[str, Any]:
        """Decompose a task and execute it using appropriate crews"""
        if not self.is_initialized:
            raise RuntimeError("Orchestrator not initialized. Call initialize() first.")
        
        self.logger.info(f"Decomposing and executing task: {task_description}")
        
        try:
            # Step 1: Decompose the task
            decomposition = self.task_decomposer.decompose_task(task_description)
            
            if decomposition["status"] == "failed":
                self.logger.error(f"Task decomposition failed: {decomposition.get('error', 'Unknown error')}")
                return decomposition
            
            # Step 2: Execute subtasks in order
            execution_results = []
            for subtask in decomposition["subtasks"]:
                crew_name = subtask["crew"]
                description = subtask["description"]
                priority = subtask["priority"]
                
                self.logger.info(f"Executing subtask [{priority}] with crew '{crew_name}': {description}")
                
                try:
                    # Execute the subtask
                    result = self.execute_task(description, crew_name)
                    execution_results.append({
                        "crew": crew_name,
                        "description": description,
                        "priority": priority,
                        "result": result,
                        "status": "success"
                    })
                except Exception as e:
                    self.logger.error(f"Subtask execution failed for crew '{crew_name}': {e}")
                    execution_results.append({
                        "crew": crew_name,
                        "description": description,
                        "priority": priority,
                        "error": str(e),
                        "status": "failed"
                    })
            
            # Step 3: Compile final results
            final_result = {
                "original_task": task_description,
                "decomposition": decomposition,
                "execution_results": execution_results,
                "status": "completed",
                "subtasks_completed": len([r for r in execution_results if r["status"] == "success"]),
                "subtasks_failed": len([r for r in execution_results if r["status"] == "failed"]),
                "total_subtasks": len(execution_results)
            }
            
            self.logger.info(f"Task decomposition and execution completed: {final_result['subtasks_completed']}/{final_result['total_subtasks']} subtasks successful")
            return final_result
            
        except Exception as e:
            self.logger.error(f"Task decomposition and execution failed: {e}")
            return {
                "original_task": task_description,
                "error": str(e),
                "status": "failed"
            }
    
    def reload_configuration(self) -> bool:
        """Reload configuration and reinitialize the system"""
        self.logger.info("Reloading configuration...")
        
        # Shutdown current state
        self.shutdown()
        
        # Reinitialize
        return self.initialize()
    
    def validate_system(self) -> Dict[str, Any]:
        """Perform comprehensive system validation"""
        validation_results = {
            "orchestrator_initialized": self.is_initialized,
            "configuration_valid": True,
            "crew_status": {},
            "agent_status": {},
            "errors": [],
            "warnings": []
        }
        
        try:
            # Validate configuration
            config_validation = self.config_loader.validate_config_integrity()
            validation_results["configuration_valid"] = config_validation["valid"]
            validation_results["errors"].extend(config_validation["errors"])
            validation_results["warnings"].extend(config_validation["warnings"])
            
            # Validate crews
            for crew_name, crew in self.initialized_crews.items():
                validation_results["crew_status"][crew_name] = {
                    "initialized": crew is not None,
                    "agents_count": len(crew.agents) if crew and hasattr(crew, 'agents') else 0
                }
            
            # Validate agents
            for agent_name, agent in self.initialized_agents.items():
                validation_results["agent_status"][agent_name] = {
                    "initialized": agent is not None,
                    "crew": self.agents_config[agent_name].crew if agent_name in self.agents_config else "unknown"
                }
            
        except Exception as e:
            validation_results["errors"].append(f"System validation failed: {e}")
        
        return validation_results
    
    def intelligent_task_dispatch(self, task_description: str, priority: str = "medium") -> Dict[str, Any]:
        """Use orchestrator crew for intelligent task dispatch"""
        if not self.is_initialized:
            raise RuntimeError("Orchestrator not initialized. Call initialize() first.")
        
        return self.orchestrator_crew.intelligent_task_dispatch(task_description, priority)
    
    def get_crew_health(self, crew_name: str) -> Dict[str, Any]:
        """Get health status of a specific crew"""
        if not self.is_initialized:
            raise RuntimeError("Orchestrator not initialized. Call initialize() first.")
        
        return self.orchestrator_crew.monitor_crew_health(crew_name)
    
    def get_all_crews_health(self) -> Dict[str, Dict[str, Any]]:
        """Get health status of all crews"""
        if not self.is_initialized:
            raise RuntimeError("Orchestrator not initialized. Call initialize() first.")
        
        return self.orchestrator_crew.monitor_all_crews()
    
    def get_orchestrator_overview(self) -> Dict[str, Any]:
        """Get comprehensive orchestrator overview"""
        if not self.is_initialized:
            raise RuntimeError("Orchestrator not initialized. Call initialize() first.")
        
        system_status = self.get_system_status()
        orchestrator_overview = self.orchestrator_crew.get_system_overview()
        
        return {
            "system_status": system_status,
            "orchestrator_crew": orchestrator_overview,
            "integration_status": "active"
        }
    
    def process_task_queue(self) -> List[Dict[str, Any]]:
        """Process queued tasks using orchestrator crew"""
        if not self.is_initialized:
            raise RuntimeError("Orchestrator not initialized. Call initialize() first.")
        
        return self.orchestrator_crew.process_task_queue()
    
    def complete_task(self, crew_name: str, success: bool = True):
        """Mark a task as completed and update crew metrics"""
        if not self.is_initialized:
            raise RuntimeError("Orchestrator not initialized. Call initialize() first.")
        
        self.orchestrator_crew.complete_task(crew_name, success)
    
    def get_task_queue_status(self) -> Dict[str, Any]:
        """Get task queue status"""
        if not self.is_initialized:
            raise RuntimeError("Orchestrator not initialized. Call initialize() first.")
        
        return self.orchestrator_crew.get_task_queue_status()
    
    def perform_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        if not self.is_initialized:
            return {
                "status": "not_initialized",
                "timestamp": "N/A",
                "error": "Orchestrator not initialized"
            }
        
        # Get orchestrator crew health check
        orchestrator_health = self.orchestrator_crew.health_check()
        
        # Get system validation
        system_validation = self.validate_system()
        
        # Combine results
        overall_status = "healthy"
        if orchestrator_health["status"] == "critical" or not system_validation["configuration_valid"]:
            overall_status = "critical"
        elif orchestrator_health["status"] == "warning" or system_validation["errors"]:
            overall_status = "warning"
        
        return {
            "overall_status": overall_status,
            "orchestrator_crew_health": orchestrator_health,
            "system_validation": system_validation,
            "timestamp": orchestrator_health["timestamp"]
        }