"""
Unit tests for the Tool Selector module.

This module contains tests to verify the functionality of the ToolSelector class
which implements predictive tool selection for Manus AI.
"""

import unittest
import sys
import os

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from refactoring.tool_selector import ToolSelector

class TestToolSelector(unittest.TestCase):
    """Test cases for the ToolSelector class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tool_selector = ToolSelector()
        
        # Register test tools
        self.tool_selector.register_tool(
            "file_read",
            ["read file", "access file content", "view file"],
            {"file": "string", "start_line": "integer", "end_line": "integer"}
        )
        
        self.tool_selector.register_tool(
            "file_write",
            ["write file", "create file", "modify file"],
            {"file": "string", "content": "string", "append": "boolean"}
        )
        
        self.tool_selector.register_tool(
            "browser_navigate",
            ["open url", "navigate to website", "browse web"],
            {"url": "string"}
        )
        
    def test_initialization(self):
        """Test that the tool selector initializes correctly."""
        self.assertEqual(len(self.tool_selector.tool_history), 0)
        self.assertEqual(len(self.tool_selector.context_patterns), 0)
        self.assertEqual(len(self.tool_selector.success_metrics), 3)  # Three registered tools
        self.assertEqual(len(self.tool_selector.available_tools), 3)  # Three registered tools
        
    def test_register_tool(self):
        """Test registering a new tool."""
        # Register a new tool
        self.tool_selector.register_tool(
            "shell_exec",
            ["execute command", "run shell", "terminal command"],
            {"command": "string", "exec_dir": "string"}
        )
        
        # Verify tool was registered
        self.assertIn("shell_exec", self.tool_selector.available_tools)
        self.assertIn("shell_exec", self.tool_selector.tool_capabilities)
        self.assertIn("shell_exec", self.tool_selector.success_metrics)
        
        # Verify capabilities were stored
        self.assertEqual(len(self.tool_selector.tool_capabilities["shell_exec"]["capabilities"]), 3)
        self.assertEqual(len(self.tool_selector.tool_capabilities["shell_exec"]["parameters"]), 2)
        
    def test_select_tool_basic(self):
        """Test basic tool selection based on user intent."""
        # Create a simple task context
        task_context = {
            "events": [
                {"type": "message", "source": "user", "payload": "I need to read a file"}
            ]
        }
        
        # Create a simple user intent
        user_intent = {
            "action": "read",
            "object": "file",
            "path": "/home/user/document.txt"
        }
        
        # Create available data
        available_data = {
            "file": "/home/user/document.txt"
        }
        
        # Select tool
        result = self.tool_selector.select_tool(task_context, user_intent, available_data)
        
        # Verify correct tool was selected
        self.assertEqual(result["tool"], "file_read")
        self.assertGreater(result["confidence"], 0)
        self.assertIn("parameter_recommendations", result)
        
    def test_select_tool_with_history(self):
        """Test tool selection with historical data."""
        # Record successful use of file_read
        self.tool_selector.record_tool_result(
            "file_read",
            {"task_type": "read_file", "recent_tools": [], "data_types": {"file"}, "complexity": 1},
            True,  # Success
            100    # Latency in ms
        )
        
        # Create a task context similar to the successful one
        task_context = {
            "events": [
                {"type": "message", "source": "user", "payload": "I need to read a file"}
            ]
        }
        
        # Create a user intent that could match multiple tools
        user_intent = {
            "action": "access",
            "object": "content"
        }
        
        # Create available data
        available_data = {
            "file": "/home/user/document.txt"
        }
        
        # Select tool
        result = self.tool_selector.select_tool(task_context, user_intent, available_data)
        
        # Verify file_read was selected due to historical success
        self.assertEqual(result["tool"], "file_read")
        
    def test_record_tool_result(self):
        """Test recording tool execution results."""
        # Record a successful result
        context_features = {
            "task_type": "write_file",
            "recent_tools": ["file_read"],
            "data_types": {"file"},
            "complexity": 2
        }
        
        self.tool_selector.record_tool_result(
            "file_write",
            context_features,
            True,  # Success
            150    # Latency in ms
        )
        
        # Verify metrics were updated
        metrics = self.tool_selector.success_metrics["file_write"]
        self.assertEqual(metrics["calls"], 1)
        self.assertEqual(metrics["successes"], 1)
        self.assertEqual(metrics["failures"], 0)
        self.assertEqual(metrics["avg_latency"], 150)
        
        # Record a failure
        self.tool_selector.record_tool_result(
            "file_write",
            context_features,
            False,  # Failure
            200,    # Latency in ms
            "permission_denied"  # Error type
        )
        
        # Verify metrics were updated
        metrics = self.tool_selector.success_metrics["file_write"]
        self.assertEqual(metrics["calls"], 2)
        self.assertEqual(metrics["successes"], 1)
        self.assertEqual(metrics["failures"], 1)
        self.assertNotEqual(metrics["avg_latency"], 150)  # Should have changed
        
    def test_get_tool_statistics(self):
        """Test retrieving tool usage statistics."""
        # Record some tool results
        context_features = {"task_type": "general", "recent_tools": [], "data_types": set(), "complexity": 1}
        
        # Record for file_read
        self.tool_selector.record_tool_result("file_read", context_features, True, 100)
        self.tool_selector.record_tool_result("file_read", context_features, True, 120)
        self.tool_selector.record_tool_result("file_read", context_features, False, 150)
        
        # Record for browser_navigate
        self.tool_selector.record_tool_result("browser_navigate", context_features, True, 80)
        self.tool_selector.record_tool_result("browser_navigate", context_features, False, 90)
        
        # Get statistics
        stats = self.tool_selector.get_tool_statistics()
        
        # Verify statistics
        self.assertIn("file_read", stats)
        self.assertIn("browser_navigate", stats)
        self.assertIn("file_write", stats)
        
        self.assertEqual(stats["file_read"]["calls"], 3)
        self.assertAlmostEqual(stats["file_read"]["success_rate"], 2/3, places=2)
        
        self.assertEqual(stats["browser_navigate"]["calls"], 2)
        self.assertAlmostEqual(stats["browser_navigate"]["success_rate"], 0.5, places=2)
        
        self.assertEqual(stats["file_write"]["calls"], 0)
        self.assertEqual(stats["file_write"]["success_rate"], 0)
        
    def test_parameter_recommendations(self):
        """Test parameter recommendations for selected tools."""
        # Create context with file information
        task_context = {
            "files": ["/home/user/document.txt"]
        }
        
        # Create user intent
        user_intent = {
            "action": "read",
            "object": "file"
        }
        
        # Create available data
        available_data = {}  # Empty to force inference from context
        
        # Select tool
        result = self.tool_selector.select_tool(task_context, user_intent, available_data)
        
        # Verify parameter recommendations
        self.assertIn("parameter_recommendations", result)
        recommendations = result["parameter_recommendations"]
        self.assertIn("file", recommendations)
        self.assertEqual(recommendations["file"], "/home/user/document.txt")
        
    def test_alternative_tools(self):
        """Test alternative tool suggestions."""
        # Create a context where multiple tools could be appropriate
        task_context = {
            "events": [
                {"type": "message", "source": "user", "payload": "I need to access content"}
            ]
        }
        
        # Create a vague user intent
        user_intent = {
            "action": "access",
            "object": "content"
        }
        
        # Create available data with both file and URL
        available_data = {
            "file": "/home/user/document.txt",
            "url": "https://example.com"
        }
        
        # Select tool
        result = self.tool_selector.select_tool(task_context, user_intent, available_data)
        
        # Verify alternative tools are provided
        self.assertIn("alternative_tools", result)
        self.assertGreaterEqual(len(result["alternative_tools"]), 1)
        
if __name__ == '__main__':
    unittest.main()
