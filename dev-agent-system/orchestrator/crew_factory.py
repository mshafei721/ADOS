"""
ADOS Crew Factory
Factory for creating CrewAI crews from configuration
"""

import logging
from typing import Dict, List, Optional, Any

from crewai import Crew, Process, Task
from crewai import Agent

from config.config_loader import ConfigLoader, CrewConfig
from orchestrator.agent_factory import AgentFactory


class CrewFactory:
    """Factory for creating CrewAI crews from ADOS configuration"""
    
    def __init__(self, config_loader: ConfigLoader, agent_factory: AgentFactory):
        """Initialize the crew factory"""
        self.config_loader = config_loader
        self.agent_factory = agent_factory
        self.logger = logging.getLogger(__name__)
        
        # Cache for created crews
        self._crew_cache: Dict[str, Crew] = {}
    
    def create_crew(self, crew_name: str, crew_config: CrewConfig) -> Crew:
        """Create a CrewAI crew from configuration"""
        # Check cache first
        if crew_name in self._crew_cache:
            return self._crew_cache[crew_name]
        
        try:
            self.logger.debug(f"Creating crew: {crew_name}")
            
            # Get agents for this crew
            agents = self.agent_factory.create_agents_for_crew(crew_name)
            
            if not agents:
                raise ValueError(f"No agents found for crew '{crew_name}'")
            
            # Create default tasks for the crew
            tasks = self._create_default_tasks(crew_name, crew_config, agents)
            
            # Create the crew
            crew = Crew(
                agents=agents,
                tasks=tasks,
                process=Process.sequential,  # Default to sequential processing
                verbose=True,
                memory=True,  # Enable memory for better performance
                planning=True  # Enable planning for better coordination
            )
            
            # Cache the crew
            self._crew_cache[crew_name] = crew
            
            self.logger.debug(f"Successfully created crew: {crew_name}")
            return crew
            
        except Exception as e:
            self.logger.error(f"Failed to create crew '{crew_name}': {e}")
            raise
    
    def _create_default_tasks(self, crew_name: str, crew_config: CrewConfig, agents: List[Agent]) -> List[Task]:
        """Create default tasks for a crew"""
        tasks = []
        
        if not agents:
            return tasks
        
        # Create a basic task for the crew based on its goal
        task = Task(
            description=f"Execute {crew_name} crew responsibilities: {crew_config.goal}",
            expected_output="Task completion confirmation with status report",
            agent=agents[0]  # Assign to first agent
        )
        
        tasks.append(task)
        
        # If there are multiple agents, create coordination tasks
        if len(agents) > 1:
            for i, agent in enumerate(agents[1:], 1):
                coordination_task = Task(
                    description=f"Coordinate with {crew_name} crew for specialized {agent.role} tasks",
                    expected_output="Coordination confirmation and task results",
                    agent=agent
                )
                tasks.append(coordination_task)
        
        return tasks
    
    def create_crew_with_custom_tasks(self, crew_name: str, crew_config: CrewConfig, tasks: List[Task]) -> Crew:
        """Create a crew with custom tasks"""
        try:
            self.logger.debug(f"Creating crew with custom tasks: {crew_name}")
            
            # Get agents for this crew
            agents = self.agent_factory.create_agents_for_crew(crew_name)
            
            if not agents:
                raise ValueError(f"No agents found for crew '{crew_name}'")
            
            # Create the crew with custom tasks
            crew = Crew(
                agents=agents,
                tasks=tasks,
                process=Process.sequential,
                verbose=True,
                memory=True,
                planning=True
            )
            
            # Cache the crew
            self._crew_cache[crew_name] = crew
            
            self.logger.debug(f"Successfully created crew with custom tasks: {crew_name}")
            return crew
            
        except Exception as e:
            self.logger.error(f"Failed to create crew with custom tasks '{crew_name}': {e}")
            raise
    
    def get_crew(self, crew_name: str) -> Optional[Crew]:
        """Get a cached crew by name"""
        return self._crew_cache.get(crew_name)
    
    def list_crews(self) -> List[str]:
        """List all cached crew names"""
        return list(self._crew_cache.keys())
    
    def clear_cache(self):
        """Clear the crew cache"""
        self._crew_cache.clear()
        self.logger.debug("Crew cache cleared")
    
    def validate_crew_configuration(self, crew_name: str, crew_config: CrewConfig) -> Dict[str, Any]:
        """Validate crew configuration"""
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        try:
            # Validate required fields
            if not crew_config.goal:
                validation_results["errors"].append("Goal is required")
                validation_results["valid"] = False
            
            if not crew_config.tools:
                validation_results["warnings"].append("No tools specified for crew")
            
            # Validate dependencies
            all_crews = self.config_loader.load_crews_config()
            for dependency in crew_config.dependencies:
                if dependency not in all_crews:
                    validation_results["errors"].append(f"Invalid dependency: {dependency}")
                    validation_results["valid"] = False
            
            # Validate that the crew has agents
            crew_agents = self.config_loader.get_crew_agents(crew_name)
            if not crew_agents:
                validation_results["warnings"].append(f"No agents assigned to crew '{crew_name}'")
            
            # Validate tools availability
            for tool in crew_config.tools:
                # In a real implementation, this would check if tools are available
                self.logger.debug(f"Tool validation: {tool}")
            
        except Exception as e:
            validation_results["valid"] = False
            validation_results["errors"].append(f"Validation failed: {e}")
        
        return validation_results
    
    def get_crew_info(self, crew_name: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive information about a crew"""
        crews_config = self.config_loader.load_crews_config()
        
        if crew_name not in crews_config:
            return None
        
        crew_config = crews_config[crew_name]
        cached_crew = self._crew_cache.get(crew_name)
        crew_agents = self.config_loader.get_crew_agents(crew_name)
        
        return {
            "name": crew_name,
            "goal": crew_config.goal,
            "constraints": crew_config.constraints,
            "dependencies": crew_config.dependencies,
            "tools": crew_config.tools,
            "agents": [agent.role for agent in crew_agents],
            "agent_count": len(crew_agents),
            "cached": cached_crew is not None,
            "validation": self.validate_crew_configuration(crew_name, crew_config)
        }
    
    def get_all_crews_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all crews"""
        crews_info = {}
        
        for crew_name in self.config_loader.load_crews_config().keys():
            crews_info[crew_name] = self.get_crew_info(crew_name)
        
        return crews_info
    
    def execute_crew_task(self, crew_name: str, task_description: str) -> Optional[str]:
        """Execute a task with a specific crew"""
        try:
            crew = self.get_crew(crew_name)
            if not crew:
                # Create crew if not cached
                crew_config = self.config_loader.get_crew_config(crew_name)
                if not crew_config:
                    raise ValueError(f"Crew '{crew_name}' not found in configuration")
                
                crew = self.create_crew(crew_name, crew_config)
            
            # Create a task for the crew
            task = Task(
                description=task_description,
                expected_output="Task completion confirmation",
                agent=crew.agents[0] if crew.agents else None
            )
            
            # Create a temporary crew for this specific task
            temp_crew = Crew(
                agents=crew.agents,
                tasks=[task],
                process=Process.sequential,
                verbose=True
            )
            
            # Execute the task
            result = temp_crew.kickoff()
            
            self.logger.info(f"Task executed successfully by crew '{crew_name}'")
            return str(result)
            
        except Exception as e:
            self.logger.error(f"Failed to execute task for crew '{crew_name}': {e}")
            return None
    
    def get_crew_dependencies(self, crew_name: str) -> List[str]:
        """Get dependencies for a crew"""
        crew_config = self.config_loader.get_crew_config(crew_name)
        if crew_config:
            return crew_config.dependencies
        return []
    
    def get_crew_dependency_graph(self) -> Dict[str, List[str]]:
        """Get dependency graph for all crews"""
        dependency_graph = {}
        
        for crew_name in self.config_loader.load_crews_config().keys():
            dependency_graph[crew_name] = self.get_crew_dependencies(crew_name)
        
        return dependency_graph
    
    def validate_dependency_graph(self) -> Dict[str, Any]:
        """Validate crew dependency graph for cycles"""
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "cycles": []
        }
        
        try:
            dependency_graph = self.get_crew_dependency_graph()
            
            # Check for cycles using DFS
            visited = set()
            rec_stack = set()
            
            def has_cycle(node):
                visited.add(node)
                rec_stack.add(node)
                
                for neighbor in dependency_graph.get(node, []):
                    if neighbor not in visited:
                        if has_cycle(neighbor):
                            return True
                    elif neighbor in rec_stack:
                        return True
                
                rec_stack.remove(node)
                return False
            
            # Check each crew for cycles
            for crew_name in dependency_graph:
                if crew_name not in visited:
                    if has_cycle(crew_name):
                        validation_results["cycles"].append(crew_name)
                        validation_results["valid"] = False
            
            if validation_results["cycles"]:
                validation_results["errors"].append(f"Dependency cycles detected: {validation_results['cycles']}")
        
        except Exception as e:
            validation_results["valid"] = False
            validation_results["errors"].append(f"Dependency validation failed: {e}")
        
        return validation_results