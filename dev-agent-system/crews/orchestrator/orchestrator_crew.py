"""
ADOS Orchestrator Crew Implementation
Specialized crew with system awareness and intelligent task dispatch
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from crewai import Agent, Crew, Task, Process
# from crewai.project import CrewBase

from config.config_loader import ConfigLoader
from orchestrator.agent_factory import AgentFactory


class OrchestratorCrew:
    """Specialized orchestrator crew with system awareness and intelligent dispatch"""
    
    def __init__(self, config_loader: ConfigLoader, agent_factory: AgentFactory):
        """Initialize the orchestrator crew"""
        self.config_loader = config_loader
        self.agent_factory = agent_factory
        self.logger = logging.getLogger(__name__)
        
        # System state monitoring
        self.system_status = {}
        self.crew_health = {}
        self.task_queue = []
        self.performance_metrics = {}
        
        # Initialize the crew
        self.initialize_system_awareness()
    
    def initialize_system_awareness(self) -> bool:
        """Initialize system awareness module"""
        try:
            self.logger.info("Initializing orchestrator crew system awareness...")
            
            # Initialize monitoring systems
            self._setup_crew_monitoring()
            self._setup_performance_tracking()
            self._setup_task_queue_management()
            
            self.logger.info("System awareness initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize system awareness: {e}")
            return False
    
    def _setup_crew_monitoring(self):
        """Setup crew health monitoring"""
        self.crew_health = {
            "orchestrator": {"status": "active", "load": 0, "last_check": None},
            "backend": {"status": "ready", "load": 0, "last_check": None},
            "security": {"status": "ready", "load": 0, "last_check": None},
            "quality": {"status": "ready", "load": 0, "last_check": None},
            "integration": {"status": "ready", "load": 0, "last_check": None},
            "deployment": {"status": "ready", "load": 0, "last_check": None},
            "frontend": {"status": "ready", "load": 0, "last_check": None}
        }
    
    def _setup_performance_tracking(self):
        """Setup performance monitoring"""
        self.performance_metrics = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "average_completion_time": 0.0,
            "crew_utilization": {},
            "system_load": 0.0,
            "start_time": datetime.now()
        }
    
    def _setup_task_queue_management(self):
        """Setup task queue management"""
        self.task_queue = []
    
    def monitor_crew_health(self, crew_name: str) -> Dict[str, Any]:
        """Monitor health of a specific crew"""
        if crew_name not in self.crew_health:
            return {"status": "unknown", "error": f"Crew '{crew_name}' not found"}
        
        health_status = self.crew_health[crew_name].copy()
        
        # Update last check timestamp
        health_status["last_check"] = datetime.now().isoformat()
        self.crew_health[crew_name]["last_check"] = health_status["last_check"]
        
        # Simulate health check logic
        if health_status["load"] > 80:
            health_status["status"] = "overloaded"
        elif health_status["load"] > 50:
            health_status["status"] = "busy"
        else:
            health_status["status"] = "ready"
        
        return health_status
    
    def monitor_all_crews(self) -> Dict[str, Dict[str, Any]]:
        """Monitor health of all crews"""
        health_report = {}
        
        for crew_name in self.crew_health.keys():
            health_report[crew_name] = self.monitor_crew_health(crew_name)
        
        return health_report
    
    def intelligent_task_dispatch(self, task_description: str, priority: str = "medium") -> Dict[str, Any]:
        """Intelligently dispatch tasks to appropriate crews"""
        try:
            self.logger.info(f"Dispatching task with priority {priority}: {task_description}")
            
            # Analyze task to determine best crew
            target_crew = self._analyze_task_for_crew(task_description)
            
            # Check crew availability
            crew_health = self.monitor_crew_health(target_crew)
            if crew_health["status"] in ["overloaded", "unavailable"]:
                # Find alternative crew or queue task
                return self._handle_crew_unavailable(task_description, target_crew, priority)
            
            # Dispatch to crew
            dispatch_result = {
                "task": task_description,
                "assigned_crew": target_crew,
                "priority": priority,
                "status": "dispatched",
                "timestamp": self._get_timestamp(),
                "crew_health": crew_health
            }
            
            # Update crew load
            self.crew_health[target_crew]["load"] += self._calculate_task_load(priority)
            
            # Update performance metrics
            self._update_performance_metrics(target_crew)
            
            self.logger.info(f"Task dispatched to crew '{target_crew}' successfully")
            return dispatch_result
            
        except Exception as e:
            self.logger.error(f"Task dispatch failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    def _analyze_task_for_crew(self, task_description: str) -> str:
        """Analyze task description to determine best crew"""
        task_lower = task_description.lower()
        
        # Advanced keyword-based routing with scoring
        crew_scores = {
            "backend": 0,
            "security": 0,
            "quality": 0,
            "deployment": 0,
            "frontend": 0,
            "integration": 0,
            "orchestrator": 0
        }
        
        # Backend keywords
        backend_keywords = ["api", "backend", "database", "server", "endpoint", "model", "schema"]
        crew_scores["backend"] = sum(1 for keyword in backend_keywords if keyword in task_lower)
        
        # Security keywords
        security_keywords = ["security", "auth", "vulnerability", "encrypt", "token", "permission"]
        crew_scores["security"] = sum(1 for keyword in security_keywords if keyword in task_lower)
        
        # Quality keywords
        quality_keywords = ["test", "quality", "lint", "review", "validate", "check"]
        crew_scores["quality"] = sum(1 for keyword in quality_keywords if keyword in task_lower)
        
        # Deployment keywords
        deployment_keywords = ["deploy", "docker", "kubernetes", "cloud", "container", "helm"]
        crew_scores["deployment"] = sum(1 for keyword in deployment_keywords if keyword in task_lower)
        
        # Frontend keywords
        frontend_keywords = ["ui", "frontend", "react", "component", "style", "css"]
        crew_scores["frontend"] = sum(1 for keyword in frontend_keywords if keyword in task_lower)
        
        # Integration keywords
        integration_keywords = ["integration", "ci/cd", "pipeline", "webhook", "sync"]
        crew_scores["integration"] = sum(1 for keyword in integration_keywords if keyword in task_lower)
        
        # Orchestrator keywords
        orchestrator_keywords = ["orchestrate", "coordinate", "manage", "plan", "decompose"]
        crew_scores["orchestrator"] = sum(1 for keyword in orchestrator_keywords if keyword in task_lower)
        
        # Find best crew
        best_crew = max(crew_scores, key=crew_scores.get)
        
        # Default to orchestrator if no clear match
        if crew_scores[best_crew] == 0:
            best_crew = "orchestrator"
        
        return best_crew
    
    def _calculate_task_load(self, priority: str) -> int:
        """Calculate task load based on priority"""
        priority_weights = {
            "critical": 30,
            "high": 20,
            "medium": 10,
            "low": 5
        }
        return priority_weights.get(priority, 10)
    
    def _handle_crew_unavailable(self, task_description: str, target_crew: str, priority: str) -> Dict[str, Any]:
        """Handle situation when target crew is unavailable"""
        # Try to find alternative crew
        alternative_crew = self._find_alternative_crew(target_crew)
        
        if alternative_crew:
            self.logger.info(f"Redirecting task from '{target_crew}' to '{alternative_crew}'")
            return self.intelligent_task_dispatch(task_description, priority)
        
        # Queue the task for later
        queued_task = {
            "task": task_description,
            "target_crew": target_crew,
            "priority": priority,
            "queued_at": self._get_timestamp(),
            "status": "queued"
        }
        
        self.task_queue.append(queued_task)
        
        self.logger.warning(f"Crew '{target_crew}' unavailable, task queued")
        return queued_task
    
    def _find_alternative_crew(self, unavailable_crew: str) -> Optional[str]:
        """Find alternative crew when primary is unavailable"""
        alternatives = {
            "backend": ["orchestrator"],
            "security": ["orchestrator"],
            "quality": ["orchestrator"],
            "deployment": ["orchestrator"],
            "frontend": ["orchestrator"],
            "integration": ["orchestrator"],
            "orchestrator": ["backend", "quality"]  # Fallback options
        }
        
        for alternative in alternatives.get(unavailable_crew, []):
            if self.monitor_crew_health(alternative)["status"] in ["ready", "active"]:
                return alternative
        
        return None
    
    def _update_performance_metrics(self, crew_name: str):
        """Update performance metrics for crew utilization"""
        if crew_name not in self.performance_metrics["crew_utilization"]:
            self.performance_metrics["crew_utilization"][crew_name] = 0
        
        self.performance_metrics["crew_utilization"][crew_name] += 1
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        return datetime.now().isoformat()
    
    def get_system_overview(self) -> Dict[str, Any]:
        """Get comprehensive system overview"""
        return {
            "crew_health": self.crew_health,
            "performance_metrics": self.performance_metrics,
            "task_queue_length": len(self.task_queue),
            "active_tasks": self._count_active_tasks(),
            "system_status": self._determine_system_status(),
            "uptime": str(datetime.now() - self.performance_metrics["start_time"]),
            "total_crews": len(self.crew_health)
        }
    
    def _count_active_tasks(self) -> int:
        """Count currently active tasks"""
        return sum(1 for health in self.crew_health.values() if health["load"] > 0)
    
    def _determine_system_status(self) -> str:
        """Determine overall system status"""
        crew_statuses = [health["status"] for health in self.crew_health.values()]
        
        if "unavailable" in crew_statuses:
            return "degraded"
        elif "overloaded" in crew_statuses:
            return "stressed"
        elif all(status in ["active", "ready"] for status in crew_statuses):
            return "operational"
        else:
            return "mixed"
    
    def process_task_queue(self) -> List[Dict[str, Any]]:
        """Process queued tasks"""
        processed_tasks = []
        
        # Sort queue by priority
        self.task_queue.sort(key=lambda x: {
            "critical": 0, "high": 1, "medium": 2, "low": 3
        }.get(x["priority"], 2))
        
        for task in self.task_queue[:]:  # Copy to avoid modification during iteration
            crew_health = self.monitor_crew_health(task["target_crew"])
            
            if crew_health["status"] in ["active", "ready"]:
                # Process the task
                result = self.intelligent_task_dispatch(
                    task["task"], 
                    task["priority"]
                )
                
                if result["status"] == "dispatched":
                    processed_tasks.append(result)
                    self.task_queue.remove(task)
        
        return processed_tasks
    
    def complete_task(self, crew_name: str, success: bool = True):
        """Mark a task as completed and update metrics"""
        if crew_name in self.crew_health:
            # Reduce crew load
            self.crew_health[crew_name]["load"] = max(0, self.crew_health[crew_name]["load"] - 10)
            
            # Update performance metrics
            if success:
                self.performance_metrics["tasks_completed"] += 1
            else:
                self.performance_metrics["tasks_failed"] += 1
    
    def get_task_queue_status(self) -> Dict[str, Any]:
        """Get detailed task queue status"""
        return {
            "total_queued": len(self.task_queue),
            "by_priority": {
                "critical": len([t for t in self.task_queue if t["priority"] == "critical"]),
                "high": len([t for t in self.task_queue if t["priority"] == "high"]),
                "medium": len([t for t in self.task_queue if t["priority"] == "medium"]),
                "low": len([t for t in self.task_queue if t["priority"] == "low"])
            },
            "by_crew": {
                crew: len([t for t in self.task_queue if t["target_crew"] == crew])
                for crew in self.crew_health.keys()
            },
            "oldest_task": min(self.task_queue, key=lambda x: x["queued_at"])["queued_at"] if self.task_queue else None
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        health_status = {
            "status": "healthy",
            "timestamp": self._get_timestamp(),
            "checks": {
                "system_awareness": True,
                "crew_monitoring": True,
                "task_queue": True,
                "performance_tracking": True
            },
            "metrics": self.get_system_overview(),
            "issues": []
        }
        
        # Check for issues
        if len(self.task_queue) > 50:
            health_status["issues"].append("Task queue is getting large")
            health_status["status"] = "warning"
        
        if any(health["status"] == "overloaded" for health in self.crew_health.values()):
            health_status["issues"].append("Some crews are overloaded")
            health_status["status"] = "warning"
        
        failed_rate = (
            self.performance_metrics["tasks_failed"] / 
            max(1, self.performance_metrics["tasks_completed"] + self.performance_metrics["tasks_failed"])
        )
        
        if failed_rate > 0.1:  # More than 10% failure rate
            health_status["issues"].append("High task failure rate")
            health_status["status"] = "critical"
        
        return health_status