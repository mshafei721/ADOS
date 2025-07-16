"""
PRD Parser Tool
Product Requirements Document parser for ADOS orchestrator
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Requirement:
    """Individual requirement data structure"""
    id: str
    title: str
    description: str
    priority: str
    category: str
    acceptance_criteria: List[str]
    dependencies: List[str]
    estimated_effort: str
    tags: List[str]


@dataclass
class PRDSection:
    """PRD section data structure"""
    title: str
    content: str
    requirements: List[Requirement]
    subsections: List['PRDSection']


@dataclass
class ParsedPRD:
    """Complete parsed PRD data structure"""
    title: str
    version: str
    overview: str
    sections: List[PRDSection]
    requirements: List[Requirement]
    metadata: Dict[str, Any]
    parse_timestamp: str


class PRDParser:
    """Product Requirements Document parser"""
    
    def __init__(self):
        """Initialize the PRD parser"""
        self.logger = logging.getLogger(__name__)
        
        # Common patterns for parsing
        self.patterns = {
            'requirement': r'(?:REQ|REQUIREMENT|FEATURE)\s*[:\-#]?\s*(\d+(?:\.\d+)*)\s*[:\-]?\s*(.+?)(?=\n\n|\nREQ|\nREQUIREMENT|\nFEATURE|\Z)',
            'priority': r'(?:PRIORITY|PRI)\s*[:\-]?\s*(HIGH|MEDIUM|LOW|CRITICAL)',
            'acceptance_criteria': r'(?:ACCEPTANCE\s*CRITERIA|AC)\s*[:\-]?\s*((?:[-*•]\s*.+\n?)+)',
            'dependencies': r'(?:DEPENDS\s*ON|DEPENDENCIES)\s*[:\-]?\s*((?:[-*•]\s*.+\n?)+)',
            'effort': r'(?:EFFORT|ESTIMATE|POINTS)\s*[:\-]?\s*(\d+(?:\.\d+)?\s*(?:HOURS?|DAYS?|WEEKS?|POINTS?|SP)?)',
            'tags': r'(?:TAGS|LABELS)\s*[:\-]?\s*((?:[-*•]\s*.+\n?)+)',
            'section': r'^#{1,6}\s+(.+)$',
            'subsection': r'^#{2,6}\s+(.+)$'
        }
    
    def parse_prd(self, content: str, title: str = "Untitled PRD") -> ParsedPRD:
        """Parse a complete PRD document"""
        try:
            self.logger.info(f"Parsing PRD: {title}")
            
            # Clean up content
            content = self._clean_content(content)
            
            # Extract metadata
            metadata = self._extract_metadata(content)
            
            # Extract overview
            overview = self._extract_overview(content)
            
            # Parse sections
            sections = self._parse_sections(content)
            
            # Extract all requirements
            requirements = self._extract_all_requirements(content)
            
            # Create parsed PRD
            parsed_prd = ParsedPRD(
                title=title,
                version=metadata.get('version', '1.0'),
                overview=overview,
                sections=sections,
                requirements=requirements,
                metadata=metadata,
                parse_timestamp=datetime.now().isoformat()
            )
            
            self.logger.info(f"PRD parsed successfully: {len(requirements)} requirements found")
            return parsed_prd
            
        except Exception as e:
            self.logger.error(f"Failed to parse PRD: {e}")
            return ParsedPRD(
                title=title,
                version="1.0",
                overview="",
                sections=[],
                requirements=[],
                metadata={"error": str(e)},
                parse_timestamp=datetime.now().isoformat()
            )
    
    def _clean_content(self, content: str) -> str:
        """Clean and normalize content"""
        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        # Normalize line endings
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove trailing spaces
        content = '\n'.join(line.rstrip() for line in content.split('\n'))
        
        return content
    
    def _extract_metadata(self, content: str) -> Dict[str, Any]:
        """Extract metadata from PRD"""
        metadata = {}
        
        # Look for version
        version_match = re.search(r'(?:VERSION|VER)\s*[:\-]?\s*(\d+(?:\.\d+)*)', content, re.IGNORECASE)
        if version_match:
            metadata['version'] = version_match.group(1)
        
        # Look for author
        author_match = re.search(r'(?:AUTHOR|BY)\s*[:\-]?\s*(.+)', content, re.IGNORECASE)
        if author_match:
            metadata['author'] = author_match.group(1).strip()
        
        # Look for date
        date_match = re.search(r'(?:DATE|CREATED)\s*[:\-]?\s*(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})', content, re.IGNORECASE)
        if date_match:
            metadata['date'] = date_match.group(1)
        
        # Look for status
        status_match = re.search(r'(?:STATUS)\s*[:\-]?\s*(DRAFT|REVIEW|APPROVED|DEPRECATED)', content, re.IGNORECASE)
        if status_match:
            metadata['status'] = status_match.group(1).upper()
        
        return metadata
    
    def _extract_overview(self, content: str) -> str:
        """Extract overview/summary from PRD"""
        # Look for overview section
        overview_patterns = [
            r'(?:OVERVIEW|SUMMARY|DESCRIPTION)\s*[:\-]?\s*\n(.*?)(?=\n#{1,6}|\nREQ|\nREQUIREMENT|\Z)',
            r'^([^#\n]+(?:\n[^#\n]+)*?)(?=\n#{1,6}|\nREQ|\nREQUIREMENT)',
        ]
        
        for pattern in overview_patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        
        # Fallback: first paragraph
        lines = content.split('\n')
        overview_lines = []
        for line in lines:
            if line.strip() and not line.startswith('#') and not re.match(r'(?:REQ|REQUIREMENT)', line):
                overview_lines.append(line)
            elif overview_lines and line.strip() == '':
                break
        
        return '\n'.join(overview_lines)
    
    def _parse_sections(self, content: str) -> List[PRDSection]:
        """Parse sections from PRD"""
        sections = []
        
        # Find all headers
        header_pattern = r'^(#{1,6})\s+(.+)$'
        lines = content.split('\n')
        
        current_section = None
        section_content = []
        
        for line in lines:
            header_match = re.match(header_pattern, line)
            
            if header_match:
                # Save previous section
                if current_section:
                    sections.append(PRDSection(
                        title=current_section,
                        content='\n'.join(section_content).strip(),
                        requirements=self._extract_requirements_from_content('\n'.join(section_content)),
                        subsections=[]
                    ))
                
                # Start new section
                current_section = header_match.group(2).strip()
                section_content = []
            else:
                section_content.append(line)
        
        # Save last section
        if current_section:
            sections.append(PRDSection(
                title=current_section,
                content='\n'.join(section_content).strip(),
                requirements=self._extract_requirements_from_content('\n'.join(section_content)),
                subsections=[]
            ))
        
        return sections
    
    def _extract_all_requirements(self, content: str) -> List[Requirement]:
        """Extract all requirements from PRD"""
        return self._extract_requirements_from_content(content)
    
    def _extract_requirements_from_content(self, content: str) -> List[Requirement]:
        """Extract requirements from content"""
        requirements = []
        
        # Find requirement blocks
        req_pattern = self.patterns['requirement']
        matches = re.finditer(req_pattern, content, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            req_id = match.group(1)
            req_text = match.group(2).strip()
            
            # Parse requirement details
            requirement = self._parse_requirement(req_id, req_text)
            if requirement:
                requirements.append(requirement)
        
        return requirements
    
    def _parse_requirement(self, req_id: str, req_text: str) -> Optional[Requirement]:
        """Parse individual requirement"""
        try:
            # Extract title (first line)
            lines = req_text.split('\n')
            title = lines[0].strip()
            
            # Extract description
            description_lines = []
            for line in lines[1:]:
                if not re.match(r'(?:PRIORITY|ACCEPTANCE|DEPENDS|EFFORT|TAGS)', line, re.IGNORECASE):
                    description_lines.append(line.strip())
                else:
                    break
            
            description = '\n'.join(description_lines).strip()
            
            # Extract priority
            priority_match = re.search(self.patterns['priority'], req_text, re.IGNORECASE)
            priority = priority_match.group(1).upper() if priority_match else "MEDIUM"
            
            # Extract acceptance criteria
            ac_match = re.search(self.patterns['acceptance_criteria'], req_text, re.IGNORECASE | re.DOTALL)
            acceptance_criteria = []
            if ac_match:
                ac_text = ac_match.group(1)
                acceptance_criteria = [
                    line.strip().lstrip('-*• ') for line in ac_text.split('\n') 
                    if line.strip() and line.strip().startswith(('-', '*', '•'))
                ]
            
            # Extract dependencies
            dep_match = re.search(self.patterns['dependencies'], req_text, re.IGNORECASE | re.DOTALL)
            dependencies = []
            if dep_match:
                dep_text = dep_match.group(1)
                dependencies = [
                    line.strip().lstrip('-*• ') for line in dep_text.split('\n') 
                    if line.strip() and line.strip().startswith(('-', '*', '•'))
                ]
            
            # Extract effort
            effort_match = re.search(self.patterns['effort'], req_text, re.IGNORECASE)
            effort = effort_match.group(1) if effort_match else "TBD"
            
            # Extract tags
            tags_match = re.search(self.patterns['tags'], req_text, re.IGNORECASE | re.DOTALL)
            tags = []
            if tags_match:
                tags_text = tags_match.group(1)
                tags = [
                    line.strip().lstrip('-*• ') for line in tags_text.split('\n') 
                    if line.strip() and line.strip().startswith(('-', '*', '•'))
                ]
            
            # Determine category
            category = self._determine_category(title, description, tags)
            
            return Requirement(
                id=req_id,
                title=title,
                description=description,
                priority=priority,
                category=category,
                acceptance_criteria=acceptance_criteria,
                dependencies=dependencies,
                estimated_effort=effort,
                tags=tags
            )
            
        except Exception as e:
            self.logger.error(f"Failed to parse requirement {req_id}: {e}")
            return None
    
    def _determine_category(self, title: str, description: str, tags: List[str]) -> str:
        """Determine requirement category"""
        text = f"{title} {description} {' '.join(tags)}".lower()
        
        # Category keywords
        categories = {
            "backend": ["api", "backend", "database", "server", "service", "endpoint"],
            "frontend": ["ui", "frontend", "interface", "component", "page", "view"],
            "security": ["security", "auth", "permission", "encryption", "vulnerability"],
            "performance": ["performance", "speed", "optimization", "load", "scalability"],
            "integration": ["integration", "third-party", "external", "webhook", "sync"],
            "testing": ["test", "testing", "validation", "verification", "quality"],
            "deployment": ["deploy", "deployment", "infrastructure", "devops", "ci/cd"],
            "documentation": ["documentation", "docs", "guide", "tutorial", "help"]
        }
        
        # Score categories
        category_scores = {}
        for category, keywords in categories.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                category_scores[category] = score
        
        # Return highest scoring category
        if category_scores:
            return max(category_scores, key=category_scores.get)
        
        return "general"
    
    def extract_tasks_from_requirements(self, requirements: List[Requirement]) -> List[Dict[str, Any]]:
        """Extract actionable tasks from requirements"""
        tasks = []
        
        for req in requirements:
            # Create main task
            main_task = {
                "id": f"task_{req.id}",
                "title": req.title,
                "description": req.description,
                "priority": req.priority.lower(),
                "category": req.category,
                "estimated_effort": req.estimated_effort,
                "requirements": [req.id],
                "crew": self._determine_crew_for_category(req.category),
                "subtasks": []
            }
            
            # Create subtasks from acceptance criteria
            for i, ac in enumerate(req.acceptance_criteria, 1):
                subtask = {
                    "id": f"subtask_{req.id}_{i}",
                    "title": ac,
                    "description": f"Acceptance criteria for {req.title}",
                    "priority": req.priority.lower(),
                    "category": req.category,
                    "parent_task": f"task_{req.id}",
                    "crew": self._determine_crew_for_category(req.category)
                }
                main_task["subtasks"].append(subtask)
            
            tasks.append(main_task)
        
        return tasks
    
    def _determine_crew_for_category(self, category: str) -> str:
        """Determine which crew should handle a category"""
        crew_mapping = {
            "backend": "backend",
            "frontend": "frontend",
            "security": "security",
            "performance": "quality",
            "integration": "integration",
            "testing": "quality",
            "deployment": "deployment",
            "documentation": "quality",
            "general": "orchestrator"
        }
        
        return crew_mapping.get(category, "orchestrator")
    
    def validate_prd(self, parsed_prd: ParsedPRD) -> Dict[str, Any]:
        """Validate parsed PRD for completeness"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "completeness_score": 0
        }
        
        # Check basic structure
        if not parsed_prd.title:
            validation_result["errors"].append("PRD title is missing")
            validation_result["valid"] = False
        
        if not parsed_prd.overview:
            validation_result["warnings"].append("PRD overview is missing")
        
        if not parsed_prd.requirements:
            validation_result["errors"].append("No requirements found")
            validation_result["valid"] = False
        
        # Check requirements quality
        req_scores = []
        for req in parsed_prd.requirements:
            score = 0
            
            # Check required fields
            if req.title:
                score += 20
            if req.description:
                score += 20
            if req.acceptance_criteria:
                score += 25
            if req.priority != "MEDIUM":  # Non-default priority
                score += 15
            if req.estimated_effort != "TBD":
                score += 10
            if req.tags:
                score += 10
            
            req_scores.append(score)
            
            # Check for issues
            if not req.acceptance_criteria:
                validation_result["warnings"].append(f"Requirement {req.id} has no acceptance criteria")
            
            if len(req.description) < 20:
                validation_result["warnings"].append(f"Requirement {req.id} has a short description")
        
        # Calculate completeness score
        if req_scores:
            validation_result["completeness_score"] = sum(req_scores) / len(req_scores)
        
        return validation_result
    
    def export_to_json(self, parsed_prd: ParsedPRD) -> str:
        """Export parsed PRD to JSON string"""
        return json.dumps(asdict(parsed_prd), indent=2)
    
    def get_requirements_summary(self, parsed_prd: ParsedPRD) -> Dict[str, Any]:
        """Get summary of requirements"""
        summary = {
            "total_requirements": len(parsed_prd.requirements),
            "by_priority": {},
            "by_category": {},
            "by_crew": {},
            "estimated_effort": {},
            "completion_status": "not_started"
        }
        
        for req in parsed_prd.requirements:
            # Count by priority
            priority = req.priority
            summary["by_priority"][priority] = summary["by_priority"].get(priority, 0) + 1
            
            # Count by category
            category = req.category
            summary["by_category"][category] = summary["by_category"].get(category, 0) + 1
            
            # Count by crew
            crew = self._determine_crew_for_category(req.category)
            summary["by_crew"][crew] = summary["by_crew"].get(crew, 0) + 1
            
            # Effort estimation
            effort = req.estimated_effort
            if effort != "TBD":
                summary["estimated_effort"][effort] = summary["estimated_effort"].get(effort, 0) + 1
        
        return summary


# Tool instance for CrewAI
prd_parser = PRDParser()


# Helper functions for CrewAI tool integration
def parse_prd_content(content: str, title: str = "PRD") -> str:
    """Parse PRD content and return summary"""
    parsed = prd_parser.parse_prd(content, title)
    summary = prd_parser.get_requirements_summary(parsed)
    
    return f"PRD '{parsed.title}' parsed: {summary['total_requirements']} requirements found\n" + \
           f"By priority: {summary['by_priority']}\n" + \
           f"By category: {summary['by_category']}"


def extract_tasks_from_prd(content: str) -> str:
    """Extract actionable tasks from PRD"""
    parsed = prd_parser.parse_prd(content)
    tasks = prd_parser.extract_tasks_from_requirements(parsed.requirements)
    
    return f"Extracted {len(tasks)} tasks from PRD:\n" + \
           "\n".join([f"- {task['title']} ({task['crew']} crew)" for task in tasks[:5]])


def validate_prd_content(content: str) -> str:
    """Validate PRD content"""
    parsed = prd_parser.parse_prd(content)
    validation = prd_parser.validate_prd(parsed)
    
    status = "Valid" if validation["valid"] else "Invalid"
    return f"PRD Validation: {status}\n" + \
           f"Completeness Score: {validation['completeness_score']:.1f}/100\n" + \
           f"Errors: {len(validation['errors'])}, Warnings: {len(validation['warnings'])}"