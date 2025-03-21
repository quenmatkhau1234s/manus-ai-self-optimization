"""
Unit tests for the Knowledge Retrieval System module.

This module contains tests to verify the functionality of the KnowledgeRetrievalSystem class
which implements semantic indexing and vector-based retrieval for Manus AI.
"""

import unittest
import sys
import os

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from refactoring.knowledge_retrieval import KnowledgeRetrievalSystem

class TestKnowledgeRetrievalSystem(unittest.TestCase):
    """Test cases for the KnowledgeRetrievalSystem class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.knowledge_system = KnowledgeRetrievalSystem(dimensions=64, index_refresh_threshold=10)
        
        # Add some test knowledge items
        self.knowledge_system.add_knowledge_item(
            "python_basics",
            "Python is a high-level, interpreted programming language known for its readability and simplicity.",
            {"type": "language", "category": "programming"}
        )
        
        self.knowledge_system.add_knowledge_item(
            "machine_learning",
            "Machine learning is a subset of artificial intelligence that enables systems to learn from data.",
            {"type": "concept", "category": "ai"}
        )
        
        self.knowledge_system.add_knowledge_item(
            "javascript_intro",
            "JavaScript is a scripting language used primarily for web development and creating interactive web pages.",
            {"type": "language", "category": "programming"}
        )
        
    def test_initialization(self):
        """Test that the knowledge retrieval system initializes correctly."""
        self.assertEqual(self.knowledge_system.dimensions, 64)
        self.assertEqual(self.knowledge_system.index_refresh_threshold, 10)
        self.assertEqual(len(self.knowledge_system.knowledge_store), 3)
        self.assertEqual(len(self.knowledge_system.vector_index), 3)
        self.assertGreater(len(self.knowledge_system.inverted_index), 0)
        
    def test_add_knowledge_item(self):
        """Test adding a knowledge item."""
        # Add a new knowledge item
        self.knowledge_system.add_knowledge_item(
            "neural_networks",
            "Neural networks are computing systems inspired by the biological neural networks in animal brains.",
            {"type": "concept", "category": "ai"}
        )
        
        # Verify item was added
        self.assertIn("neural_networks", self.knowledge_system.knowledge_store)
        self.assertIn("neural_networks", self.knowledge_system.vector_index)
        
        # Verify content was stored
        item = self.knowledge_system.knowledge_store["neural_networks"]
        self.assertEqual(item["metadata"]["type"], "concept")
        self.assertEqual(item["metadata"]["category"], "ai")
        self.assertIn("neural networks", item["content"].lower())
        
        # Verify embedding was created
        self.assertEqual(len(item["embedding"]), 64)
        
    def test_retrieve_knowledge_semantic(self):
        """Test retrieving knowledge based on semantic similarity."""
        # Retrieve knowledge about AI
        results = self.knowledge_system.retrieve_knowledge("artificial intelligence and neural networks")
        
        # Verify results contain relevant items
        self.assertGreaterEqual(len(results), 1)
        
        # Check if machine learning is in the results
        ml_found = False
        for result in results:
            if result["id"] == "machine_learning":
                ml_found = True
                break
                
        self.assertTrue(ml_found, "Machine learning should be found for AI query")
        
    def test_retrieve_knowledge_keyword(self):
        """Test retrieving knowledge based on keyword matching."""
        # Retrieve knowledge about programming languages
        results = self.knowledge_system.retrieve_knowledge("programming language Python")
        
        # Verify results contain relevant items
        self.assertGreaterEqual(len(results), 1)
        
        # Check if Python is in the results
        python_found = False
        for result in results:
            if result["id"] == "python_basics":
                python_found = True
                break
                
        self.assertTrue(python_found, "Python should be found for programming language query")
        
    def test_get_related_knowledge(self):
        """Test getting knowledge related to a specific item."""
        # Add more AI-related items
        self.knowledge_system.add_knowledge_item(
            "deep_learning",
            "Deep learning is a subset of machine learning using neural networks with many layers.",
            {"type": "concept", "category": "ai"}
        )
        
        self.knowledge_system.add_knowledge_item(
            "reinforcement_learning",
            "Reinforcement learning is a type of machine learning where agents learn to make decisions.",
            {"type": "concept", "category": "ai"}
        )
        
        # Get items related to machine learning
        related = self.knowledge_system.get_related_knowledge("machine_learning")
        
        # Verify related items were found
        self.assertGreaterEqual(len(related), 1)
        
        # Check if deep learning and reinforcement learning are in the results
        related_ids = [item["id"] for item in related]
        self.assertTrue(
            "deep_learning" in related_ids or "reinforcement_learning" in related_ids,
            "Related AI concepts should be found"
        )
        
    def test_remove_knowledge_item(self):
        """Test removing a knowledge item."""
        # Remove an item
        self.knowledge_system.remove_knowledge_item("javascript_intro")
        
        # Verify item was removed
        self.assertNotIn("javascript_intro", self.knowledge_system.knowledge_store)
        
        # Verify reindexing flag was set
        self.assertTrue(self.knowledge_system.needs_reindexing)
        
    def test_update_knowledge_item(self):
        """Test updating a knowledge item."""
        # Update an item
        self.knowledge_system.update_knowledge_item(
            "python_basics",
            "Python is a high-level, interpreted programming language known for its readability, simplicity, and versatility.",
            {"type": "language", "category": "programming", "popularity": "high"}
        )
        
        # Verify content was updated
        item = self.knowledge_system.knowledge_store["python_basics"]
        self.assertIn("versatility", item["content"])
        self.assertEqual(item["metadata"]["popularity"], "high")
        
        # Verify reindexing flag was set
        self.assertTrue(self.knowledge_system.needs_reindexing)
        
    def test_get_knowledge_statistics(self):
        """Test retrieving knowledge statistics."""
        # Get statistics
        stats = self.knowledge_system.get_knowledge_statistics()
        
        # Verify statistics
        self.assertEqual(stats["total_items"], 3)
        self.assertIn("type_distribution", stats)
        self.assertEqual(stats["type_distribution"]["language"], 2)
        self.assertEqual(stats["type_distribution"]["concept"], 1)
        
    def test_reindexing(self):
        """Test that reindexing occurs when threshold is reached."""
        # Add items until reindexing threshold is reached
        initial_update_count = self.knowledge_system.update_count
        
        for i in range(10):
            self.knowledge_system.add_knowledge_item(
                f"test_item_{i}",
                f"Test content for item {i}",
                {"type": "test"}
            )
            
        # Verify update count increased
        self.assertGreater(self.knowledge_system.update_count, initial_update_count)
        
        # Trigger retrieval which should cause reindexing
        self.knowledge_system.retrieve_knowledge("test query")
        
        # Verify reindexing occurred
        self.assertFalse(self.knowledge_system.needs_reindexing)
        self.assertEqual(self.knowledge_system.update_count, 0)
        
    def test_compute_similarity(self):
        """Test computing similarity between embeddings."""
        # Create two similar embeddings
        embedding1 = [0.1] * 32 + [0.9] * 32
        embedding2 = [0.2] * 32 + [0.8] * 32
        
        # Create a different embedding
        embedding3 = [0.9] * 32 + [0.1] * 32
        
        # Compute similarities
        similarity_similar = self.knowledge_system._compute_similarity(embedding1, embedding2)
        similarity_different = self.knowledge_system._compute_similarity(embedding1, embedding3)
        
        # Verify similar embeddings have higher similarity
        self.assertGreater(similarity_similar, similarity_different)
        
if __name__ == '__main__':
    unittest.main()
