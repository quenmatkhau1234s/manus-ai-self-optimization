"""
Unit tests for the Error Recovery System module.

This module contains tests to verify the functionality of the ErrorRecoverySystem class
which implements predictive error detection and automated recovery for Manus AI.
"""

import unittest
import sys
import os

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from refactoring.error_recovery import ErrorRecoverySystem

class TestErrorRecoverySystem(unittest.TestCase):
    """Test cases for the ErrorRecoverySystem class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.recovery_system = ErrorRecoverySystem()
        
        # Register some error patterns
        self.recovery_system.register_error_pattern(
            "file_not_found",
            "No such file or directory",
            severity=3,
            recovery_strategy="create_file"
        )
        
        self.recovery_system.register_error_pattern(
            "permission_denied",
            "Permission denied",
            severity=4,
            recovery_strategy="elevate_permissions"
        )
        
        self.recovery_system.register_error_pattern(
            "network_timeout",
            "Connection timed out",
            severity=3,
            recovery_strategy="retry_with_backoff"
        )
        
        # Register some recovery strategies
        def create_file_strategy(error, context):
            file_path = context.get('file_path', '/tmp/default.txt')
            return {
                'success': True,
                'error': error,
                'actions': [f"Created file {file_path}"],
                'message': "File created successfully"
            }
            
        def elevate_permissions_strategy(error, context):
            file_path = context.get('file_path', '/tmp/default.txt')
            return {
                'success': True,
                'error': error,
                'actions': [f"Changed permissions for {file_path}"],
                'message': "Permissions updated successfully"
            }
            
        def retry_with_backoff_strategy(error, context):
            return {
                'success': True,
                'error': error,
                'actions': ["Retried with exponential backoff"],
                'message': "Connection established after retry"
            }
            
        self.recovery_system.register_recovery_strategy(
            "create_file",
            create_file_strategy,
            ["file_not_found"]
        )
        
        self.recovery_system.register_recovery_strategy(
            "elevate_permissions",
            elevate_permissions_strategy,
            ["permission_denied"]
        )
        
        self.recovery_system.register_recovery_strategy(
            "retry_with_backoff",
            retry_with_backoff_strategy,
            ["network_timeout", "connection_refused"]
        )
        
    def test_initialization(self):
        """Test that the error recovery system initializes correctly."""
        self.assertEqual(len(self.recovery_system.error_patterns), 3)
        self.assertEqual(len(self.recovery_system.recovery_strategies), 3)
        self.assertEqual(len(self.recovery_system.error_history), 0)
        self.assertEqual(len(self.recovery_system.active_recoveries), 0)
        
    def test_register_error_pattern(self):
        """Test registering an error pattern."""
        # Register a new error pattern
        self.recovery_system.register_error_pattern(
            "out_of_memory",
            "Out of memory",
            severity=5,
            recovery_strategy="free_memory"
        )
        
        # Verify pattern was registered
        self.assertIn("out_of_memory", self.recovery_system.error_patterns)
        self.assertEqual(self.recovery_system.error_patterns["out_of_memory"]["severity"], 5)
        self.assertEqual(self.recovery_system.error_patterns["out_of_memory"]["recovery_strategy"], "free_memory")
        
    def test_register_recovery_strategy(self):
        """Test registering a recovery strategy."""
        # Define a new strategy function
        def free_memory_strategy(error, context):
            return {
                'success': True,
                'error': error,
                'actions': ["Cleared cache", "Terminated unused processes"],
                'message': "Memory freed successfully"
            }
            
        # Register the strategy
        self.recovery_system.register_recovery_strategy(
            "free_memory",
            free_memory_strategy,
            ["out_of_memory"]
        )
        
        # Verify strategy was registered
        self.assertIn("free_memory", self.recovery_system.recovery_strategies)
        self.assertEqual(self.recovery_system.recovery_strategies["free_memory"]["attempts"], 0)
        self.assertEqual(self.recovery_system.recovery_strategies["free_memory"]["successes"], 0)
        self.assertEqual(self.recovery_system.recovery_strategies["free_memory"]["applicable_errors"], ["out_of_memory"])
        
    def test_detect_error(self):
        """Test detecting errors in operation results."""
        # Create an operation result with an error
        operation_result = "Error: No such file or directory: /home/user/missing_file.txt"
        
        # Create operation context
        operation_context = {
            "operation": "read_file",
            "file_path": "/home/user/missing_file.txt"
        }
        
        # Detect error
        error = self.recovery_system.detect_error(operation_result, operation_context)
        
        # Verify error was detected
        self.assertIsNotNone(error)
        self.assertEqual(error["type"], "file_not_found")
        self.assertEqual(error["severity"], 3)
        self.assertEqual(error["recovery_strategy"], "create_file")
        self.assertEqual(error["context"], operation_context)
        
        # Verify error was added to history
        self.assertEqual(len(self.recovery_system.error_history), 1)
        
        # Verify occurrence count was updated
        self.assertEqual(self.recovery_system.error_patterns["file_not_found"]["occurrences"], 1)
        
    def test_detect_error_no_match(self):
        """Test that no error is detected when there's no match."""
        # Create an operation result without a known error
        operation_result = "Operation completed successfully"
        
        # Create operation context
        operation_context = {
            "operation": "read_file",
            "file_path": "/home/user/existing_file.txt"
        }
        
        # Detect error
        error = self.recovery_system.detect_error(operation_result, operation_context)
        
        # Verify no error was detected
        self.assertIsNone(error)
        
        # Verify history wasn't updated
        self.assertEqual(len(self.recovery_system.error_history), 0)
        
    def test_predict_potential_errors(self):
        """Test predicting potential errors before operation execution."""
        # Add some errors to history
        file_operation_context = {
            "operation": "read_file",
            "file_path": "/home/user/restricted_file.txt"
        }
        
        # Simulate multiple permission denied errors for file operations
        for _ in range(3):
            self.recovery_system.detect_error(
                "Error: Permission denied: /home/user/restricted_file.txt",
                file_operation_context
            )
            
        # Predict errors for a similar operation
        planned_operation = "read_file"
        operation_context = {
            "operation": "read_file",
            "file_path": "/home/user/another_restricted_file.txt"
        }
        
        potential_errors = self.recovery_system.predict_potential_errors(planned_operation, operation_context)
        
        # Verify potential errors were predicted
        self.assertGreaterEqual(len(potential_errors), 1)
        
        # Check if permission_denied is in the predictions
        permission_error_predicted = False
        for error in potential_errors:
            if error["type"] == "permission_denied":
                permission_error_predicted = True
                self.assertGreater(error["probability"], 0.2)
                break
                
        self.assertTrue(permission_error_predicted, "Permission denied error should be predicted")
        
    def test_attempt_recovery(self):
        """Test attempting to recover from an error."""
        # Create an error
        error = {
            "type": "file_not_found",
            "severity": 3,
            "context": {
                "operation": "read_file",
                "file_path": "/home/user/missing_file.txt"
            },
            "result": "Error: No such file or directory",
            "timestamp": self.recovery_system._get_timestamp(),
            "recovery_strategy": "create_file"
        }
        
        # Attempt recovery
        recovery_result = self.recovery_system.attempt_recovery(error, error["context"])
        
        # Verify recovery was successful
        self.assertTrue(recovery_result["success"])
        self.assertIn("actions", recovery_result)
        self.assertIn("Created file", recovery_result["actions"][0])
        
        # Verify recovery statistics were updated
        self.assertEqual(self.recovery_system.recovery_strategies["create_file"]["attempts"], 1)
        self.assertEqual(self.recovery_system.recovery_strategies["create_file"]["successes"], 1)
        self.assertEqual(self.recovery_system.error_patterns["file_not_found"]["successful_recoveries"], 1)
        
    def test_attempt_recovery_no_strategy(self):
        """Test attempting recovery with no suitable strategy."""
        # Create an error with no strategy
        error = {
            "type": "unknown_error",
            "severity": 2,
            "context": {
                "operation": "unknown_operation"
            },
            "result": "Unknown error occurred",
            "timestamp": self.recovery_system._get_timestamp(),
            "recovery_strategy": None
        }
        
        # Attempt recovery
        recovery_result = self.recovery_system.attempt_recovery(error, error["context"])
        
        # Verify recovery failed
        self.assertFalse(recovery_result["success"])
        self.assertEqual(recovery_result["message"], "No suitable recovery strategy found")
        
    def test_get_error_statistics(self):
        """Test retrieving error statistics."""
        # Create some errors and recoveries
        file_not_found_context = {
            "operation": "read_file",
            "file_path": "/home/user/missing_file.txt"
        }
        
        permission_denied_context = {
            "operation": "write_file",
            "file_path": "/home/user/restricted_file.txt"
        }
        
        # Detect and recover from file_not_found errors
        for _ in range(3):
            error = self.recovery_system.detect_error(
                "Error: No such file or directory",
                file_not_found_context
            )
            self.recovery_system.attempt_recovery(error, file_not_found_context)
            
        # Detect and recover from permission_denied errors (one will fail)
        for i in range(2):
            error = self.recovery_system.detect_error(
                "Error: Permission denied",
                permission_denied_context
            )
            # Make one recovery fail
            if i == 1:
                # Override the strategy to make it fail
                original_function = self.recovery_system.recovery_strategies["elevate_permissions"]["function"]
                
                def failing_strategy(error, context):
                    return {
                        'success': False,
                        'error': error,
                        'actions': [],
                        'message': "Failed to elevate permissions"
                    }
                    
                self.recovery_system.recovery_strategies["elevate_permissions"]["function"] = failing_strategy
                
            self.recovery_system.attempt_recovery(error, permission_denied_context)
            
            # Restore original function
            if i == 1:
                self.recovery_system.recovery_strategies["elevate_permissions"]["function"] = original_function
            
        # Get statistics
        stats = self.recovery_system.get_error_statistics()
        
        # Verify statistics
        self.assertIn("errors", stats)
        self.assertIn("recovery_strategies", stats)
        self.assertEqual(stats["total_errors"], 5)  # 3 file_not_found + 2 permission_denied
        self.assertEqual(stats["total_recoveries"], 4)  # All except one permission_denied
        
        # Verify error-specific statistics
        self.assertEqual(stats["errors"]["file_not_found"]["occurrences"], 3)
        self.assertEqual(stats["errors"]["file_not_found"]["successful_recoveries"], 3)
        self.assertEqual(stats["errors"]["permission_denied"]["occurrences"], 2)
        self.assertEqual(stats["errors"]["permission_denied"]["successful_recoveries"], 1)
        
        # Verify strategy-specific statistics
        self.assertEqual(stats["recovery_strategies"]["create_file"]["attempts"], 3)
        self.assertEqual(stats["recovery_strategies"]["create_file"]["successes"], 3)
        self.assertEqual(stats["recovery_strategies"]["elevate_permissions"]["attempts"], 2)
        self.assertEqual(stats["recovery_strategies"]["elevate_permissions"]["successes"], 1)
        
if __name__ == '__main__':
    unittest.main()
