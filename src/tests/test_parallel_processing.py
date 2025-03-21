"""
Unit tests for the Parallel Processing System module.

This module contains tests to verify the functionality of the ParallelProcessingSystem class
which implements task decomposition and parallel execution for Manus AI.
"""

import unittest
import sys
import os
import time

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from refactoring.parallel_processing import ParallelProcessingSystem

class TestParallelProcessingSystem(unittest.TestCase):
    """Test cases for the ParallelProcessingSystem class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parallel_system = ParallelProcessingSystem(max_parallel_tasks=4)
        
    def test_initialization(self):
        """Test that the parallel processing system initializes correctly."""
        self.assertEqual(self.parallel_system.max_parallel_tasks, 4)
        self.assertEqual(len(self.parallel_system.active_tasks), 0)
        self.assertEqual(len(self.parallel_system.task_dependencies), 0)
        self.assertEqual(len(self.parallel_system.task_results), 0)
        self.assertEqual(len(self.parallel_system.task_queue), 0)
        self.assertEqual(len(self.parallel_system.completed_tasks), 0)
        self.assertEqual(len(self.parallel_system.failed_tasks), 0)
        
    def test_decompose_task_auto(self):
        """Test automatic task decomposition."""
        # Create a simple task
        task = {
            "name": "Process data",
            "description": "Process a large dataset"
        }
        
        # Decompose task
        task_id = self.parallel_system.decompose_task(task)
        
        # Verify task was decomposed
        self.assertIn(task_id, self.parallel_system.active_tasks)
        self.assertIn(task_id, self.parallel_system.task_dependencies)
        self.assertIn(task_id, self.parallel_system.task_results)
        
        # Verify subtasks were created
        subtasks = self.parallel_system.active_tasks[task_id]["subtasks"]
        self.assertGreaterEqual(len(subtasks), 1)
        
        # Verify task status
        self.assertEqual(self.parallel_system.active_tasks[task_id]["status"], "decomposed")
        self.assertEqual(self.parallel_system.active_tasks[task_id]["progress"], 0.0)
        
    def test_decompose_task_with_definitions(self):
        """Test task decomposition with provided subtask definitions."""
        # Create a task with subtask definitions
        task = {
            "name": "Generate report",
            "description": "Generate a comprehensive report"
        }
        
        subtask_definitions = [
            {
                "id": "collect_data",
                "description": "Collect data from sources",
                "action": {"type": "collect", "params": {"sources": ["db1", "db2"]}},
                "dependencies": []
            },
            {
                "id": "analyze_data",
                "description": "Analyze collected data",
                "action": {"type": "analyze", "params": {"method": "statistical"}},
                "dependencies": ["collect_data"]
            },
            {
                "id": "generate_charts",
                "description": "Generate charts from analysis",
                "action": {"type": "visualize", "params": {"type": "charts"}},
                "dependencies": ["analyze_data"]
            },
            {
                "id": "write_report",
                "description": "Write the final report",
                "action": {"type": "write", "params": {"format": "pdf"}},
                "dependencies": ["analyze_data", "generate_charts"]
            }
        ]
        
        # Decompose task with definitions
        task_id = self.parallel_system.decompose_task(task, subtask_definitions)
        
        # Verify task was decomposed
        self.assertIn(task_id, self.parallel_system.active_tasks)
        
        # Verify subtasks match definitions
        subtasks = self.parallel_system.active_tasks[task_id]["subtasks"]
        self.assertEqual(len(subtasks), 4)
        
        # Verify dependencies were set correctly
        dependencies = self.parallel_system.task_dependencies[task_id]
        self.assertEqual(len(dependencies["collect_data"]), 0)
        self.assertEqual(len(dependencies["analyze_data"]), 1)
        self.assertEqual(len(dependencies["write_report"]), 2)
        
    def test_execute_task(self):
        """Test executing a decomposed task."""
        # Create and decompose a task with simple subtasks
        task = {"name": "Simple task"}
        
        subtask_definitions = [
            {
                "id": "subtask_1",
                "description": "First subtask",
                "action": {"type": "process", "params": {}},
                "dependencies": []
            },
            {
                "id": "subtask_2",
                "description": "Second subtask",
                "action": {"type": "process", "params": {}},
                "dependencies": []
            }
        ]
        
        task_id = self.parallel_system.decompose_task(task, subtask_definitions)
        
        # Execute task
        execution_status = self.parallel_system.execute_task(task_id)
        
        # Verify execution started
        self.assertEqual(execution_status["status"], "executing")
        self.assertEqual(self.parallel_system.active_tasks[task_id]["status"], "executing")
        
        # Verify subtasks were queued
        self.assertGreaterEqual(execution_status["executed"], 0)
        
    def test_get_task_status(self):
        """Test getting task status."""
        # Create and decompose a task
        task = {"name": "Status test task"}
        task_id = self.parallel_system.decompose_task(task)
        
        # Get initial status
        initial_status = self.parallel_system.get_task_status(task_id)
        
        # Verify initial status
        self.assertEqual(initial_status["status"], "decomposed")
        self.assertEqual(initial_status["progress"], 0.0)
        self.assertEqual(initial_status["completed_subtasks"], 0)
        
        # Execute task
        self.parallel_system.execute_task(task_id)
        
        # Get status during execution
        execution_status = self.parallel_system.get_task_status(task_id)
        
        # Verify execution status
        self.assertEqual(execution_status["status"], "executing")
        
        # Manually complete all subtasks to test completion status
        for subtask_id in self.parallel_system.task_results[task_id]:
            self.parallel_system.task_results[task_id][subtask_id] = {
                "status": "completed",
                "result": "Test result"
            }
            self.parallel_system.completed_tasks.add(subtask_id)
            
        # Get final status
        final_status = self.parallel_system.get_task_status(task_id)
        
        # Verify completion status
        self.assertEqual(final_status["status"], "completed")
        self.assertEqual(final_status["progress"], 1.0)
        self.assertEqual(final_status["completed_subtasks"], len(self.parallel_system.task_results[task_id]))
        
    def test_get_task_results(self):
        """Test getting task results."""
        # Create and decompose a task
        task = {"name": "Results test task"}
        task_id = self.parallel_system.decompose_task(task)
        
        # Execute task
        self.parallel_system.execute_task(task_id)
        
        # Get results before completion
        pending_results = self.parallel_system.get_task_results(task_id)
        
        # Verify pending results
        self.assertEqual(pending_results["status"], "pending")
        
        # Manually complete all subtasks
        for subtask_id in self.parallel_system.task_results[task_id]:
            self.parallel_system.task_results[task_id][subtask_id] = {
                "status": "completed",
                "result": f"Result for {subtask_id}"
            }
            self.parallel_system.completed_tasks.add(subtask_id)
            
        # Update task status to completed
        self.parallel_system.active_tasks[task_id]["status"] = "completed"
        self.parallel_system.active_tasks[task_id]["end_time"] = self.parallel_system._get_timestamp()
        
        # Get final results
        final_results = self.parallel_system.get_task_results(task_id)
        
        # Verify final results
        self.assertEqual(final_results["status"], "completed")
        self.assertIn("execution_time", final_results)
        self.assertIn("subtask_results", final_results)
        self.assertEqual(len(final_results["subtask_results"]), len(self.parallel_system.task_results[task_id]))
        
    def test_cancel_task(self):
        """Test cancelling a running task."""
        # Create and decompose a task
        task = {"name": "Cancel test task"}
        task_id = self.parallel_system.decompose_task(task)
        
        # Execute task
        self.parallel_system.execute_task(task_id)
        
        # Cancel task
        cancel_result = self.parallel_system.cancel_task(task_id)
        
        # Verify cancellation
        self.assertEqual(cancel_result["status"], "success")
        self.assertEqual(self.parallel_system.active_tasks[task_id]["status"], "cancelled")
        
        # Verify task queue was updated
        for item in self.parallel_system.task_queue:
            self.assertNotEqual(item["task_id"], task_id)
            
    def test_queue_dependent_subtasks(self):
        """Test queuing dependent subtasks after completion."""
        # Create a task with dependencies
        task = {"name": "Dependency test task"}
        
        subtask_definitions = [
            {
                "id": "subtask_1",
                "description": "First subtask",
                "action": {"type": "process", "params": {}},
                "dependencies": []
            },
            {
                "id": "subtask_2",
                "description": "Second subtask",
                "action": {"type": "process", "params": {}},
                "dependencies": ["subtask_1"]
            },
            {
                "id": "subtask_3",
                "description": "Third subtask",
                "action": {"type": "process", "params": {}},
                "dependencies": ["subtask_1"]
            },
            {
                "id": "subtask_4",
                "description": "Fourth subtask",
                "action": {"type": "process", "params": {}},
                "dependencies": ["subtask_2", "subtask_3"]
            }
        ]
        
        task_id = self.parallel_system.decompose_task(task, subtask_definitions)
        
        # Execute task (should only queue subtask_1 initially)
        self.parallel_system.execute_task(task_id)
        
        # Verify only first subtask is queued
        initial_queue_ids = [item["subtask_id"] for item in self.parallel_system.task_queue]
        self.assertIn("subtask_1", initial_queue_ids)
        self.assertNotIn("subtask_2", initial_queue_ids)
        self.assertNotIn("subtask_3", initial_queue_ids)
        
        # Manually complete first subtask
        self.parallel_system.task_results[task_id]["subtask_1"] = {
            "status": "completed",
            "result": "Completed first subtask"
        }
        self.parallel_system.completed_tasks.add("subtask_1")
        
        # Queue dependent subtasks
        self.parallel_system._queue_dependent_subtasks(task_id, "subtask_1")
        
        # Verify dependent subtasks are queued
        updated_queue_ids = [item["subtask_id"] for item in self.parallel_system.task_queue]
        self.assertIn("subtask_2", updated_queue_ids)
        self.assertIn("subtask_3", updated_queue_ids)
        self.assertNotIn("subtask_4", updated_queue_ids)
        
        # Manually complete second and third subtasks
        self.parallel_system.task_results[task_id]["subtask_2"] = {
            "status": "completed",
            "result": "Completed second subtask"
        }
        self.parallel_system.completed_tasks.add("subtask_2")
        
        self.parallel_system.task_results[task_id]["subtask_3"] = {
            "status": "completed",
            "result": "Completed third subtask"
        }
        self.parallel_system.completed_tasks.add("subtask_3")
        
        # Queue dependent subtasks after completing subtask_2
        self.parallel_system._queue_dependent_subtasks(task_id, "subtask_2")
        
        # Verify fourth subtask is not yet queued (needs both 2 and 3)
        after_subtask2_queue_ids = [item["subtask_id"] for item in self.parallel_system.task_queue]
        self.assertNotIn("subtask_4", after_subtask2_queue_ids)
        
        # Queue dependent subtasks after completing subtask_3
        self.parallel_system._queue_dependent_subtasks(task_id, "subtask_3")
        
        # Verify fourth subtask is now queued
        final_queue_ids = [item["subtask_id"] for item in self.parallel_system.task_queue]
        self.assertIn("subtask_4", final_queue_ids)
        
    def test_generate_task_id(self):
        """Test generating unique task IDs."""
        # Create two identical tasks
        task1 = {"name": "Test task", "data": [1, 2, 3]}
        task2 = {"name": "Test task", "data": [1, 2, 3]}
        
        # Generate IDs
        id1 = self.parallel_system._generate_task_id(task1)
        time.sleep(0.01)  # Ensure timestamp is different
        id2 = self.parallel_system._generate_task_id(task2)
        
        # Verify IDs are different despite identical tasks
        self.assertNotEqual(id1, id2)
        
        # Verify ID format
        self.assertTrue(id1.startswith("task_"))
        self.assertTrue(id2.startswith("task_"))
        
if __name__ == '__main__':
    unittest.main()
