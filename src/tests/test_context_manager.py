"""
Unit tests for the Context Manager module.

This module contains tests to verify the functionality of the ContextManager class
which implements hierarchical context summarization for Manus AI.
"""

import unittest
import sys
import os
import time

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from refactoring.context_manager import ContextManager

class TestContextManager(unittest.TestCase):
    """Test cases for the ContextManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.context_manager = ContextManager(max_context_size=1000, summarization_threshold=0.8)
        
    def test_initialization(self):
        """Test that the context manager initializes correctly."""
        self.assertEqual(self.context_manager.max_context_size, 1000)
        self.assertEqual(self.context_manager.summarization_threshold, 0.8)
        self.assertEqual(self.context_manager.current_context_size, 0)
        self.assertEqual(len(self.context_manager.active_context), 0)
        self.assertEqual(len(self.context_manager.summarized_context), 0)
        
    def test_add_event(self):
        """Test adding events to the context."""
        # Create test event
        event = {
            'id': 'event_1',
            'type': 'message',
            'source': 'user',
            'date': '2025-03-21',
            'payload': 'Test message'
        }
        
        # Add event
        self.context_manager.add_event(event, importance=0.8)
        
        # Verify event was added
        self.assertEqual(len(self.context_manager.active_context), 1)
        self.assertEqual(self.context_manager.active_context[0], event)
        self.assertEqual(self.context_manager.importance_weights['event_1'], 0.8)
        self.assertGreater(self.context_manager.current_context_size, 0)
        
    def test_get_full_context(self):
        """Test retrieving the full context."""
        # Add multiple events
        for i in range(5):
            event = {
                'id': f'event_{i}',
                'type': 'message',
                'source': 'user',
                'date': '2025-03-21',
                'payload': f'Test message {i}'
            }
            self.context_manager.add_event(event)
            
        # Get full context
        full_context = self.context_manager.get_full_context()
        
        # Verify structure
        self.assertIn('active_context', full_context)
        self.assertIn('summarized_context', full_context)
        self.assertIn('total_events_processed', full_context)
        
        # Verify content
        self.assertEqual(len(full_context['active_context']), 5)
        self.assertEqual(full_context['total_events_processed'], 5)
        
    def test_get_relevant_context(self):
        """Test retrieving context relevant to a query."""
        # Add events with different content
        events = [
            {
                'id': 'event_1',
                'type': 'message',
                'source': 'user',
                'date': '2025-03-21',
                'payload': 'Information about Python programming'
            },
            {
                'id': 'event_2',
                'type': 'message',
                'source': 'user',
                'date': '2025-03-21',
                'payload': 'Data about machine learning algorithms'
            },
            {
                'id': 'event_3',
                'type': 'message',
                'source': 'user',
                'date': '2025-03-21',
                'payload': 'Questions about JavaScript frameworks'
            }
        ]
        
        for event in events:
            self.context_manager.add_event(event)
            
        # Get relevant context for Python query
        python_context = self.context_manager.get_relevant_context('Python programming')
        
        # Verify most relevant result is first
        self.assertIn('Python', str(python_context[0]))
        
        # Get relevant context for JavaScript query
        js_context = self.context_manager.get_relevant_context('JavaScript')
        
        # Verify most relevant result is first
        self.assertIn('JavaScript', str(js_context[0]))
        
    def test_summarization_trigger(self):
        """Test that summarization is triggered when threshold is reached."""
        # Create a context manager with small max size
        small_context_manager = ContextManager(max_context_size=100, summarization_threshold=0.8)
        
        # Add events until summarization should trigger
        initial_active_count = 0
        events_added = 0
        
        while events_added < 20:  # Limit to prevent infinite loop
            event = {
                'id': f'event_{events_added}',
                'type': 'message',
                'source': 'user',
                'date': '2025-03-21',
                'payload': 'A' * 50  # Create event with substantial size
            }
            
            small_context_manager.add_event(event)
            events_added += 1
            
            # Check if summarization has occurred
            current_active_count = len(small_context_manager.active_context)
            if current_active_count < events_added and len(small_context_manager.summarized_context) > 0:
                break
                
        # Verify summarization occurred
        self.assertLess(len(small_context_manager.active_context), events_added)
        self.assertGreater(len(small_context_manager.summarized_context), 0)
        
    def test_importance_based_retention(self):
        """Test that important events are retained longer during summarization."""
        # Create a context manager with small max size
        small_context_manager = ContextManager(max_context_size=100, summarization_threshold=0.8)
        
        # Add a high-importance event
        important_event = {
            'id': 'important_event',
            'type': 'message',
            'source': 'user',
            'date': '2025-03-21',
            'payload': 'Critical information'
        }
        small_context_manager.add_event(important_event, importance=1.0)
        
        # Add many low-importance events to trigger summarization
        for i in range(20):
            event = {
                'id': f'low_importance_{i}',
                'type': 'message',
                'source': 'user',
                'date': '2025-03-21',
                'payload': 'Low importance information'
            }
            small_context_manager.add_event(event, importance=0.1)
            
        # Verify important event is still in active context
        active_ids = [e['id'] for e in small_context_manager.active_context]
        self.assertIn('important_event', active_ids)
        
    def test_estimate_token_count(self):
        """Test token count estimation."""
        event = {
            'id': 'test_event',
            'type': 'message',
            'payload': 'This is a test message with approximately twenty tokens in it for testing the token estimation function'
        }
        
        # Estimate tokens
        token_count = self.context_manager._estimate_token_count(event)
        
        # Verify reasonable estimate (exact count may vary by implementation)
        self.assertGreater(token_count, 0)
        
if __name__ == '__main__':
    unittest.main()
