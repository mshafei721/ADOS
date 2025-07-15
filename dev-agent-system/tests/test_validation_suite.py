"""
ADOS Complete Validation Test Suite

This comprehensive test suite validates the entire ADOS system using pytest.
It integrates all validators and provides detailed reporting on system readiness.

Usage:
    pytest tests/test_validation_suite.py -v                    # Run all tests
    pytest tests/test_validation_suite.py::test_directory -v    # Run specific test
    pytest tests/test_validation_suite.py --tb=short           # Short traceback
"""

import pytest
import json
from pathlib import Path
from typing import Dict, Any

# Import all validators
from tests.validators import ValidationOrchestrator
from tests.validators.directory_structure import DirectoryStructureValidator
from tests.validators.config_validation import ConfigValidationValidator
from tests.validators.cli_commands import CLICommandValidator
from tests.validators.knowledge_base import KnowledgeBaseValidator
from tests.validators.agent_protocol import AgentProtocolValidator


class TestADOSValidationSuite:
    """Complete ADOS system validation test suite"""
    
    @pytest.fixture(scope="class")
    def validation_orchestrator(self):
        """Create and configure validation orchestrator"""
        orchestrator = ValidationOrchestrator()
        
        # Register all validators
        orchestrator.register_validator(DirectoryStructureValidator())
        orchestrator.register_validator(ConfigValidationValidator())
        orchestrator.register_validator(CLICommandValidator())
        orchestrator.register_validator(KnowledgeBaseValidator())
        orchestrator.register_validator(AgentProtocolValidator())
        
        return orchestrator
    
    @pytest.fixture(scope="class")
    def validation_results(self, validation_orchestrator):
        """Run all validations and return results"""
        return validation_orchestrator.run_all_validations()
    
    def test_overall_system_validation(self, validation_results):
        """Test overall system validation passes"""
        assert validation_results['overall_passed'], (
            f"Overall system validation failed. "
            f"Passed validators: {validation_results['passed_validators']}/{validation_results['total_validators']}"
        )
    
    def test_directory_structure_validation(self, validation_results):
        """Test directory structure validation passes"""
        dir_result = validation_results['validation_results']['DirectoryStructureValidator']
        assert dir_result['overall_passed'], (
            f"Directory structure validation failed. "
            f"Success rate: {dir_result['success_rate']}"
        )
    
    def test_configuration_validation(self, validation_results):
        """Test configuration validation passes"""
        config_result = validation_results['validation_results']['ConfigValidationValidator']
        assert config_result['overall_passed'], (
            f"Configuration validation failed. "
            f"Success rate: {config_result['success_rate']}"
        )
    
    def test_cli_commands_validation(self, validation_results):
        """Test CLI commands validation passes"""
        cli_result = validation_results['validation_results']['CLICommandValidator']
        assert cli_result['overall_passed'], (
            f"CLI commands validation failed. "
            f"Success rate: {cli_result['success_rate']}"
        )
    
    def test_knowledge_base_validation(self, validation_results):
        """Test knowledge base validation passes"""
        kb_result = validation_results['validation_results']['KnowledgeBaseValidator']
        assert kb_result['overall_passed'], (
            f"Knowledge base validation failed. "
            f"Success rate: {kb_result['success_rate']}"
        )
    
    def test_agent_protocol_validation(self, validation_results):
        """Test agent protocol validation passes"""
        protocol_result = validation_results['validation_results']['AgentProtocolValidator']
        assert protocol_result['overall_passed'], (
            f"Agent protocol validation failed. "
            f"Success rate: {protocol_result['success_rate']}"
        )
    
    def test_minimum_validator_success_rate(self, validation_results):
        """Test each validator has minimum 80% success rate"""
        minimum_success_rate = 0.8
        
        for validator_name, result in validation_results['validation_results'].items():
            if result['total_checks'] > 0:
                success_rate = result['passed_checks'] / result['total_checks']
                assert success_rate >= minimum_success_rate, (
                    f"Validator '{validator_name}' success rate {success_rate:.2%} "
                    f"below minimum {minimum_success_rate:.2%}"
                )
    
    def test_critical_system_components(self, validation_results):
        """Test critical system components are present"""
        critical_components = [
            'DirectoryStructureValidator',
            'ConfigValidationValidator',
            'CLICommandValidator',
            'KnowledgeBaseValidator',
            'AgentProtocolValidator'
        ]
        
        validation_results_keys = set(validation_results['validation_results'].keys())
        
        for component in critical_components:
            assert component in validation_results_keys, (
                f"Critical component '{component}' missing from validation results"
            )
    
    def test_crews_configuration(self, validation_results):
        """Test all expected crews are properly configured"""
        expected_crews = [
            'orchestrator', 'frontend', 'backend', 'security', 
            'quality', 'integration', 'deployment'
        ]
        
        config_result = validation_results['validation_results']['ConfigValidationValidator']
        
        # Check if crew validation results exist
        crew_results = [
            result for result in config_result['results'] 
            if result['name'].startswith('crew_') and result['name'].endswith('_config')
        ]
        
        assert len(crew_results) == len(expected_crews), (
            f"Expected {len(expected_crews)} crews, found {len(crew_results)} in validation"
        )
    
    def test_agents_configuration(self, validation_results):
        """Test all expected agents are properly configured"""
        expected_agents = {
            'orchestrator': 2,  # TaskDecomposer, WorkflowManager
            'frontend': 2,      # UIDevAgent, StyleAgent
            'backend': 2,       # APIAgent, DatabaseAgent
            'security': 2,      # AuthAgent, VulnAgent
            'quality': 3,       # UnitTester, Linter, CodeReviewer
            'integration': 2,   # CIAgent, APIIntegrator
            'deployment': 2     # DockerAgent, CloudAgent
        }
        
        total_expected_agents = sum(expected_agents.values())
        
        config_result = validation_results['validation_results']['ConfigValidationValidator']
        
        # Check if agent validation results exist
        agent_results = [
            result for result in config_result['results'] 
            if result['name'].startswith('agent_') and result['name'].endswith('_config')
        ]
        
        assert len(agent_results) == total_expected_agents, (
            f"Expected {total_expected_agents} agents, found {len(agent_results)} in validation"
        )
    
    def test_knowledge_base_completeness(self, validation_results):
        """Test knowledge base has all expected files"""
        expected_kb_files = 14  # Total from all crews
        
        kb_result = validation_results['validation_results']['KnowledgeBaseValidator']
        
        # Count KB file results
        kb_file_results = [
            result for result in kb_result['results'] 
            if result['name'].startswith('kb_file_') and result['passed']
        ]
        
        assert len(kb_file_results) == expected_kb_files, (
            f"Expected {expected_kb_files} KB files, found {len(kb_file_results)} passing validation"
        )
    
    def test_phase_1_completion_criteria(self, validation_results):
        """Test Phase 1 completion criteria are met"""
        # All validators must pass
        assert validation_results['overall_passed'], "Not all validators passed"
        
        # Minimum success rate across all validators
        total_checks = sum(
            result['total_checks'] 
            for result in validation_results['validation_results'].values()
        )
        
        total_passed = sum(
            result['passed_checks'] 
            for result in validation_results['validation_results'].values()
        )
        
        overall_success_rate = total_passed / total_checks if total_checks > 0 else 0
        
        assert overall_success_rate >= 0.9, (
            f"Overall success rate {overall_success_rate:.2%} below required 90%"
        )
        
        # Critical components must be 100% functional
        critical_validators = ['DirectoryStructureValidator', 'ConfigValidationValidator']
        
        for validator_name in critical_validators:
            result = validation_results['validation_results'][validator_name]
            success_rate = result['passed_checks'] / result['total_checks'] if result['total_checks'] > 0 else 0
            
            assert success_rate >= 0.95, (
                f"Critical validator '{validator_name}' success rate {success_rate:.2%} below required 95%"
            )
    
    def test_system_readiness_for_phase_2(self, validation_results):
        """Test system is ready for Phase 2: System Backbone"""
        # All Phase 1 requirements must be met
        phase_1_requirements = [
            validation_results['overall_passed'],
            validation_results['passed_validators'] == validation_results['total_validators'],
            validation_results['passed_validators'] >= 5  # All 5 validators
        ]
        
        assert all(phase_1_requirements), (
            "System not ready for Phase 2. Phase 1 requirements not met."
        )
        
        # Specific readiness criteria
        config_result = validation_results['validation_results']['ConfigValidationValidator']
        dir_result = validation_results['validation_results']['DirectoryStructureValidator']
        
        # Configuration system must be fully functional
        assert config_result['overall_passed'], "Configuration system not ready"
        
        # Directory structure must be complete
        assert dir_result['overall_passed'], "Directory structure not ready"
        
        # All crews must be configured
        crew_count = sum(
            1 for result in config_result['results'] 
            if result['name'].startswith('crew_') and result['name'].endswith('_config') and result['passed']
        )
        
        assert crew_count == 7, f"Expected 7 crews configured, found {crew_count}"


class TestValidationReporting:
    """Test validation reporting and output functionality"""
    
    def test_validation_orchestrator_creation(self):
        """Test validation orchestrator can be created"""
        orchestrator = ValidationOrchestrator()
        assert orchestrator is not None
        assert isinstance(orchestrator.validators, list)
        assert len(orchestrator.validators) == 0  # No validators registered yet
    
    def test_validator_registration(self):
        """Test validators can be registered"""
        orchestrator = ValidationOrchestrator()
        validator = DirectoryStructureValidator()
        
        orchestrator.register_validator(validator)
        assert len(orchestrator.validators) == 1
        assert orchestrator.validators[0] == validator
    
    def test_validation_result_structure(self):
        """Test validation result has correct structure"""
        orchestrator = ValidationOrchestrator()
        orchestrator.register_validator(DirectoryStructureValidator())
        
        results = orchestrator.run_all_validations()
        
        # Check top-level structure
        required_keys = ['overall_passed', 'total_validators', 'passed_validators', 'validation_results', 'summary']
        assert all(key in results for key in required_keys)
        
        # Check individual validator results
        for validator_name, result in results['validation_results'].items():
            validator_required_keys = ['validator', 'overall_passed', 'passed_checks', 'total_checks', 'success_rate', 'results']
            assert all(key in result for key in validator_required_keys)
    
    def test_validation_summary_generation(self):
        """Test validation summary is generated correctly"""
        orchestrator = ValidationOrchestrator()
        orchestrator.register_validator(DirectoryStructureValidator())
        
        results = orchestrator.run_all_validations()
        
        assert 'summary' in results
        assert isinstance(results['summary'], str)
        assert 'ADOS System Validation Summary' in results['summary']
        assert 'Overall Status:' in results['summary']


if __name__ == '__main__':
    # Run tests if executed directly
    pytest.main([__file__, '-v'])