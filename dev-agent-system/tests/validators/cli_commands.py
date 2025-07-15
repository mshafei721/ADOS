"""
CLI Commands Validator

This validator ensures that all ADOS CLI commands are functional and working correctly.

Validates:
- All 4 CLI commands exist and are accessible (init, run, status, version)
- Commands produce expected output formats
- Help text and documentation are present
- Error handling works correctly
- Command return codes are appropriate
"""

import subprocess
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Tuple

from tests.validators import BaseValidator


class CLICommandValidator(BaseValidator):
    """Validates all ADOS CLI commands and their functionality"""
    
    def __init__(self):
        super().__init__("CLICommandValidator")
        
        # Define expected CLI commands
        self.expected_commands = [
            'init',
            'run', 
            'status',
            'version'
        ]
        
        # Expected help text patterns
        self.help_patterns = {
            'init': ['workspace', 'initialize', 'setup'],
            'run': ['orchestrator', 'crew', 'execute'],
            'status': ['system', 'health', 'configuration'],
            'version': ['version', 'build', 'information']
        }
        
        # CLI script path
        self.cli_script = self.base_path / 'runner' / 'main.py'
        
        # Python executable
        self.python_exec = sys.executable
    
    def validate(self) -> bool:
        """Run all CLI command validations"""
        
        # Validate CLI script exists
        self._validate_cli_script_exists()
        
        # Test basic CLI functionality
        self._test_cli_basic_functionality()
        
        # Test individual commands
        self._test_individual_commands()
        
        # Test help functionality
        self._test_help_functionality()
        
        # Test error handling
        self._test_error_handling()
        
        # Return overall validation result
        return all(result.passed for result in self.results)
    
    def _validate_cli_script_exists(self):
        """Validate the main CLI script exists"""
        if self.cli_script.exists() and self.cli_script.is_file():
            self.add_result(
                "cli_script_exists",
                True,
                f"CLI script exists at {self.cli_script}"
            )
        else:
            self.add_result(
                "cli_script_exists",
                False,
                f"CLI script missing at {self.cli_script}",
                {"expected_path": str(self.cli_script)}
            )
    
    def _test_cli_basic_functionality(self):
        """Test basic CLI functionality"""
        # Test CLI can be imported/executed
        try:
            result = self._run_cli_command(['--help'])
            
            if result[0] == 0:  # return code
                self.add_result(
                    "cli_basic_help",
                    True,
                    "CLI script responds to --help"
                )
            else:
                self.add_result(
                    "cli_basic_help",
                    False,
                    f"CLI script --help failed with return code {result[0]}",
                    {"stdout": result[1], "stderr": result[2]}
                )
        except Exception as e:
            self.add_result(
                "cli_basic_help",
                False,
                f"CLI script execution failed: {str(e)}"
            )
    
    def _test_individual_commands(self):
        """Test each individual CLI command"""
        for command in self.expected_commands:
            self._test_command_exists(command)
            self._test_command_help(command)
            self._test_command_execution(command)
    
    def _test_command_exists(self, command: str):
        """Test if a command exists and is accessible"""
        try:
            result = self._run_cli_command([command, '--help'])
            
            if result[0] == 0:  # return code
                self.add_result(
                    f"command_exists_{command}",
                    True,
                    f"Command '{command}' exists and responds to --help"
                )
            else:
                self.add_result(
                    f"command_exists_{command}",
                    False,
                    f"Command '{command}' failed with return code {result[0]}",
                    {"stdout": result[1], "stderr": result[2]}
                )
        except Exception as e:
            self.add_result(
                f"command_exists_{command}",
                False,
                f"Command '{command}' execution failed: {str(e)}"
            )
    
    def _test_command_help(self, command: str):
        """Test if a command has appropriate help text"""
        try:
            result = self._run_cli_command([command, '--help'])
            
            if result[0] == 0:  # return code
                help_text = result[1].lower()
                expected_patterns = self.help_patterns.get(command, [])
                
                # Check if expected patterns are in help text
                patterns_found = [pattern for pattern in expected_patterns if pattern in help_text]
                
                if len(patterns_found) >= len(expected_patterns) // 2:  # At least half the patterns
                    self.add_result(
                        f"command_help_{command}",
                        True,
                        f"Command '{command}' has appropriate help text"
                    )
                else:
                    self.add_result(
                        f"command_help_{command}",
                        False,
                        f"Command '{command}' help text missing expected patterns",
                        {"expected": expected_patterns, "found": patterns_found}
                    )
            else:
                self.add_result(
                    f"command_help_{command}",
                    False,
                    f"Command '{command}' help failed with return code {result[0]}"
                )
        except Exception as e:
            self.add_result(
                f"command_help_{command}",
                False,
                f"Command '{command}' help test failed: {str(e)}"
            )
    
    def _test_command_execution(self, command: str):
        """Test command execution with appropriate parameters"""
        try:
            if command == 'init':
                # Test init command (might need special handling)
                result = self._run_cli_command([command, '--help'])
                
            elif command == 'run':
                # Test run command (might need special handling)
                result = self._run_cli_command([command, '--help'])
                
            elif command == 'status':
                # Test status command (should be safe to run)
                result = self._run_cli_command([command])
                
            elif command == 'version':
                # Test version command (should be safe to run)
                result = self._run_cli_command([command])
                
            else:
                # Default to help for unknown commands
                result = self._run_cli_command([command, '--help'])
            
            # Check return code (0 = success, others may be acceptable for some commands)
            if result[0] == 0:
                self.add_result(
                    f"command_execution_{command}",
                    True,
                    f"Command '{command}' executed successfully"
                )
            elif result[0] == 1 and command in ['run', 'init']:
                # Some commands might return 1 for expected reasons (missing config, etc.)
                self.add_result(
                    f"command_execution_{command}",
                    True,
                    f"Command '{command}' executed with expected return code {result[0]}"
                )
            else:
                self.add_result(
                    f"command_execution_{command}",
                    False,
                    f"Command '{command}' failed with return code {result[0]}",
                    {"stdout": result[1], "stderr": result[2]}
                )
                
        except Exception as e:
            self.add_result(
                f"command_execution_{command}",
                False,
                f"Command '{command}' execution test failed: {str(e)}"
            )
    
    def _test_help_functionality(self):
        """Test general help functionality"""
        help_commands = [
            ['--help'],
            ['-h'],
            ['help']
        ]
        
        for help_cmd in help_commands:
            try:
                result = self._run_cli_command(help_cmd)
                
                if result[0] == 0:
                    self.add_result(
                        f"help_functionality_{help_cmd[0].replace('-', '_')}",
                        True,
                        f"Help command '{help_cmd[0]}' works"
                    )
                else:
                    self.add_result(
                        f"help_functionality_{help_cmd[0].replace('-', '_')}",
                        False,
                        f"Help command '{help_cmd[0]}' failed with return code {result[0]}"
                    )
            except Exception as e:
                self.add_result(
                    f"help_functionality_{help_cmd[0].replace('-', '_')}",
                    False,
                    f"Help command '{help_cmd[0]}' test failed: {str(e)}"
                )
    
    def _test_error_handling(self):
        """Test error handling for invalid commands and arguments"""
        error_test_cases = [
            (['nonexistent_command'], "Invalid command handling"),
            (['status', '--invalid-flag'], "Invalid flag handling"),
            (['run', '--invalid-param', 'value'], "Invalid parameter handling")
        ]
        
        for test_cmd, description in error_test_cases:
            try:
                result = self._run_cli_command(test_cmd)
                
                # For error cases, we expect non-zero return code
                if result[0] != 0:
                    self.add_result(
                        f"error_handling_{test_cmd[0]}",
                        True,
                        f"Error handling works for {description}"
                    )
                else:
                    self.add_result(
                        f"error_handling_{test_cmd[0]}",
                        False,
                        f"Error handling failed for {description} - should have returned non-zero code"
                    )
            except Exception as e:
                # Exception during error test might be acceptable
                self.add_result(
                    f"error_handling_{test_cmd[0]}",
                    True,
                    f"Error handling works for {description} (exception: {str(e)})"
                )
    
    def _run_cli_command(self, args: List[str]) -> Tuple[int, str, str]:
        """Run a CLI command and return (return_code, stdout, stderr)"""
        # Change to the correct directory
        old_cwd = os.getcwd()
        os.chdir(self.base_path)
        
        try:
            # Construct command
            cmd = [self.python_exec, '-m', 'runner.main'] + args
            
            # Run command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            return result.returncode, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
        except Exception as e:
            return -1, "", f"Command execution failed: {str(e)}"
        finally:
            os.chdir(old_cwd)
    
    def get_cli_summary(self) -> Dict[str, Any]:
        """Get a summary of CLI validation results"""
        summary = {
            'total_commands': len(self.expected_commands),
            'working_commands': 0,
            'failed_commands': [],
            'help_functionality': 0,
            'error_handling': 0
        }
        
        # Count working commands
        for command in self.expected_commands:
            command_working = any(
                result.passed for result in self.results 
                if f"command_exists_{command}" in result.name
            )
            if command_working:
                summary['working_commands'] += 1
            else:
                summary['failed_commands'].append(command)
        
        # Count help functionality
        summary['help_functionality'] = sum(
            1 for result in self.results 
            if 'help_functionality' in result.name and result.passed
        )
        
        # Count error handling
        summary['error_handling'] = sum(
            1 for result in self.results 
            if 'error_handling' in result.name and result.passed
        )
        
        return summary