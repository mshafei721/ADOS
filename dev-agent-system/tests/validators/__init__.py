"""
ADOS System Validators

This module contains validation components for the ADOS (AI Dev Orchestration System).
Each validator ensures specific aspects of the system are properly configured and functional.

Validators:
- DirectoryStructureValidator: Validates directory structure and organization
- ConfigValidationValidator: Validates configuration loading and integrity
- CLICommandValidator: Validates CLI commands and functionality
- KnowledgeBaseValidator: Validates knowledge base files and structure
- AgentProtocolValidator: Validates agent communication protocols

Usage:
    from tests.validators import BaseValidator, ValidationOrchestrator
    
    orchestrator = ValidationOrchestrator()
    results = orchestrator.run_all_validations()
"""

import abc
from typing import Dict, List, Any, Optional
from pathlib import Path
import sys
import os

# Add dev-agent-system to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class ValidationResult:
    """Result of a validation check"""
    
    def __init__(self, name: str, passed: bool, message: str = "", details: Optional[Dict[str, Any]] = None):
        self.name = name
        self.passed = passed
        self.message = message
        self.details = details or {}
    
    def __repr__(self):
        status = "PASS" if self.passed else "FAIL"
        return f"ValidationResult({self.name}: {status})"


class BaseValidator(abc.ABC):
    """Base class for all system validators"""
    
    def __init__(self, name: str):
        self.name = name
        self.results: List[ValidationResult] = []
        self.base_path = Path(__file__).parent.parent.parent  # dev-agent-system/
    
    @abc.abstractmethod
    def validate(self) -> bool:
        """Run validation checks and return overall pass/fail status"""
        pass
    
    def add_result(self, name: str, passed: bool, message: str = "", details: Optional[Dict[str, Any]] = None):
        """Add a validation result"""
        result = ValidationResult(name, passed, message, details)
        self.results.append(result)
        return result
    
    def get_report(self) -> Dict[str, Any]:
        """Generate validation report"""
        passed_count = sum(1 for r in self.results if r.passed)
        total_count = len(self.results)
        
        return {
            'validator': self.name,
            'overall_passed': self.validate(),
            'passed_checks': passed_count,
            'total_checks': total_count,
            'success_rate': f"{passed_count}/{total_count}" if total_count > 0 else "0/0",
            'results': [
                {
                    'name': r.name,
                    'passed': r.passed,
                    'message': r.message,
                    'details': r.details
                }
                for r in self.results
            ]
        }
    
    def reset(self):
        """Reset validation results"""
        self.results.clear()


class ValidationOrchestrator:
    """Central orchestrator for all system validations"""
    
    def __init__(self):
        self.validators: List[BaseValidator] = []
        self.execution_order = [
            'DirectoryStructureValidator',
            'ConfigValidationValidator', 
            'KnowledgeBaseValidator',
            'CLICommandValidator',
            'AgentProtocolValidator'
        ]
    
    def register_validator(self, validator: BaseValidator):
        """Register a validator with the orchestrator"""
        self.validators.append(validator)
    
    def run_all_validations(self) -> Dict[str, Any]:
        """Run all registered validators in dependency order"""
        results = {}
        overall_passed = True
        
        # Sort validators by execution order
        ordered_validators = []
        for validator_name in self.execution_order:
            for validator in self.validators:
                if validator.__class__.__name__ == validator_name:
                    ordered_validators.append(validator)
                    break
        
        # Add any remaining validators not in execution order
        for validator in self.validators:
            if validator not in ordered_validators:
                ordered_validators.append(validator)
        
        # Execute validators
        for validator in ordered_validators:
            try:
                validator.reset()
                validator_passed = validator.validate()
                results[validator.name] = validator.get_report()
                
                if not validator_passed:
                    overall_passed = False
                    
            except Exception as e:
                results[validator.name] = {
                    'validator': validator.name,
                    'overall_passed': False,
                    'error': str(e),
                    'passed_checks': 0,
                    'total_checks': 0,
                    'success_rate': '0/0',
                    'results': []
                }
                overall_passed = False
        
        return {
            'overall_passed': overall_passed,
            'total_validators': len(ordered_validators),
            'passed_validators': sum(1 for r in results.values() if r.get('overall_passed', False)),
            'validation_results': results,
            'summary': self._generate_summary(results)
        }
    
    def _generate_summary(self, results: Dict[str, Any]) -> str:
        """Generate a summary of validation results"""
        passed_validators = sum(1 for r in results.values() if r.get('overall_passed', False))
        total_validators = len(results)
        
        summary = f"ADOS System Validation Summary\n"
        summary += f"==============================\n"
        summary += f"Overall Status: {'PASS' if passed_validators == total_validators else 'FAIL'}\n"
        summary += f"Validators: {passed_validators}/{total_validators} passed\n\n"
        
        for validator_name, result in results.items():
            status = "PASS" if result.get('overall_passed', False) else "FAIL"
            success_rate = result.get('success_rate', '0/0')
            summary += f"  {validator_name}: {status} ({success_rate})\n"
        
        return summary