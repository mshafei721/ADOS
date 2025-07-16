"""
ADOS Task Decomposer
Task analysis and routing system (Task 2.2 - To be implemented)
"""

import logging
from typing import Dict, List, Optional, Any


class TaskDecomposer:
    """Task decomposer for analyzing and routing tasks to appropriate crews"""
    
    def __init__(self):
        """Initialize the task decomposer with crew mappings and dependencies"""
        self.logger = logging.getLogger(__name__)
        
        # Crew keyword mappings for task analysis
        self.crew_keywords = {
            "orchestrator": ["coordinate", "orchestrate", "manage", "plan", "decompose", "workflow"],
            "backend": ["api", "database", "server", "fastapi", "flask", "sql", "orm", "sqlalchemy", "endpoint", "rest", "graphql"],
            "security": ["auth", "authentication", "authorization", "jwt", "oauth", "security", "login", "password", "token", "encrypt"],
            "quality": ["test", "testing", "unit test", "coverage", "lint", "review", "quality", "validation", "pytest"],
            "integration": ["ci/cd", "pipeline", "integration", "deploy", "build", "continuous", "automation", "workflow"],
            "deployment": ["docker", "kubernetes", "k8s", "container", "cloud", "infrastructure", "devops", "release"],
            "frontend": ["ui", "frontend", "react", "vue", "component", "interface", "design", "user", "html", "css", "javascript"]
        }
        
        # Crew dependency graph (crew -> dependencies)
        self.crew_dependencies = {
            "orchestrator": [],
            "security": ["orchestrator"],
            "backend": ["security", "orchestrator"],
            "quality": ["backend", "security", "integration"],
            "integration": ["quality", "deployment"],
            "deployment": ["integration", "security"],
            "frontend": ["backend", "security"]
        }
        
        # Priority mappings for MoSCoW method
        self.priority_keywords = {
            "must": ["critical", "essential", "required", "mandatory", "core", "primary"],
            "should": ["important", "needed", "recommended", "significant"],
            "could": ["optional", "nice to have", "enhancement", "improvement"],
            "wont": ["future", "later", "not needed", "exclude", "skip"]
        }
        
        self.logger.info("TaskDecomposer initialized with crew mappings and dependencies")
    
    def decompose_task(self, task_description: str) -> Dict[str, Any]:
        """Decompose a task into subtasks and route to appropriate crews"""
        self.logger.info(f"Task decomposition requested: {task_description}")
        
        try:
            # Step 1: Analyze task complexity
            complexity_analysis = self.analyze_task_complexity(task_description)
            
            # Step 2: Identify relevant crews
            relevant_crews = self.identify_relevant_crews(task_description)
            
            # Step 3: Resolve crew dependencies
            execution_order = self.resolve_crew_dependencies(relevant_crews)
            
            # Step 4: Create subtasks
            subtasks = self.create_subtasks(task_description, execution_order)
            
            # Step 5: Assign priorities
            prioritized_subtasks = self.assign_priorities(subtasks, task_description)
            
            result = {
                "original_task": task_description,
                "complexity": complexity_analysis["complexity"],
                "estimated_time": complexity_analysis["estimated_time"],
                "subtasks": prioritized_subtasks,
                "execution_order": execution_order,
                "routing": self._create_routing_info(prioritized_subtasks),
                "status": "decomposed"
            }
            
            self.logger.info(f"Task decomposition completed: {len(prioritized_subtasks)} subtasks created")
            return result
            
        except Exception as e:
            self.logger.error(f"Task decomposition failed: {e}")
            return {
                "original_task": task_description,
                "error": str(e),
                "status": "failed"
            }
    
    def route_task(self, task: Dict[str, Any]) -> str:
        """Route a task to the appropriate crew"""
        task_description = task.get("description", "")
        
        # Identify the best crew for this specific task
        crew_scores = {}
        for crew, keywords in self.crew_keywords.items():
            score = sum(1 for keyword in keywords if keyword.lower() in task_description.lower())
            if score > 0:
                crew_scores[crew] = score
        
        if crew_scores:
            best_crew = max(crew_scores, key=crew_scores.get)
            self.logger.info(f"Task routed to crew: {best_crew}")
            return best_crew
        
        # Default to orchestrator if no specific crew identified
        self.logger.info("Task routed to default crew: orchestrator")
        return "orchestrator"
    
    def analyze_task_complexity(self, task_description: str) -> Dict[str, Any]:
        """Analyze task complexity and requirements"""
        task_lower = task_description.lower()
        
        # Count relevant crews
        relevant_crews = self.identify_relevant_crews(task_description)
        crew_count = len(relevant_crews)
        
        # Analyze complexity indicators
        complexity_indicators = {
            "simple": ["fix", "update", "change", "modify", "simple"],
            "medium": ["create", "implement", "build", "add", "develop"],
            "complex": ["system", "architecture", "full", "complete", "entire", "comprehensive"],
            "epic": ["project", "application", "platform", "multi", "end-to-end", "workflow"]
        }
        
        complexity_scores = {}
        for level, keywords in complexity_indicators.items():
            score = sum(1 for keyword in keywords if keyword in task_lower)
            complexity_scores[level] = score
        
        # Determine complexity based on indicators and crew count
        if crew_count >= 5 or complexity_scores.get("epic", 0) > 0:
            complexity = "epic"
            estimated_time = "1-2 weeks"
        elif crew_count >= 3 or complexity_scores.get("complex", 0) > 0:
            complexity = "complex"
            estimated_time = "3-5 days"
        elif crew_count >= 2 or complexity_scores.get("medium", 0) > 0:
            complexity = "medium"
            estimated_time = "1-2 days"
        else:
            complexity = "simple"
            estimated_time = "2-6 hours"
        
        return {
            "complexity": complexity,
            "estimated_time": estimated_time,
            "required_crews": relevant_crews,
            "crew_count": crew_count
        }
    
    def identify_relevant_crews(self, task_description: str) -> List[str]:
        """Identify which crews are relevant for the task"""
        task_lower = task_description.lower()
        relevant_crews = []
        
        for crew, keywords in self.crew_keywords.items():
            if any(keyword in task_lower for keyword in keywords):
                relevant_crews.append(crew)
        
        # Always include orchestrator for coordination
        if "orchestrator" not in relevant_crews:
            relevant_crews.append("orchestrator")
        
        return relevant_crews
    
    def resolve_crew_dependencies(self, crews: List[str]) -> List[str]:
        """Resolve crew dependencies using topological sorting"""
        # Create a graph of dependencies for the relevant crews
        graph = {}
        in_degree = {}
        
        for crew in crews:
            graph[crew] = []
            in_degree[crew] = 0
        
        # Build dependency graph
        for crew in crews:
            for dependency in self.crew_dependencies.get(crew, []):
                if dependency in crews:
                    graph[dependency].append(crew)
                    in_degree[crew] += 1
        
        # Topological sort using Kahn's algorithm
        queue = [crew for crew in crews if in_degree[crew] == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return result
    
    def create_subtasks(self, task_description: str, execution_order: List[str]) -> List[Dict[str, Any]]:
        """Create subtasks based on execution order"""
        subtasks = []
        
        for crew in execution_order:
            if crew == "orchestrator":
                subtask = {
                    "description": f"Coordinate and plan: {task_description}",
                    "crew": crew,
                    "type": "coordination"
                }
            elif crew == "backend":
                subtask = {
                    "description": f"Implement backend services for: {task_description}",
                    "crew": crew,
                    "type": "implementation"
                }
            elif crew == "security":
                subtask = {
                    "description": f"Implement security measures for: {task_description}",
                    "crew": crew,
                    "type": "security"
                }
            elif crew == "quality":
                subtask = {
                    "description": f"Test and validate: {task_description}",
                    "crew": crew,
                    "type": "testing"
                }
            elif crew == "integration":
                subtask = {
                    "description": f"Set up CI/CD for: {task_description}",
                    "crew": crew,
                    "type": "automation"
                }
            elif crew == "deployment":
                subtask = {
                    "description": f"Deploy and configure: {task_description}",
                    "crew": crew,
                    "type": "deployment"
                }
            elif crew == "frontend":
                subtask = {
                    "description": f"Build user interface for: {task_description}",
                    "crew": crew,
                    "type": "ui"
                }
            else:
                subtask = {
                    "description": f"Process {crew} tasks for: {task_description}",
                    "crew": crew,
                    "type": "general"
                }
            
            subtasks.append(subtask)
        
        return subtasks
    
    def assign_priorities(self, subtasks: List[Dict[str, Any]], task_description: str) -> List[Dict[str, Any]]:
        """Assign priorities to subtasks using MoSCoW method"""
        task_lower = task_description.lower()
        
        # Determine overall priority context
        priority_context = "should"  # default
        for priority, keywords in self.priority_keywords.items():
            if any(keyword in task_lower for keyword in keywords):
                priority_context = priority
                break
        
        # Assign priorities based on crew roles and context
        for subtask in subtasks:
            crew = subtask["crew"]
            
            # Core infrastructure crews get higher priority
            if crew in ["orchestrator", "security", "backend"]:
                subtask["priority"] = "must"
            elif crew in ["quality", "integration"]:
                subtask["priority"] = "should"
            elif crew in ["deployment", "frontend"]:
                subtask["priority"] = "could" if priority_context == "could" else "should"
            else:
                subtask["priority"] = priority_context
        
        return subtasks
    
    def _create_routing_info(self, subtasks: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Create routing information for orchestrator"""
        routing = {}
        for subtask in subtasks:
            crew = subtask["crew"]
            description = subtask["description"]
            
            if crew not in routing:
                routing[crew] = []
            routing[crew].append(description)
        
        return routing