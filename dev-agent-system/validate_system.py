#!/usr/bin/env python3
"""
ADOS System Validation Orchestrator

This script provides comprehensive validation of the ADOS (AI Dev Orchestration System)
to ensure all Phase 1 components are properly implemented and the system is ready
for Phase 2: System Backbone.

Usage:
    python validate_system.py              # Run all validations
    python validate_system.py --help       # Show help
    python validate_system.py --validator directory  # Run specific validator
    python validate_system.py --report     # Generate detailed report
    python validate_system.py --summary    # Show summary only

Exit Codes:
    0: All validations passed
    1: One or more validations failed
    2: Critical error during validation
"""

import sys
import argparse
from pathlib import Path
from typing import Dict, Any
import json

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from tests.validators import ValidationOrchestrator


def main():
    """Main entry point for system validation"""
    parser = argparse.ArgumentParser(
        description="ADOS System Validation Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--validator', 
        choices=['directory', 'config', 'cli', 'knowledge', 'agent'],
        help='Run specific validator only'
    )
    
    parser.add_argument(
        '--report', 
        action='store_true',
        help='Generate detailed validation report'
    )
    
    parser.add_argument(
        '--summary', 
        action='store_true',
        help='Show summary only'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results in JSON format'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    try:
        # Create orchestrator
        orchestrator = ValidationOrchestrator()
        
        # Import and register validators
        validator_modules = _import_validators()
        
        # Register validators based on selection
        if args.validator:
            _register_specific_validator(orchestrator, validator_modules, args.validator)
        else:
            _register_all_validators(orchestrator, validator_modules)
        
        # Run validations
        if args.verbose:
            print("Starting ADOS System Validation...")
            print("=" * 50)
        
        results = orchestrator.run_all_validations()
        
        # Output results
        if args.json:
            print(json.dumps(results, indent=2))
        elif args.summary:
            print(results['summary'])
        else:
            _print_detailed_report(results, args.report or args.verbose)
        
        # Exit with appropriate code
        if results['overall_passed']:
            if args.verbose:
                print("\\n✅ All validations passed! ADOS system is ready for Phase 2.")
            sys.exit(0)
        else:
            if args.verbose:
                print("\\n❌ Some validations failed. Please review the results above.")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Critical error during validation: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(2)


def _import_validators():
    """Import all validator modules"""
    validators = {}
    
    try:
        from tests.validators.directory_structure import DirectoryStructureValidator
        validators['directory'] = DirectoryStructureValidator
    except ImportError:
        if __name__ == '__main__':
            print("⚠️  DirectoryStructureValidator not available")
    
    try:
        from tests.validators.config_validation import ConfigValidationValidator
        validators['config'] = ConfigValidationValidator
    except ImportError:
        if __name__ == '__main__':
            print("⚠️  ConfigValidationValidator not available")
    
    try:
        from tests.validators.cli_commands import CLICommandValidator
        validators['cli'] = CLICommandValidator
    except ImportError:
        if __name__ == '__main__':
            print("⚠️  CLICommandValidator not available")
    
    try:
        from tests.validators.knowledge_base import KnowledgeBaseValidator
        validators['knowledge'] = KnowledgeBaseValidator
    except ImportError:
        if __name__ == '__main__':
            print("⚠️  KnowledgeBaseValidator not available")
    
    try:
        from tests.validators.agent_protocol import AgentProtocolValidator
        validators['agent'] = AgentProtocolValidator
    except ImportError:
        if __name__ == '__main__':
            print("⚠️  AgentProtocolValidator not available")
    
    return validators


def _register_specific_validator(orchestrator: ValidationOrchestrator, validators: Dict, validator_name: str):
    """Register a specific validator"""
    if validator_name in validators:
        validator_class = validators[validator_name]
        orchestrator.register_validator(validator_class())
    else:
        raise ValueError(f"Validator '{validator_name}' not available")


def _register_all_validators(orchestrator: ValidationOrchestrator, validators: Dict):
    """Register all available validators"""
    for validator_class in validators.values():
        orchestrator.register_validator(validator_class())


def _print_detailed_report(results: Dict[str, Any], show_details: bool = False):
    """Print detailed validation report"""
    print("ADOS System Validation Results")
    print("=" * 50)
    
    overall_status = "✅ PASS" if results['overall_passed'] else "❌ FAIL"
    print(f"Overall Status: {overall_status}")
    print(f"Validators: {results['passed_validators']}/{results['total_validators']} passed")
    print()
    
    # Print individual validator results
    for validator_name, result in results['validation_results'].items():
        status = "✅ PASS" if result.get('overall_passed', False) else "❌ FAIL"
        success_rate = result.get('success_rate', '0/0')
        
        print(f"{validator_name}: {status} ({success_rate})")
        
        if show_details and 'results' in result:
            for check in result['results']:
                check_status = "  ✅" if check['passed'] else "  ❌"
                print(f"{check_status} {check['name']}")
                if check['message']:
                    print(f"     {check['message']}")
        
        if 'error' in result:
            print(f"  ❌ Error: {result['error']}")
        
        print()


if __name__ == '__main__':
    main()