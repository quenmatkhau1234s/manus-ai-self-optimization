"""
Knowledge Retrieval System for Manus AI

This module implements a semantic indexing and vector-based retrieval system
to improve the relevance and efficiency of knowledge retrieval.
"""

import math
from collections import defaultdict

class KnowledgeRetrievalSystem:
    """
    Manages knowledge retrieval with semantic indexing and vector-based search
    to optimize relevance and efficiency.
    """
    
    def __init__(self, dimensions=128, index_refresh_threshold=50):
        """
        Initialize the knowledge retrieval system.
        
        Args:
            dimensions: Dimensionality of vector embeddings
            index_refresh_threshold: Number of updates before index refresh
        """
        self.dimensions = dimensions
        self.index_refresh_threshold = index_refresh_threshold
        self.knowledge_store = {}
        self.vector_index = {}
        self.inverted_index = defaultdict(list)
        self.update_count = 0
        self.needs_reindexing = False
        
    def add_knowledge_item(self, item_id, content, metadata=None, embedding=None):
        """
        Add a knowledge item to the retrieval system.
        
        Args:
            item_id: Unique identifier for the knowledge item
            content: Text content of the knowledge item
            metadata: Additional metadata for the knowledge item
            embedding: Pre-computed embedding vector (optional)
        """
        # Store the knowledge item
        self.knowledge_store[item_id] = {
            'content': content,
            'metadata': metadata or {},
            'embedding': embedding or self._compute_embedding(content)
        }
        
        # Update indices
        self._update_indices(item_id)
        
        # Check if reindexing is needed
        self.update_count += 1
        if self.update_count >= self.index_refresh_threshold:
            self.needs_reindexing = True
            
    def retrieve_knowledge(self, query, max_results=5, threshold=0.6):
        """
        Retrieve knowledge items relevant to the query.
        
        Args:
            query: Search query text
            max_results: Maximum number of results to return
            threshold: Minimum relevance score threshold
            
        Returns:
            List of relevant knowledge items with scores
        """
        # Check if reindexing is needed
        if self.needs_reindexing:
            self._reindex()
            
        # Compute query embedding
        query_embedding = self._compute_embedding(query)
        
        # Perform semantic search
        semantic_results = self._semantic_search(query_embedding, max_results * 2, threshold)
        
        # Perform keyword search
        keyword_results = self._keyword_search(query, max_results * 2)
        
        # Combine and rank results
        combined_results = self._combine_results(semantic_results, keyword_results)
        
        # Return top results
        return combined_results[:max_results]
    
    def get_related_knowledge(self, item_id, max_results=5):
        """
        Get knowledge items related to a specific item.
        
        Args:
            item_id: ID of the knowledge item to find related items for
            max_results: Maximum number of results to return
            
        Returns:
            List of related knowledge items with scores
        """
        if item_id not in self.knowledge_store:
            return []
            
        # Get the embedding for the source item
        source_embedding = self.knowledge_store[item_id]['embedding']
        
        # Find related items by embedding similarity
        related_items = []
        for related_id, item in self.knowledge_store.items():
            if related_id == item_id:
                continue
                
            similarity = self._compute_similarity(source_embedding, item['embedding'])
            if similarity > 0.7:  # Higher threshold for relatedness
                related_items.append({
                    'id': related_id,
                    'content': item['content'],
                    'metadata': item['metadata'],
                    'similarity': similarity
                })
                
        # Sort by similarity
        related_items.sort(key=lambda x: x['similarity'], reverse=True)
        
        return related_items[:max_results]
    
    def remove_knowledge_item(self, item_id):
        """
        Remove a knowledge item from the retrieval system.
        
        Args:
            item_id: ID of the knowledge item to remove
        """
        if item_id not in self.knowledge_store:
            return
            
        # Remove from knowledge store
        del self.knowledge_store[item_id]
        
        # Mark for reindexing
        self.needs_reindexing = True
        
    def update_knowledge_item(self, item_id, content=None, metadata=None):
        """
        Update an existing knowledge item.
        
        Args:
            item_id: ID of the knowledge item to update
            content: New content (if None, keep existing)
            metadata: New metadata (if None, keep existing)
        """
        if item_id not in self.knowledge_store:
            return
            
        item = self.knowledge_store[item_id]
        
        # Update content if provided
        if content is not None:
            item['content'] = content
            item['embedding'] = self._compute_embedding(content)
            
        # Update metadata if provided
        if metadata is not None:
            item['metadata'] = metadata
            
        # Mark for reindexing
        self.needs_reindexing = True
        
    def get_knowledge_statistics(self):
        """
        Get statistics about the knowledge store.
        
        Returns:
            Dictionary of statistics
        """
        # Count items by type
        type_counts = defaultdict(int)
        for item in self.knowledge_store.values():
            item_type = item['metadata'].get('type', 'unknown')
            type_counts[item_type] += 1
            
        return {
            'total_items': len(self.knowledge_store),
            'type_distribution': dict(type_counts),
            'needs_reindexing': self.needs_reindexing,
            'update_count': self.update_count
        }
    
    def _compute_embedding(self, text):
        """
        Compute embedding vector for text.
        
        Args:
            text: Text to compute embedding for
            
        Returns:
            Embedding vector
        """
        # Simplified embedding computation
        # In practice, would use a proper embedding model
        
        # Create a simple frequency-based embedding
        words = text.lower().split()
        embedding = [0] * self.dimensions
        
        for i, word in enumerate(words):
            # Use hash of word to determine which dimensions to affect
            word_hash = hash(word) % self.dimensions
            embedding[word_hash] += 1
            
            # Add some context by affecting nearby dimensions
            for j in range(1, 4):
                left_dim = (word_hash - j) % self.dimensions
                right_dim = (word_hash + j) % self.dimensions
                embedding[left_dim] += 0.5 / j
                embedding[right_dim] += 0.5 / j
                
        # Normalize the embedding
        magnitude = math.sqrt(sum(x*x for x in embedding))
        if magnitude > 0:
            embedding = [x/magnitude for x in embedding]
            
        return embedding
    
    def _update_indices(self, item_id):
        """
        Update indices for a knowledge item.
        
        Args:
            item_id: ID of the knowledge item to index
        """
        item = self.knowledge_store[item_id]
        
        # Update vector index
        self.vector_index[item_id] = item['embedding']
        
        # Update inverted index
        content = item['content'].lower()
        words = set(content.split())
        
        for word in words:
            self.inverted_index[word].append(item_id)
    
    def _reindex(self):
        """Rebuild all indices."""
        # Clear existing indices
        self.vector_index = {}
        self.inverted_index = defaultdict(list)
        
        # Rebuild indices
        for item_id in self.knowledge_store:
            self._update_indices(item_id)
            
        # Reset counters
        self.update_count = 0
        self.needs_reindexing = False
    
    def _semantic_search(self, query_embedding, max_results, threshold):
        """
        Perform semantic search using vector similarity.
        
        Args:
            query_embedding: Embedding vector for the query
            max_results: Maximum number of results to return
            threshold: Minimum similarity threshold
            
        Returns:
            List of results with similarity scores
        """
        results = []
        
        for item_id, item in self.knowledge_store.items():
            similarity = self._compute_similarity(query_embedding, item['embedding'])
            
            if similarity >= threshold:
                results.append({
                    'id': item_id,
                    'content': item['content'],
                    'metadata': item['metadata'],
                    'score': similarity,
                    'match_type': 'semantic'
                })
                
        # Sort by similarity
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results[:max_results]
    
    def _keyword_search(self, query, max_results):
        """
        Perform keyword-based search.
        
        Args:
            query: Search query text
            max_results: Maximum number of results to return
            
        Returns:
            List of results with relevance scores
        """
        query_words = set(query.lower().split())
        item_scores = defaultdict(float)
        
        # Calculate TF-IDF style scores
        total_items = len(self.knowledge_store)
        
        for word in query_words:
            if word in self.inverted_index:
                # Inverse document frequency
                idf = math.log(total_items / (1 + len(self.inverted_index[word])))
                
                for item_id in self.inverted_index[word]:
                    # Term frequency (simplified)
                    content = self.knowledge_store[item_id]['content'].lower()
                    tf = content.count(word) / len(content.split())
                    
                    # TF-IDF score
                    item_scores[item_id] += tf * idf
        
        # Convert to result format
        results = []
        for item_id, score in item_scores.items():
            if score > 0:
                results.append({
                    'id': item_id,
                    'content': self.knowledge_store[item_id]['content'],
                    'metadata': self.knowledge_store[item_id]['metadata'],
                    'score': score,
                    'match_type': 'keyword'
                })
                
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results[:max_results]
    
    def _combine_results(self, semantic_results, keyword_results):
        """
        Combine and rank results from semantic and keyword searches.
        
        Args:
            semantic_results: Results from semantic search
            keyword_results: Results from keyword search
            
        Returns:
            Combined and ranked results
        """
        # Create a map of item_id to result
        combined_map = {}
        
        # Process semantic results
        for result in semantic_results:
            combined_map[result['id']] = {
                'id': result['id'],
                'content': result['content'],
                'metadata': result['metadata'],
                'semantic_score': result['score'],
                'keyword_score': 0,
                'combined_score': result['score'] * 0.7  # Weight semantic results higher
            }
            
        # Process keyword results
        for result in keyword_results:
            if result['id'] in combined_map:
                # Update existing entry
                combined_map[result['id']]['keyword_score'] = result['score']
                combined_map[result['id']]['combined_score'] += result['score'] * 0.3
            else:
                # Add new entry
                combined_map[result['id']] = {
                    'id': result['id'],
                    'content': result['content'],
                    'metadata': result['metadata'],
                    'semantic_score': 0,
                    'keyword_score': result['score'],
                    'combined_score': result['score'] * 0.3
                }
                
        # Convert map to list and sort by combined score
        combined_results = list(combined_map.values())
        combined_results.sort(key=lambda x: x['combined_score'], reverse=True)
        
        return combined_results
    
    def _compute_similarity(self, embedding1, embedding2):
        """
        Compute cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score
        """
        # Compute dot product
        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
        
        # Compute magnitudes
        magnitude1 = math.sqrt(sum(x*x for x in embedding1))
        magnitude2 = math.sqrt(sum(x*x for x in embedding2))
        
        # Compute cosine similarity
        if magnitude1 > 0 and magnitude2 > 0:
            return dot_product / (magnitude1 * magnitude2)
        else:
            return 0
