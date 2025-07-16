"""
Memory Writer Tool
Enhanced memory operations for ADOS orchestrator
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class MemoryEntry:
    """Memory entry data structure"""
    id: str
    content: str
    metadata: Dict[str, Any]
    timestamp: str
    crew: str
    agent: str
    category: str


class MemoryWriter:
    """Enhanced memory writer for ADOS system"""
    
    def __init__(self, base_path: str = "dev-agent-system/memory"):
        """Initialize the memory writer"""
        self.base_path = Path(base_path)
        self.logger = logging.getLogger(__name__)
        
        # Memory categories
        self.categories = {
            "task": "task_memory",
            "crew": "crew_memory", 
            "system": "system_memory",
            "knowledge": "knowledge_base",
            "performance": "performance_memory",
            "error": "error_memory"
        }
        
        # Ensure memory directories exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure all memory directories exist"""
        try:
            self.base_path.mkdir(parents=True, exist_ok=True)
            
            # Create category directories
            for category in self.categories.values():
                (self.base_path / category).mkdir(exist_ok=True)
            
            # Create crew-specific directories
            crew_memory_path = self.base_path / "crew_memory"
            crews = ["orchestrator", "backend", "security", "quality", "integration", "deployment", "frontend"]
            
            for crew in crews:
                (crew_memory_path / crew).mkdir(exist_ok=True)
            
        except Exception as e:
            self.logger.error(f"Failed to create memory directories: {e}")
    
    def write_memory(self, content: str, category: str, crew: str = "orchestrator", 
                    agent: str = "system", metadata: Optional[Dict[str, Any]] = None) -> str:
        """Write content to memory"""
        try:
            # Generate unique ID
            memory_id = f"{category}_{crew}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create memory entry
            entry = MemoryEntry(
                id=memory_id,
                content=content,
                metadata=metadata or {},
                timestamp=datetime.now().isoformat(),
                crew=crew,
                agent=agent,
                category=category
            )
            
            # Determine file path
            if category in self.categories:
                if category == "crew":
                    file_path = self.base_path / "crew_memory" / crew / f"{memory_id}.json"
                else:
                    file_path = self.base_path / self.categories[category] / f"{memory_id}.json"
            else:
                file_path = self.base_path / "system_memory" / f"{memory_id}.json"
            
            # Write to file
            with open(file_path, 'w') as f:
                json.dump(asdict(entry), f, indent=2)
            
            self.logger.info(f"Memory written: {memory_id}")
            return memory_id
            
        except Exception as e:
            self.logger.error(f"Failed to write memory: {e}")
            return ""
    
    def read_memory(self, memory_id: str) -> Optional[MemoryEntry]:
        """Read memory entry by ID"""
        try:
            # Search for memory file
            for category_dir in self.base_path.iterdir():
                if category_dir.is_dir():
                    # Check direct files
                    memory_file = category_dir / f"{memory_id}.json"
                    if memory_file.exists():
                        with open(memory_file, 'r') as f:
                            data = json.load(f)
                        return MemoryEntry(**data)
                    
                    # Check crew subdirectories
                    for crew_dir in category_dir.iterdir():
                        if crew_dir.is_dir():
                            memory_file = crew_dir / f"{memory_id}.json"
                            if memory_file.exists():
                                with open(memory_file, 'r') as f:
                                    data = json.load(f)
                                return MemoryEntry(**data)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to read memory {memory_id}: {e}")
            return None
    
    def update_memory(self, memory_id: str, content: str, 
                     metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Update existing memory entry"""
        try:
            # Read existing entry
            entry = self.read_memory(memory_id)
            if not entry:
                return False
            
            # Update content and metadata
            entry.content = content
            if metadata:
                entry.metadata.update(metadata)
            entry.timestamp = datetime.now().isoformat()
            
            # Find and update file
            for category_dir in self.base_path.iterdir():
                if category_dir.is_dir():
                    memory_file = category_dir / f"{memory_id}.json"
                    if memory_file.exists():
                        with open(memory_file, 'w') as f:
                            json.dump(asdict(entry), f, indent=2)
                        return True
                    
                    # Check crew subdirectories
                    for crew_dir in category_dir.iterdir():
                        if crew_dir.is_dir():
                            memory_file = crew_dir / f"{memory_id}.json"
                            if memory_file.exists():
                                with open(memory_file, 'w') as f:
                                    json.dump(asdict(entry), f, indent=2)
                                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to update memory {memory_id}: {e}")
            return False
    
    def search_memory(self, query: str, category: Optional[str] = None, 
                     crew: Optional[str] = None) -> List[MemoryEntry]:
        """Search memory entries"""
        try:
            results = []
            
            # Determine search directories
            search_dirs = []
            if category and category in self.categories:
                if category == "crew" and crew:
                    search_dirs = [self.base_path / "crew_memory" / crew]
                else:
                    search_dirs = [self.base_path / self.categories[category]]
            else:
                search_dirs = [self.base_path]
            
            # Search through directories
            for search_dir in search_dirs:
                for file_path in search_dir.rglob("*.json"):
                    try:
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                        
                        entry = MemoryEntry(**data)
                        
                        # Check if query matches
                        if (query.lower() in entry.content.lower() or
                            query.lower() in entry.id.lower() or
                            any(query.lower() in str(v).lower() for v in entry.metadata.values())):
                            
                            # Apply filters
                            if crew and entry.crew != crew:
                                continue
                            if category and entry.category != category:
                                continue
                            
                            results.append(entry)
                            
                    except Exception as e:
                        self.logger.warning(f"Failed to read memory file {file_path}: {e}")
                        continue
            
            # Sort by timestamp (newest first)
            results.sort(key=lambda x: x.timestamp, reverse=True)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to search memory: {e}")
            return []
    
    def list_memory(self, category: Optional[str] = None, 
                   crew: Optional[str] = None, limit: int = 50) -> List[MemoryEntry]:
        """List memory entries"""
        try:
            results = []
            
            # Determine search directories
            search_dirs = []
            if category and category in self.categories:
                if category == "crew" and crew:
                    search_dirs = [self.base_path / "crew_memory" / crew]
                else:
                    search_dirs = [self.base_path / self.categories[category]]
            else:
                search_dirs = [self.base_path]
            
            # Collect all entries
            for search_dir in search_dirs:
                for file_path in search_dir.rglob("*.json"):
                    try:
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                        
                        entry = MemoryEntry(**data)
                        
                        # Apply filters
                        if crew and entry.crew != crew:
                            continue
                        if category and entry.category != category:
                            continue
                        
                        results.append(entry)
                        
                    except Exception as e:
                        self.logger.warning(f"Failed to read memory file {file_path}: {e}")
                        continue
            
            # Sort by timestamp (newest first)
            results.sort(key=lambda x: x.timestamp, reverse=True)
            
            # Apply limit
            return results[:limit]
            
        except Exception as e:
            self.logger.error(f"Failed to list memory: {e}")
            return []
    
    def delete_memory(self, memory_id: str) -> bool:
        """Delete memory entry"""
        try:
            # Find and delete file
            for category_dir in self.base_path.iterdir():
                if category_dir.is_dir():
                    memory_file = category_dir / f"{memory_id}.json"
                    if memory_file.exists():
                        memory_file.unlink()
                        self.logger.info(f"Memory deleted: {memory_id}")
                        return True
                    
                    # Check crew subdirectories
                    for crew_dir in category_dir.iterdir():
                        if crew_dir.is_dir():
                            memory_file = crew_dir / f"{memory_id}.json"
                            if memory_file.exists():
                                memory_file.unlink()
                                self.logger.info(f"Memory deleted: {memory_id}")
                                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to delete memory {memory_id}: {e}")
            return False
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        try:
            stats = {
                "total_entries": 0,
                "by_category": {},
                "by_crew": {},
                "disk_usage": 0,
                "latest_entry": None
            }
            
            latest_timestamp = None
            
            # Collect statistics
            for category_dir in self.base_path.iterdir():
                if category_dir.is_dir():
                    category_name = category_dir.name
                    stats["by_category"][category_name] = 0
                    
                    for file_path in category_dir.rglob("*.json"):
                        try:
                            # Count file
                            stats["total_entries"] += 1
                            stats["by_category"][category_name] += 1
                            
                            # Add to disk usage
                            stats["disk_usage"] += file_path.stat().st_size
                            
                            # Read for crew stats and latest timestamp
                            with open(file_path, 'r') as f:
                                data = json.load(f)
                            
                            crew = data.get("crew", "unknown")
                            if crew not in stats["by_crew"]:
                                stats["by_crew"][crew] = 0
                            stats["by_crew"][crew] += 1
                            
                            # Check if this is the latest entry
                            timestamp = data.get("timestamp")
                            if timestamp and (latest_timestamp is None or timestamp > latest_timestamp):
                                latest_timestamp = timestamp
                                stats["latest_entry"] = data.get("id")
                            
                        except Exception as e:
                            self.logger.warning(f"Failed to process file {file_path}: {e}")
                            continue
            
            # Convert disk usage to human readable
            if stats["disk_usage"] > 1024 * 1024:
                stats["disk_usage_formatted"] = f"{stats['disk_usage'] / (1024 * 1024):.1f} MB"
            elif stats["disk_usage"] > 1024:
                stats["disk_usage_formatted"] = f"{stats['disk_usage'] / 1024:.1f} KB"
            else:
                stats["disk_usage_formatted"] = f"{stats['disk_usage']} bytes"
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get memory stats: {e}")
            return {"error": str(e)}
    
    def cleanup_old_entries(self, days: int = 30) -> int:
        """Clean up old memory entries"""
        try:
            cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
            deleted_count = 0
            
            for category_dir in self.base_path.iterdir():
                if category_dir.is_dir():
                    for file_path in category_dir.rglob("*.json"):
                        try:
                            # Check file age
                            if file_path.stat().st_mtime < cutoff_date:
                                file_path.unlink()
                                deleted_count += 1
                                
                        except Exception as e:
                            self.logger.warning(f"Failed to check/delete file {file_path}: {e}")
                            continue
            
            self.logger.info(f"Cleaned up {deleted_count} old memory entries")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old entries: {e}")
            return 0


# Tool instance for CrewAI
memory_writer = MemoryWriter()


# Helper functions for CrewAI tool integration
def write_task_memory(content: str, crew: str = "orchestrator", agent: str = "system") -> str:
    """Write task-related memory"""
    memory_id = memory_writer.write_memory(content, "task", crew, agent)
    return f"Task memory written: {memory_id}"


def write_crew_memory(content: str, crew: str, agent: str = "system") -> str:
    """Write crew-specific memory"""
    memory_id = memory_writer.write_memory(content, "crew", crew, agent)
    return f"Crew memory written: {memory_id}"


def search_memory(query: str, category: str = None) -> str:
    """Search memory entries"""
    results = memory_writer.search_memory(query, category)
    if not results:
        return f"No memory entries found for query: {query}"
    
    return f"Found {len(results)} memory entries:\n" + "\n".join([
        f"- {entry.id}: {entry.content[:100]}..." for entry in results[:5]
    ])


def get_memory_status() -> str:
    """Get memory system status"""
    stats = memory_writer.get_memory_stats()
    return f"Memory Status: {stats['total_entries']} entries, {stats['disk_usage_formatted']}"