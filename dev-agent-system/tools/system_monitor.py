"""
System Monitor Tool
Real-time monitoring of crew health and system status
"""

import psutil
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class SystemMetrics:
    """System metrics data structure"""
    timestamp: str
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    active_processes: int
    system_load: float


@dataclass
class CrewHealth:
    """Crew health data structure"""
    crew_name: str
    status: str
    load: int
    last_activity: str
    response_time: float
    error_rate: float


class SystemMonitor:
    """System monitoring tool for ADOS orchestrator"""
    
    def __init__(self):
        """Initialize the system monitor"""
        self.logger = logging.getLogger(__name__)
        self.metrics_history: List[SystemMetrics] = []
        self.crew_health_history: Dict[str, List[CrewHealth]] = {}
        self.alerts: List[Dict[str, Any]] = []
        
    def get_system_metrics(self) -> SystemMetrics:
        """Get current system metrics"""
        try:
            # Get CPU usage
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # Get memory usage
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # Get disk usage
            disk = psutil.disk_usage('/')
            disk_usage = disk.percent
            
            # Get active processes
            active_processes = len(psutil.pids())
            
            # Calculate system load (average of CPU and memory)
            system_load = (cpu_usage + memory_usage) / 2
            
            metrics = SystemMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                disk_usage=disk_usage,
                active_processes=active_processes,
                system_load=system_load
            )
            
            # Store in history
            self.metrics_history.append(metrics)
            
            # Keep only last 100 entries
            if len(self.metrics_history) > 100:
                self.metrics_history = self.metrics_history[-100:]
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get system metrics: {e}")
            return SystemMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_usage=0.0,
                memory_usage=0.0,
                disk_usage=0.0,
                active_processes=0,
                system_load=0.0
            )
    
    def monitor_crew_health(self, crew_name: str, current_load: int = 0) -> CrewHealth:
        """Monitor health of a specific crew"""
        try:
            # Simulate crew health monitoring
            # In a real implementation, this would check actual crew status
            
            # Determine status based on load
            if current_load > 80:
                status = "overloaded"
            elif current_load > 50:
                status = "busy"
            elif current_load > 0:
                status = "active"
            else:
                status = "ready"
            
            # Simulate response time (would be measured in real implementation)
            response_time = min(1000, current_load * 10)  # ms
            
            # Simulate error rate (would be calculated from actual errors)
            error_rate = max(0, (current_load - 70) / 30 * 10)  # percentage
            
            health = CrewHealth(
                crew_name=crew_name,
                status=status,
                load=current_load,
                last_activity=datetime.now().isoformat(),
                response_time=response_time,
                error_rate=error_rate
            )
            
            # Store in history
            if crew_name not in self.crew_health_history:
                self.crew_health_history[crew_name] = []
            
            self.crew_health_history[crew_name].append(health)
            
            # Keep only last 50 entries per crew
            if len(self.crew_health_history[crew_name]) > 50:
                self.crew_health_history[crew_name] = self.crew_health_history[crew_name][-50:]
            
            # Check for alerts
            self._check_crew_alerts(health)
            
            return health
            
        except Exception as e:
            self.logger.error(f"Failed to monitor crew health for '{crew_name}': {e}")
            return CrewHealth(
                crew_name=crew_name,
                status="error",
                load=0,
                last_activity=datetime.now().isoformat(),
                response_time=0.0,
                error_rate=0.0
            )
    
    def _check_crew_alerts(self, health: CrewHealth):
        """Check for alert conditions"""
        alerts = []
        
        # Check for overload
        if health.status == "overloaded":
            alerts.append({
                "type": "overload",
                "crew": health.crew_name,
                "message": f"Crew {health.crew_name} is overloaded (load: {health.load}%)",
                "severity": "high",
                "timestamp": datetime.now().isoformat()
            })
        
        # Check for high error rate
        if health.error_rate > 5:
            alerts.append({
                "type": "error_rate",
                "crew": health.crew_name,
                "message": f"Crew {health.crew_name} has high error rate: {health.error_rate:.1f}%",
                "severity": "medium",
                "timestamp": datetime.now().isoformat()
            })
        
        # Check for slow response
        if health.response_time > 500:
            alerts.append({
                "type": "slow_response",
                "crew": health.crew_name,
                "message": f"Crew {health.crew_name} has slow response time: {health.response_time:.1f}ms",
                "severity": "low",
                "timestamp": datetime.now().isoformat()
            })
        
        # Add alerts to history
        self.alerts.extend(alerts)
        
        # Keep only last 100 alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
    
    def get_system_overview(self) -> Dict[str, Any]:
        """Get comprehensive system overview"""
        current_metrics = self.get_system_metrics()
        
        # Get crew health summary
        crew_summary = {}
        for crew_name, health_history in self.crew_health_history.items():
            if health_history:
                latest_health = health_history[-1]
                crew_summary[crew_name] = asdict(latest_health)
        
        # Get recent alerts
        recent_alerts = [
            alert for alert in self.alerts 
            if datetime.fromisoformat(alert['timestamp']) > datetime.now() - timedelta(hours=1)
        ]
        
        return {
            "system_metrics": asdict(current_metrics),
            "crew_health": crew_summary,
            "recent_alerts": recent_alerts,
            "total_alerts": len(self.alerts),
            "system_status": self._determine_system_status(current_metrics, crew_summary)
        }
    
    def _determine_system_status(self, metrics: SystemMetrics, crew_summary: Dict[str, Any]) -> str:
        """Determine overall system status"""
        # Check system metrics
        if metrics.cpu_usage > 90 or metrics.memory_usage > 90:
            return "critical"
        elif metrics.cpu_usage > 70 or metrics.memory_usage > 70:
            return "warning"
        
        # Check crew health
        if crew_summary:
            overloaded_crews = [
                crew for crew, health in crew_summary.items() 
                if health.get("status") == "overloaded"
            ]
            
            if overloaded_crews:
                return "warning"
        
        return "healthy"
    
    def get_metrics_history(self, hours: int = 1) -> List[SystemMetrics]:
        """Get metrics history for specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        return [
            metrics for metrics in self.metrics_history
            if datetime.fromisoformat(metrics.timestamp) > cutoff_time
        ]
    
    def get_crew_health_history(self, crew_name: str, hours: int = 1) -> List[CrewHealth]:
        """Get crew health history for specified hours"""
        if crew_name not in self.crew_health_history:
            return []
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        return [
            health for health in self.crew_health_history[crew_name]
            if datetime.fromisoformat(health.last_activity) > cutoff_time
        ]
    
    def get_alerts(self, severity: Optional[str] = None, hours: int = 24) -> List[Dict[str, Any]]:
        """Get alerts with optional filtering"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        filtered_alerts = [
            alert for alert in self.alerts
            if datetime.fromisoformat(alert['timestamp']) > cutoff_time
        ]
        
        if severity:
            filtered_alerts = [
                alert for alert in filtered_alerts
                if alert['severity'] == severity
            ]
        
        return filtered_alerts
    
    def clear_alerts(self):
        """Clear all alerts"""
        self.alerts.clear()
    
    def export_metrics(self, filename: str):
        """Export metrics to file"""
        try:
            import json
            
            export_data = {
                "metrics_history": [asdict(m) for m in self.metrics_history],
                "crew_health_history": {
                    crew: [asdict(h) for h in health_list]
                    for crew, health_list in self.crew_health_history.items()
                },
                "alerts": self.alerts,
                "export_timestamp": datetime.now().isoformat()
            }
            
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            self.logger.info(f"Metrics exported to {filename}")
            
        except Exception as e:
            self.logger.error(f"Failed to export metrics: {e}")
    
    def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        try:
            system_metrics = self.get_system_metrics()
            
            health_status = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "system_metrics": asdict(system_metrics),
                "checks": {
                    "cpu_usage": system_metrics.cpu_usage < 80,
                    "memory_usage": system_metrics.memory_usage < 80,
                    "disk_usage": system_metrics.disk_usage < 90,
                    "monitoring_active": True
                },
                "issues": []
            }
            
            # Check for issues
            if system_metrics.cpu_usage > 80:
                health_status["issues"].append("High CPU usage")
                health_status["status"] = "warning"
            
            if system_metrics.memory_usage > 80:
                health_status["issues"].append("High memory usage")
                health_status["status"] = "warning"
            
            if system_metrics.disk_usage > 90:
                health_status["issues"].append("High disk usage")
                health_status["status"] = "critical"
            
            # Check for recent critical alerts
            critical_alerts = [
                alert for alert in self.alerts
                if alert['severity'] == 'high' and 
                   datetime.fromisoformat(alert['timestamp']) > datetime.now() - timedelta(minutes=10)
            ]
            
            if critical_alerts:
                health_status["issues"].append(f"{len(critical_alerts)} critical alerts in last 10 minutes")
                health_status["status"] = "critical"
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                "status": "error",
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "checks": {
                    "cpu_usage": False,
                    "memory_usage": False,
                    "disk_usage": False,
                    "monitoring_active": False
                },
                "issues": ["Health check failed"]
            }


# Tool instance for CrewAI
system_monitor = SystemMonitor()


# Helper functions for CrewAI tool integration
def get_system_status() -> str:
    """Get current system status as string"""
    overview = system_monitor.get_system_overview()
    return f"System Status: {overview['system_status']}\nCPU: {overview['system_metrics']['cpu_usage']:.1f}%\nMemory: {overview['system_metrics']['memory_usage']:.1f}%"


def monitor_crew(crew_name: str, load: int = 0) -> str:
    """Monitor specific crew health"""
    health = system_monitor.monitor_crew_health(crew_name, load)
    return f"Crew {crew_name}: {health.status} (Load: {health.load}%, Response: {health.response_time:.1f}ms)"


def get_alerts() -> str:
    """Get recent alerts"""
    alerts = system_monitor.get_alerts(hours=1)
    if not alerts:
        return "No recent alerts"
    
    return f"Recent alerts ({len(alerts)}):\n" + "\n".join([
        f"- {alert['type']}: {alert['message']}" for alert in alerts[-5:]
    ])