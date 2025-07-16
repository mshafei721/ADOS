"""
Task Decomposer Tool
Enhanced task decomposition for ADOS orchestrator
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class SubTask:
    """Subtask data structure"""
    id: str
    title: str
    description: str
    crew: str
    priority: str
    estimated_effort: str
    dependencies: List[str]
    acceptance_criteria: List[str]
    complexity: str
    tags: List[str]


@dataclass
class TaskDecomposition:
    """Task decomposition result"""
    original_task: str
    subtasks: List[SubTask]
    execution_order: List[str]
    estimated_duration: str
    complexity_analysis: Dict[str, Any]
    crew_distribution: Dict[str, int]
    dependency_graph: Dict[str, List[str]]
    metadata: Dict[str, Any]


class TaskDecomposerTool:
    """Enhanced task decomposer for ADOS orchestrator"""
    
    def __init__(self):
        """Initialize the task decomposer"""
        self.logger = logging.getLogger(__name__)
        
        # Task patterns and keywords
        self.crew_keywords = {
            "backend": ["api", "backend", "database", "server", "endpoint", "model", "schema", "service"],
            "frontend": ["ui", "frontend", "interface", "component", "page", "view", "css", "styling"],
            "security": ["security", "auth", "permission", "encryption", "vulnerability", "token"],
            "quality": ["test", "testing", "validation", "quality", "lint", "review", "coverage"],
            "integration": ["integration", "third-party", "external", "webhook", "sync", "pipeline"],
            "deployment": ["deploy", "deployment", "infrastructure", "docker", "kubernetes", "ci/cd"],
            "orchestrator": ["orchestrate", "coordinate", "manage", "plan", "decompose", "complex"]
        }
        
        # Complexity indicators
        self.complexity_indicators = {
            "simple": ["simple", "basic", "straightforward", "easy", "quick"],
            "moderate": ["moderate", "standard", "normal", "medium", "regular"],
            "complex": ["complex", "advanced", "sophisticated", "intricate", "detailed"],
            "high": ["high", "very", "extremely", "highly", "massive", "comprehensive"]
        }
        
        # Effort estimation keywords
        self.effort_keywords = {
            "1-2 hours": ["quick", "simple", "basic", "easy", "small"],
            "4-8 hours": ["moderate", "standard", "normal", "medium"],
            "1-2 days": ["complex", "detailed", "comprehensive", "full"],
            "3-5 days": ["advanced", "sophisticated", "enterprise", "complete"],
            "1-2 weeks": ["massive", "extensive", "system-wide", "architectural"]
        }
        
        # Common task patterns
        self.task_patterns = {
            "create": r"create|build|develop|implement|generate|construct",
            "modify": r"modify|update|change|alter|enhance|improve",
            "test": r"test|verify|validate|check|ensure",
            "deploy": r"deploy|release|publish|launch|deliver",
            "integrate": r"integrate|connect|sync|link|merge",
            "analyze": r"analyze|review|audit|assess|evaluate"
        }
    
    def decompose_task(self, task_description: str, context: Optional[Dict[str, Any]] = None) -> TaskDecomposition:
        """Decompose a task into subtasks"""
        try:
            self.logger.info(f"Decomposing task: {task_description}")
            
            # Analyze task complexity
            complexity_analysis = self._analyze_complexity(task_description)
            
            # Generate subtasks
            subtasks = self._generate_subtasks(task_description, complexity_analysis)
            
            # Determine execution order
            execution_order = self._determine_execution_order(subtasks)
            
            # Calculate crew distribution
            crew_distribution = self._calculate_crew_distribution(subtasks)
            
            # Build dependency graph
            dependency_graph = self._build_dependency_graph(subtasks)
            
            # Estimate total duration
            estimated_duration = self._estimate_total_duration(subtasks)
            
            # Create decomposition result
            decomposition = TaskDecomposition(
                original_task=task_description,
                subtasks=subtasks,
                execution_order=execution_order,
                estimated_duration=estimated_duration,
                complexity_analysis=complexity_analysis,
                crew_distribution=crew_distribution,
                dependency_graph=dependency_graph,
                metadata={
                    "decomposition_timestamp": datetime.now().isoformat(),
                    "decomposer_version": "1.0",
                    "context": context or {}
                }
            )
            
            self.logger.info(f"Task decomposed into {len(subtasks)} subtasks")
            return decomposition
            
        except Exception as e:
            self.logger.error(f"Failed to decompose task: {e}")
            return TaskDecomposition(
                original_task=task_description,
                subtasks=[],
                execution_order=[],
                estimated_duration="unknown",
                complexity_analysis={"error": str(e)},
                crew_distribution={},
                dependency_graph={},
                metadata={"error": str(e)}
            )
    
    def _analyze_complexity(self, task_description: str) -> Dict[str, Any]:
        """Analyze task complexity"""
        text = task_description.lower()
        
        # Score complexity indicators
        complexity_scores = {}
        for level, keywords in self.complexity_indicators.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                complexity_scores[level] = score
        
        # Determine overall complexity
        if complexity_scores:
            max_complexity = max(complexity_scores, key=complexity_scores.get)
        else:
            max_complexity = "moderate"
        
        # Additional complexity factors
        factors = {
            "multiple_crews": len([crew for crew, keywords in self.crew_keywords.items() 
                                 if any(keyword in text for keyword in keywords)]) > 1,
            "integration_required": any(keyword in text for keyword in 
                                     ["integrate", "connect", "sync", "third-party", "external"]),
            "security_concerns": any(keyword in text for keyword in 
                                   ["security", "auth", "permission", "encryption"]),
            "performance_critical": any(keyword in text for keyword in 
                                      ["performance", "speed", "optimization", "scale"]),
            "ui_components": any(keyword in text for keyword in 
                               ["ui", "interface", "component", "page", "view"]),
            "data_processing": any(keyword in text for keyword in 
                                 ["data", "database", "model", "schema", "query"])
        }
        
        # Calculate complexity score
        base_score = {"simple": 1, "moderate": 2, "complex": 3, "high": 4}.get(max_complexity, 2)
        factor_score = sum(1 for factor in factors.values() if factor)
        
        total_score = base_score + factor_score
        final_complexity = "simple" if total_score <= 2 else "moderate" if total_score <= 4 else "complex" if total_score <= 6 else "high"
        
        return {
            "level": final_complexity,
            "score": total_score,
            "factors": factors,
            "keyword_matches": complexity_scores
        }
    
    def _generate_subtasks(self, task_description: str, complexity_analysis: Dict[str, Any]) -> List[SubTask]:
        """Generate subtasks based on task description and complexity"""
        subtasks = []
        text = task_description.lower()
        
        # Determine primary action
        primary_action = self._determine_primary_action(text)
        
        # Determine involved crews
        involved_crews = self._determine_involved_crews(text)
        
        # Generate subtasks based on complexity and action
        if complexity_analysis["level"] == "simple":
            subtasks = self._generate_simple_subtasks(task_description, primary_action, involved_crews)
        elif complexity_analysis["level"] == "moderate":
            subtasks = self._generate_moderate_subtasks(task_description, primary_action, involved_crews)
        elif complexity_analysis["level"] == "complex":
            subtasks = self._generate_complex_subtasks(task_description, primary_action, involved_crews)
        else:  # high complexity
            subtasks = self._generate_high_complexity_subtasks(task_description, primary_action, involved_crews)
        
        return subtasks
    
    def _determine_primary_action(self, text: str) -> str:
        """Determine primary action from task text"""
        for action, pattern in self.task_patterns.items():
            if re.search(pattern, text):
                return action
        return "create"  # default
    
    def _determine_involved_crews(self, text: str) -> List[str]:
        """Determine which crews are involved in the task"""
        involved_crews = []
        
        for crew, keywords in self.crew_keywords.items():
            if any(keyword in text for keyword in keywords):
                involved_crews.append(crew)
        
        # Always include orchestrator for coordination
        if len(involved_crews) > 1 and "orchestrator" not in involved_crews:
            involved_crews.append("orchestrator")
        
        # Default to orchestrator if no specific crew identified
        if not involved_crews:
            involved_crews = ["orchestrator"]
        
        return involved_crews
    
    def _generate_simple_subtasks(self, task_description: str, action: str, crews: List[str]) -> List[SubTask]:
        """Generate subtasks for simple tasks"""
        subtasks = []
        
        # Single main task
        main_crew = crews[0] if crews else "orchestrator"
        
        subtasks.append(SubTask(
            id="subtask_1",
            title=f"{action.capitalize()} implementation",
            description=task_description,
            crew=main_crew,
            priority="medium",
            estimated_effort="1-2 hours",
            dependencies=[],
            acceptance_criteria=[
                "Implementation completed successfully",
                "Basic functionality working",
                "No critical errors"
            ],
            complexity="simple",
            tags=["main", action]
        ))
        
        return subtasks
    
    def _generate_moderate_subtasks(self, task_description: str, action: str, crews: List[str]) -> List[SubTask]:
        """Generate subtasks for moderate complexity tasks"""
        subtasks = []
        
        # Planning phase
        subtasks.append(SubTask(
            id="subtask_1",
            title="Planning and analysis",
            description=f"Analyze requirements and plan implementation for: {task_description}",
            crew="orchestrator",
            priority="high",
            estimated_effort="1-2 hours",
            dependencies=[],
            acceptance_criteria=[
                "Requirements analyzed",
                "Implementation plan created",
                "Dependencies identified"
            ],
            complexity="simple",
            tags=["planning", "analysis"]
        ))
        
        # Implementation phase
        for i, crew in enumerate(crews[:3], 2):  # Limit to 3 crews
            subtasks.append(SubTask(
                id=f"subtask_{i}",
                title=f"{crew.capitalize()} implementation",
                description=f"Implement {crew}-specific components for: {task_description}",
                crew=crew,
                priority="medium",
                estimated_effort="4-8 hours",
                dependencies=["subtask_1"],
                acceptance_criteria=[
                    f"{crew.capitalize()} components implemented",
                    "Integration points defined",
                    "Basic testing completed"
                ],
                complexity="moderate",
                tags=["implementation", crew]
            ))
        
        # Integration phase
        if len(crews) > 1:
            subtasks.append(SubTask(
                id=f"subtask_{len(subtasks) + 1}",
                title="Integration and testing",
                description=f"Integrate components and test complete solution",
                crew="quality",
                priority="high",
                estimated_effort="2-4 hours",
                dependencies=[f"subtask_{i}" for i in range(2, len(crews) + 2)],
                acceptance_criteria=[
                    "All components integrated",
                    "End-to-end testing completed",
                    "Quality checks passed"
                ],
                complexity="moderate",
                tags=["integration", "testing"]
            ))
        
        return subtasks
    
    def _generate_complex_subtasks(self, task_description: str, action: str, crews: List[str]) -> List[SubTask]:
        """Generate subtasks for complex tasks"""
        subtasks = []
        
        # Discovery phase
        subtasks.append(SubTask(
            id="subtask_1",
            title="Discovery and requirements analysis",
            description=f"Comprehensive analysis of requirements for: {task_description}",
            crew="orchestrator",
            priority="high",
            estimated_effort="4-8 hours",
            dependencies=[],
            acceptance_criteria=[
                "Detailed requirements documented",
                "Technical specifications created",
                "Risk analysis completed",
                "Resource requirements identified"
            ],
            complexity="moderate",
            tags=["discovery", "requirements"]
        ))
        
        # Architecture phase
        subtasks.append(SubTask(
            id="subtask_2",
            title="Architecture design",
            description=f"Design system architecture for: {task_description}",
            crew="orchestrator",
            priority="high",
            estimated_effort="1-2 days",
            dependencies=["subtask_1"],
            acceptance_criteria=[
                "System architecture designed",
                "Component interfaces defined",
                "Database schema planned",
                "API specifications created"
            ],
            complexity="complex",
            tags=["architecture", "design"]
        ))
        
        # Implementation phases for each crew
        for i, crew in enumerate(crews[:4], 3):  # Limit to 4 crews
            subtasks.append(SubTask(
                id=f"subtask_{i}",
                title=f"{crew.capitalize()} implementation",
                description=f"Implement {crew}-specific features for: {task_description}",
                crew=crew,
                priority="medium",
                estimated_effort="1-2 days",
                dependencies=["subtask_2"],
                acceptance_criteria=[
                    f"{crew.capitalize()} features implemented",
                    "Unit tests written",
                    "Documentation updated",
                    "Code review completed"
                ],
                complexity="complex",
                tags=["implementation", crew]
            ))
        
        # Integration phase
        subtasks.append(SubTask(
            id=f"subtask_{len(subtasks) + 1}",
            title="System integration",
            description=f"Integrate all components and perform system testing",
            crew="integration",
            priority="high",
            estimated_effort="3-5 days",
            dependencies=[f"subtask_{i}" for i in range(3, len(crews) + 3)],
            acceptance_criteria=[
                "All systems integrated",
                "Integration tests passed",
                "Performance benchmarks met",
                "Security validation completed"
            ],
            complexity="complex",
            tags=["integration", "testing"]
        ))
        
        # Deployment phase
        subtasks.append(SubTask(
            id=f"subtask_{len(subtasks) + 1}",
            title="Deployment and monitoring",
            description=f"Deploy solution and setup monitoring",
            crew="deployment",
            priority="medium",
            estimated_effort="1-2 days",
            dependencies=[f"subtask_{len(subtasks)}"],
            acceptance_criteria=[
                "Solution deployed successfully",
                "Monitoring configured",
                "Health checks implemented",
                "Documentation completed"
            ],
            complexity="moderate",
            tags=["deployment", "monitoring"]
        ))
        
        return subtasks
    
    def _generate_high_complexity_subtasks(self, task_description: str, action: str, crews: List[str]) -> List[SubTask]:
        """Generate subtasks for high complexity tasks"""
        subtasks = []
        
        # Research phase
        subtasks.append(SubTask(
            id="subtask_1",
            title="Research and feasibility analysis",
            description=f"Research best practices and analyze feasibility for: {task_description}",
            crew="orchestrator",
            priority="high",
            estimated_effort="1-2 days",
            dependencies=[],
            acceptance_criteria=[
                "Market research completed",
                "Technical feasibility confirmed",
                "Best practices documented",
                "Risk mitigation strategies defined"
            ],
            complexity="complex",
            tags=["research", "feasibility"]
        ))
        
        # Architecture phase
        subtasks.append(SubTask(
            id="subtask_2",
            title="System architecture and design",
            description=f"Design comprehensive system architecture for: {task_description}",
            crew="orchestrator",
            priority="high",
            estimated_effort="3-5 days",
            dependencies=["subtask_1"],
            acceptance_criteria=[
                "Detailed architecture documented",
                "Scalability considerations addressed",
                "Security architecture defined",
                "Performance requirements specified"
            ],
            complexity="high",
            tags=["architecture", "design"]
        ))
        
        # Prototyping phase
        subtasks.append(SubTask(
            id="subtask_3",
            title="Prototype development",
            description=f"Build prototype to validate concepts for: {task_description}",
            crew="backend",
            priority="medium",
            estimated_effort="1-2 weeks",
            dependencies=["subtask_2"],
            acceptance_criteria=[
                "Working prototype created",
                "Key concepts validated",
                "Performance benchmarks established",
                "User feedback collected"
            ],
            complexity="high",
            tags=["prototype", "validation"]
        ))
        
        # Implementation phases for each crew
        for i, crew in enumerate(crews[:5], 4):  # Limit to 5 crews
            subtasks.append(SubTask(
                id=f"subtask_{i}",
                title=f"{crew.capitalize()} full implementation",
                description=f"Complete implementation of {crew}-specific features for: {task_description}",
                crew=crew,
                priority="medium",
                estimated_effort="1-2 weeks",
                dependencies=["subtask_3"],
                acceptance_criteria=[
                    f"{crew.capitalize()} features fully implemented",
                    "Comprehensive testing completed",
                    "Performance optimized",
                    "Security review passed",
                    "Documentation complete"
                ],
                complexity="high",
                tags=["implementation", crew]
            ))
        
        # Integration and testing phase
        subtasks.append(SubTask(
            id=f"subtask_{len(subtasks) + 1}",
            title="System integration and testing",
            description=f"Comprehensive integration and testing of all components",
            crew="integration",
            priority="high",
            estimated_effort="1-2 weeks",
            dependencies=[f"subtask_{i}" for i in range(4, len(crews) + 4)],
            acceptance_criteria=[
                "All systems integrated",
                "End-to-end testing completed",
                "Load testing passed",
                "Security testing completed",
                "User acceptance testing passed"
            ],
            complexity="high",
            tags=["integration", "testing"]
        ))
        
        # Deployment and monitoring phase
        subtasks.append(SubTask(
            id=f"subtask_{len(subtasks) + 1}",
            title="Production deployment",
            description=f"Deploy to production with monitoring and support",
            crew="deployment",
            priority="high",
            estimated_effort="3-5 days",
            dependencies=[f"subtask_{len(subtasks)}"],
            acceptance_criteria=[
                "Production deployment completed",
                "Monitoring and alerting configured",
                "Disaster recovery tested",
                "Documentation finalized",
                "Team training completed"
            ],
            complexity="complex",
            tags=["deployment", "production"]
        ))
        
        return subtasks
    
    def _determine_execution_order(self, subtasks: List[SubTask]) -> List[str]:
        """Determine optimal execution order based on dependencies"""
        # Simple topological sort
        visited = set()
        order = []
        
        def dfs(task_id: str):
            if task_id in visited:
                return
            
            visited.add(task_id)
            
            # Find the task
            task = next((t for t in subtasks if t.id == task_id), None)
            if task:
                # Visit dependencies first
                for dep in task.dependencies:
                    dfs(dep)
                
                order.append(task_id)
        
        # Start with tasks that have no dependencies
        for task in subtasks:
            if not task.dependencies:
                dfs(task.id)
        
        # Add remaining tasks
        for task in subtasks:
            if task.id not in visited:
                dfs(task.id)
        
        return order
    
    def _calculate_crew_distribution(self, subtasks: List[SubTask]) -> Dict[str, int]:
        """Calculate how many subtasks each crew has"""
        distribution = {}
        
        for task in subtasks:
            crew = task.crew
            distribution[crew] = distribution.get(crew, 0) + 1
        
        return distribution
    
    def _build_dependency_graph(self, subtasks: List[SubTask]) -> Dict[str, List[str]]:
        """Build dependency graph for visualization"""
        graph = {}
        
        for task in subtasks:
            graph[task.id] = task.dependencies
        
        return graph
    
    def _estimate_total_duration(self, subtasks: List[SubTask]) -> str:
        """Estimate total duration considering dependencies"""
        # Simple estimation based on effort keywords
        effort_hours = {
            "1-2 hours": 1.5,
            "4-8 hours": 6,
            "1-2 days": 16,
            "3-5 days": 32,
            "1-2 weeks": 80
        }
        
        # Calculate parallel execution time
        # This is a simplified calculation
        max_parallel_time = 0
        total_effort = 0
        
        for task in subtasks:
            hours = effort_hours.get(task.estimated_effort, 8)
            total_effort += hours
            max_parallel_time = max(max_parallel_time, hours)
        
        # Estimate based on dependencies and parallelization
        if total_effort <= 8:
            return "1 day"
        elif total_effort <= 40:
            return "1 week"
        elif total_effort <= 160:
            return "1 month"
        else:
            return "2+ months"
    
    def validate_decomposition(self, decomposition: TaskDecomposition) -> Dict[str, Any]:
        """Validate task decomposition"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "score": 0
        }
        
        # Check basic structure
        if not decomposition.subtasks:
            validation_result["errors"].append("No subtasks generated")
            validation_result["valid"] = False
            return validation_result
        
        # Check dependencies
        task_ids = {task.id for task in decomposition.subtasks}
        for task in decomposition.subtasks:
            for dep in task.dependencies:
                if dep not in task_ids:
                    validation_result["errors"].append(f"Task {task.id} has invalid dependency: {dep}")
                    validation_result["valid"] = False
        
        # Check for cycles
        if self._has_cycles(decomposition.dependency_graph):
            validation_result["errors"].append("Dependency cycle detected")
            validation_result["valid"] = False
        
        # Quality checks
        score = 0
        
        # Check if all subtasks have proper details
        for task in decomposition.subtasks:
            if task.title and task.description:
                score += 10
            if task.acceptance_criteria:
                score += 15
            if task.estimated_effort != "TBD":
                score += 10
        
        # Check crew distribution
        if len(decomposition.crew_distribution) > 1:
            score += 20  # Good crew distribution
        
        # Check execution order
        if len(decomposition.execution_order) == len(decomposition.subtasks):
            score += 15  # All tasks in execution order
        
        validation_result["score"] = score
        
        return validation_result
    
    def _has_cycles(self, graph: Dict[str, List[str]]) -> bool:
        """Check if dependency graph has cycles"""
        visited = set()
        rec_stack = set()
        
        def dfs(node):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in graph:
            if node not in visited:
                if dfs(node):
                    return True
        
        return False


# Tool instance for CrewAI
task_decomposer = TaskDecomposerTool()


# Helper functions for CrewAI tool integration
def decompose_task(task_description: str) -> str:
    """Decompose task into subtasks"""
    decomposition = task_decomposer.decompose_task(task_description)
    
    return f"Task decomposed into {len(decomposition.subtasks)} subtasks:\n" + \
           "\n".join([f"- {task.title} ({task.crew})" for task in decomposition.subtasks[:5]]) + \
           f"\nEstimated duration: {decomposition.estimated_duration}"


def get_task_complexity(task_description: str) -> str:
    """Analyze task complexity"""
    complexity = task_decomposer._analyze_complexity(task_description)
    
    return f"Task complexity: {complexity['level']} (score: {complexity['score']})\n" + \
           f"Factors: {', '.join([k for k, v in complexity['factors'].items() if v])}"


def get_crew_assignments(task_description: str) -> str:
    """Get crew assignments for task"""
    decomposition = task_decomposer.decompose_task(task_description)
    
    return f"Crew distribution: {decomposition.crew_distribution}"