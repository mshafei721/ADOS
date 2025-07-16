"""
ADOS Memory Coordinator
Memory coordination and file-based persistence system
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class MemoryCoordinator:
    """Memory coordinator for managing file-based memory and crew communication"""
    
    def __init__(self, config_loader=None, workspace_dir: Optional[Path] = None):
        """Initialize the memory coordinator"""
        self.workspace_dir = workspace_dir or Path("./workspace")
        self.config_loader = config_loader
        self.logger = logging.getLogger(__name__)
        
        # Initialize memory components
        self.vector_db = None
        self.crew_memory = {}
        self.session_memory = {}
        self.is_initialized = False
        
        # Load configuration
        self._load_memory_config()
        
        self.logger.info("MemoryCoordinator initialized")
    
    def _load_memory_config(self):
        """Load memory configuration from system settings"""
        if self.config_loader:
            try:
                self.settings = self.config_loader.load_system_settings()
                self.memory_config = self.settings.get("memory", {})
                self.logger.debug(f"Memory configuration loaded: {self.memory_config}")
            except Exception as e:
                self.logger.error(f"Failed to load memory configuration: {e}")
                self.memory_config = {}
        else:
            self.memory_config = {}
    
    def initialize_memory(self) -> bool:
        """Initialize memory system components"""
        try:
            self.logger.info("Initializing memory system...")
            
            # Initialize vector database (ChromaDB)
            self._initialize_vector_db()
            
            # Initialize crew memory directories
            self._initialize_crew_memory()
            
            # Initialize session memory
            self._initialize_session_memory()
            
            self.is_initialized = True
            self.logger.info("Memory system initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize memory system: {e}")
            self.is_initialized = False
            return False
    
    def _initialize_vector_db(self):
        """Initialize ChromaDB vector database"""
        try:
            import chromadb
            from chromadb.config import Settings
            
            vector_config = self.memory_config.get("vector_db", {})
            persist_directory = vector_config.get("persist_directory", "./memory/global_kb/chroma")
            collection_name = vector_config.get("collection_name", "ados_memory")
            
            # Create persist directory if it doesn't exist
            Path(persist_directory).mkdir(parents=True, exist_ok=True)
            
            # Initialize ChromaDB client
            self.vector_db = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            try:
                self.collection = self.vector_db.get_collection(collection_name)
                self.logger.debug(f"Retrieved existing collection: {collection_name}")
            except Exception:
                self.collection = self.vector_db.create_collection(
                    name=collection_name,
                    metadata={"description": "ADOS system memory collection"}
                )
                self.logger.debug(f"Created new collection: {collection_name}")
            
            self.logger.info(f"Vector database initialized with collection: {collection_name}")
            
        except ImportError:
            self.logger.error("ChromaDB not installed. Please install with: pip install chromadb")
            raise
        except Exception as e:
            self.logger.error(f"Failed to initialize vector database: {e}")
            raise
    
    def _initialize_crew_memory(self):
        """Initialize crew memory directories and files"""
        try:
            crew_config = self.memory_config.get("crew_memory", {})
            memory_dir = Path(crew_config.get("directory", "./memory/crew_memory"))
            
            # Create crew memory directory
            memory_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialize crew memory storage
            self.crew_memory = {}
            
            # Load existing crew memory files
            for crew_file in memory_dir.glob("*.json"):
                crew_name = crew_file.stem
                try:
                    with open(crew_file, 'r') as f:
                        self.crew_memory[crew_name] = json.load(f)
                    self.logger.debug(f"Loaded crew memory for: {crew_name}")
                except Exception as e:
                    self.logger.warning(f"Failed to load crew memory for {crew_name}: {e}")
                    self.crew_memory[crew_name] = {}
            
            self.logger.info(f"Crew memory initialized with {len(self.crew_memory)} crews")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize crew memory: {e}")
            raise
    
    def _initialize_session_memory(self):
        """Initialize session memory"""
        try:
            session_config = self.memory_config.get("session_memory", {})
            max_entries = session_config.get("max_entries", 1000)
            
            self.session_memory = {}
            self.session_max_entries = max_entries
            
            self.logger.info(f"Session memory initialized with max entries: {max_entries}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize session memory: {e}")
            raise
    
    def write_memory(self, crew_name: str, memory_type: str, content: str) -> bool:
        """Write memory for a specific crew"""
        if not self.is_initialized:
            self.logger.error("Memory system not initialized")
            return False
        
        try:
            if memory_type == "vector":
                return self._write_vector_memory(crew_name, content)
            elif memory_type == "crew":
                return self._write_crew_memory(crew_name, content)
            elif memory_type == "session":
                return self._write_session_memory(crew_name, content)
            else:
                self.logger.error(f"Unknown memory type: {memory_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to write memory for crew '{crew_name}': {e}")
            return False
    
    def _write_vector_memory(self, crew_name: str, content: str) -> bool:
        """Write to vector database"""
        try:
            import uuid
            
            # Generate unique ID for the memory entry
            memory_id = str(uuid.uuid4())
            
            # Add to vector database
            self.collection.add(
                ids=[memory_id],
                documents=[content],
                metadatas=[{
                    "crew_name": crew_name,
                    "timestamp": str(datetime.now()),
                    "memory_type": "vector"
                }]
            )
            
            self.logger.debug(f"Added vector memory for crew '{crew_name}' with ID: {memory_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to write vector memory: {e}")
            return False
    
    def _write_crew_memory(self, crew_name: str, content: str) -> bool:
        """Write to crew memory (JSON file)"""
        try:
            if crew_name not in self.crew_memory:
                self.crew_memory[crew_name] = {}
            
            # Add timestamp and content
            timestamp = datetime.now().isoformat()
            if "entries" not in self.crew_memory[crew_name]:
                self.crew_memory[crew_name]["entries"] = []
            
            self.crew_memory[crew_name]["entries"].append({
                "timestamp": timestamp,
                "content": content
            })
            
            # Save to file
            self._save_crew_memory(crew_name)
            
            self.logger.debug(f"Added crew memory for '{crew_name}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to write crew memory: {e}")
            return False
    
    def _write_session_memory(self, crew_name: str, content: str) -> bool:
        """Write to session memory"""
        try:
            if crew_name not in self.session_memory:
                self.session_memory[crew_name] = []
            
            # Add entry with timestamp
            entry = {
                "timestamp": datetime.now().isoformat(),
                "content": content
            }
            
            self.session_memory[crew_name].append(entry)
            
            # Enforce max entries limit
            if len(self.session_memory[crew_name]) > self.session_max_entries:
                self.session_memory[crew_name] = self.session_memory[crew_name][-self.session_max_entries:]
            
            self.logger.debug(f"Added session memory for '{crew_name}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to write session memory: {e}")
            return False
    
    def _save_crew_memory(self, crew_name: str):
        """Save crew memory to JSON file"""
        try:
            crew_config = self.memory_config.get("crew_memory", {})
            memory_dir = Path(crew_config.get("directory", "./memory/crew_memory"))
            memory_file = memory_dir / f"{crew_name}.json"
            
            # Check size limit
            max_size_mb = crew_config.get("max_size_mb", 100)
            current_size = len(json.dumps(self.crew_memory[crew_name]).encode('utf-8'))
            max_size_bytes = max_size_mb * 1024 * 1024
            
            if current_size > max_size_bytes:
                self.logger.warning(f"Crew memory for '{crew_name}' exceeds size limit. Truncating...")
                self._truncate_crew_memory(crew_name, max_size_bytes)
            
            with open(memory_file, 'w') as f:
                json.dump(self.crew_memory[crew_name], f, indent=2)
            
            self.logger.debug(f"Saved crew memory for '{crew_name}' to {memory_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save crew memory for '{crew_name}': {e}")
            raise
    
    def _truncate_crew_memory(self, crew_name: str, max_size_bytes: int):
        """Truncate crew memory to fit within size limit"""
        try:
            entries = self.crew_memory[crew_name].get("entries", [])
            
            # Remove oldest entries until within size limit
            while entries and len(json.dumps(self.crew_memory[crew_name]).encode('utf-8')) > max_size_bytes:
                entries.pop(0)
            
            self.crew_memory[crew_name]["entries"] = entries
            self.logger.debug(f"Truncated crew memory for '{crew_name}' to {len(entries)} entries")
            
        except Exception as e:
            self.logger.error(f"Failed to truncate crew memory for '{crew_name}': {e}")
    
    def read_memory(self, crew_name: str, memory_type: str, query: str = None) -> Optional[str]:
        """Read memory for a specific crew"""
        if not self.is_initialized:
            self.logger.error("Memory system not initialized")
            return None
        
        try:
            if memory_type == "vector":
                return self._read_vector_memory(crew_name, query)
            elif memory_type == "crew":
                return self._read_crew_memory(crew_name)
            elif memory_type == "session":
                return self._read_session_memory(crew_name)
            else:
                self.logger.error(f"Unknown memory type: {memory_type}")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to read memory for crew '{crew_name}': {e}")
            return None
    
    def _read_vector_memory(self, crew_name: str, query: str) -> Optional[str]:
        """Read from vector database using similarity search"""
        try:
            if not query:
                self.logger.warning("No query provided for vector memory search")
                return None
            
            # Perform similarity search
            results = self.collection.query(
                query_texts=[query],
                n_results=5,
                where={"crew_name": crew_name}
            )
            
            if results["documents"] and results["documents"][0]:
                # Return the most relevant result
                relevant_docs = results["documents"][0]
                self.logger.debug(f"Found {len(relevant_docs)} vector memory results for crew '{crew_name}'")
                return "\n".join(relevant_docs)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to read vector memory: {e}")
            return None
    
    def _read_crew_memory(self, crew_name: str) -> Optional[str]:
        """Read crew memory from JSON storage"""
        try:
            if crew_name not in self.crew_memory:
                return None
            
            entries = self.crew_memory[crew_name].get("entries", [])
            if not entries:
                return None
            
            # Return recent entries as formatted string
            recent_entries = entries[-10:]  # Last 10 entries
            formatted_entries = []
            
            for entry in recent_entries:
                formatted_entries.append(f"[{entry['timestamp']}] {entry['content']}")
            
            return "\n".join(formatted_entries)
            
        except Exception as e:
            self.logger.error(f"Failed to read crew memory: {e}")
            return None
    
    def _read_session_memory(self, crew_name: str) -> Optional[str]:
        """Read session memory"""
        try:
            if crew_name not in self.session_memory:
                return None
            
            entries = self.session_memory[crew_name]
            if not entries:
                return None
            
            # Return recent entries as formatted string
            recent_entries = entries[-10:]  # Last 10 entries
            formatted_entries = []
            
            for entry in recent_entries:
                formatted_entries.append(f"[{entry['timestamp']}] {entry['content']}")
            
            return "\n".join(formatted_entries)
            
        except Exception as e:
            self.logger.error(f"Failed to read session memory: {e}")
            return None
    
    def synchronize_memory(self) -> bool:
        """Synchronize memory across crews"""
        try:
            self.logger.info("Synchronizing memory across crews...")
            
            # Save all crew memory to files
            for crew_name in self.crew_memory:
                try:
                    self._save_crew_memory(crew_name)
                except Exception as e:
                    self.logger.error(f"Failed to save crew memory for '{crew_name}': {e}")
            
            # Persist vector database
            if self.vector_db:
                try:
                    self.vector_db.persist()
                    self.logger.debug("Vector database persisted")
                except Exception as e:
                    self.logger.warning(f"Failed to persist vector database: {e}")
            
            self.logger.info("Memory synchronization completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to synchronize memory: {e}")
            return False
    
    def get_memory_status(self) -> Dict[str, Any]:
        """Get memory system status"""
        try:
            # Calculate crew memory sizes
            crew_memory_info = {}
            for crew_name, data in self.crew_memory.items():
                entries_count = len(data.get("entries", []))
                size_bytes = len(json.dumps(data).encode('utf-8'))
                crew_memory_info[crew_name] = {
                    "entries_count": entries_count,
                    "size_bytes": size_bytes,
                    "size_mb": round(size_bytes / (1024 * 1024), 2)
                }
            
            # Calculate session memory info
            session_memory_info = {}
            for crew_name, entries in self.session_memory.items():
                session_memory_info[crew_name] = {
                    "entries_count": len(entries),
                    "max_entries": self.session_max_entries
                }
            
            # Vector database info
            vector_db_info = {}
            if self.collection:
                try:
                    vector_db_info = {
                        "collection_name": self.collection.name,
                        "document_count": self.collection.count()
                    }
                except Exception as e:
                    vector_db_info = {"error": str(e)}
            
            return {
                "initialized": self.is_initialized,
                "workspace_dir": str(self.workspace_dir),
                "vector_db": vector_db_info,
                "crew_memory": crew_memory_info,
                "session_memory": session_memory_info,
                "memory_config": self.memory_config
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get memory status: {e}")
            return {
                "initialized": self.is_initialized,
                "workspace_dir": str(self.workspace_dir),
                "error": str(e)
            }