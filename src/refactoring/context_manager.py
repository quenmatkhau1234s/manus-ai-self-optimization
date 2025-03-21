"""
Enhanced Context Management System for Manus AI

This module implements a hierarchical context summarization system to improve
long-term memory capabilities while maintaining processing efficiency.
"""

class ContextManager:
    """
    Manages context information with hierarchical summarization to optimize
    memory usage while preserving essential information.
    """
    
    def __init__(self, max_context_size=10000, summarization_threshold=0.8):
        """
        Initialize the context manager with configuration parameters.
        
        Args:
            max_context_size: Maximum number of tokens to maintain in active context
            summarization_threshold: Threshold at which summarization is triggered
        """
        self.max_context_size = max_context_size
        self.summarization_threshold = summarization_threshold
        self.current_context_size = 0
        self.active_context = []
        self.summarized_context = []
        self.importance_weights = {}
        
    def add_event(self, event, importance=1.0):
        """
        Add a new event to the context with specified importance.
        
        Args:
            event: The event to add to context
            importance: Importance score (0.0-1.0) affecting retention priority
        """
        # Add event to active context
        self.active_context.append(event)
        self.importance_weights[event['id']] = importance
        
        # Update current context size
        self.current_context_size += self._estimate_token_count(event)
        
        # Check if summarization is needed
        if self.current_context_size > self.max_context_size * self.summarization_threshold:
            self._perform_summarization()
            
    def get_full_context(self):
        """
        Get the full context including both active and summarized information.
        
        Returns:
            Combined context with metadata indicating summarization status
        """
        return {
            'active_context': self.active_context,
            'summarized_context': self.summarized_context,
            'total_events_processed': len(self.active_context) + sum(s['event_count'] for s in self.summarized_context)
        }
    
    def get_relevant_context(self, query, max_items=10):
        """
        Get context items most relevant to the provided query.
        
        Args:
            query: The query to match against context
            max_items: Maximum number of items to return
            
        Returns:
            List of most relevant context items
        """
        # Combine active and expanded summarized context
        all_context = self.active_context + self._expand_summaries(query)
        
        # Calculate relevance scores (simplified implementation)
        relevance_scores = self._calculate_relevance(all_context, query)
        
        # Sort by relevance and return top items
        sorted_context = sorted(
            zip(all_context, relevance_scores),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [item for item, score in sorted_context[:max_items]]
    
    def _perform_summarization(self):
        """
        Summarize older, less important context to reduce memory usage.
        """
        # Sort events by importance and recency
        events_to_summarize = self._select_events_for_summarization()
        
        if not events_to_summarize:
            return
            
        # Create summary of selected events
        summary = self._create_summary(events_to_summarize)
        
        # Remove summarized events from active context
        self.active_context = [e for e in self.active_context if e not in events_to_summarize]
        
        # Add summary to summarized context
        self.summarized_context.append(summary)
        
        # Recalculate current context size
        self.current_context_size = sum(self._estimate_token_count(e) for e in self.active_context)
    
    def _select_events_for_summarization(self):
        """
        Select which events should be summarized based on importance and recency.
        
        Returns:
            List of events to be summarized
        """
        # Calculate combined score (importance and recency)
        scored_events = []
        for i, event in enumerate(self.active_context):
            # Recency score (0-1) with more recent events having higher scores
            recency_score = i / max(1, len(self.active_context) - 1)
            # Importance score from stored weights
            importance_score = self.importance_weights.get(event['id'], 0.5)
            # Combined score favoring both important and recent events
            combined_score = 0.7 * importance_score + 0.3 * recency_score
            
            scored_events.append((event, combined_score))
        
        # Sort by score (ascending, so lowest scores first)
        scored_events.sort(key=lambda x: x[1])
        
        # Select lowest-scoring events that add up to ~30% of context
        target_reduction = self.current_context_size * 0.3
        current_reduction = 0
        events_to_summarize = []
        
        for event, score in scored_events:
            event_size = self._estimate_token_count(event)
            if current_reduction + event_size <= target_reduction:
                events_to_summarize.append(event)
                current_reduction += event_size
            else:
                break
                
        return events_to_summarize
    
    def _create_summary(self, events):
        """
        Create a summary of the provided events.
        
        Args:
            events: List of events to summarize
            
        Returns:
            Summary object containing condensed information
        """
        # Extract key information from events
        event_types = {}
        for event in events:
            event_type = event.get('type', 'unknown')
            if event_type not in event_types:
                event_types[event_type] = 0
            event_types[event_type] += 1
        
        # Create summary object
        summary = {
            'id': f"summary_{len(self.summarized_context)}",
            'type': 'summary',
            'event_count': len(events),
            'event_types': event_types,
            'time_range': {
                'start': events[0].get('date', ''),
                'end': events[-1].get('date', '')
            },
            'key_entities': self._extract_key_entities(events),
            'content_summary': self._summarize_content(events)
        }
        
        return summary
    
    def _extract_key_entities(self, events):
        """
        Extract key entities mentioned in the events.
        
        Args:
            events: List of events to analyze
            
        Returns:
            Dictionary of entity types and their occurrences
        """
        # Simplified implementation - in practice would use NLP techniques
        entities = {}
        
        # Extract entities from event payloads
        for event in events:
            if 'payload' in event:
                # Extract user mentions
                if event.get('source') == 'user':
                    entities['user_request'] = entities.get('user_request', 0) + 1
                
                # Extract tool mentions
                if event.get('tool'):
                    tool = event.get('tool')
                    entities[f'tool_{tool}'] = entities.get(f'tool_{tool}', 0) + 1
        
        return entities
    
    def _summarize_content(self, events):
        """
        Create a textual summary of event content.
        
        Args:
            events: List of events to summarize
            
        Returns:
            Text summary of the events
        """
        # Count event types
        event_types = {}
        for event in events:
            event_type = event.get('type', 'unknown')
            if event_type not in event_types:
                event_types[event_type] = 0
            event_types[event_type] += 1
        
        # Create summary text
        summary_parts = []
        
        # Summarize by event type
        for event_type, count in event_types.items():
            if event_type == 'message' and count > 0:
                summary_parts.append(f"User-AI conversation with {count} messages")
            elif event_type == 'action' and count > 0:
                summary_parts.append(f"{count} tool actions executed")
            elif event_type == 'observation' and count > 0:
                summary_parts.append(f"{count} observations recorded")
        
        # Join summary parts
        return ". ".join(summary_parts)
    
    def _expand_summaries(self, query):
        """
        Expand relevant summaries based on query for context retrieval.
        
        Args:
            query: The query to match against summaries
            
        Returns:
            List of expanded events from relevant summaries
        """
        # In a full implementation, this would selectively expand summaries
        # based on relevance to the query. This is a simplified version.
        return []
    
    def _calculate_relevance(self, context_items, query):
        """
        Calculate relevance scores between context items and query.
        
        Args:
            context_items: List of context items to score
            query: The query to match against
            
        Returns:
            List of relevance scores
        """
        # Simplified relevance calculation
        # In practice, would use semantic similarity or other NLP techniques
        scores = []
        query_terms = query.lower().split()
        
        for item in context_items:
            score = 0
            item_text = str(item).lower()
            
            for term in query_terms:
                if term in item_text:
                    score += 1
            
            # Normalize score
            score = score / max(1, len(query_terms))
            scores.append(score)
            
        return scores
    
    def _estimate_token_count(self, event):
        """
        Estimate the token count of an event.
        
        Args:
            event: The event to estimate token count for
            
        Returns:
            Estimated token count
        """
        # Simplified token estimation
        # In practice, would use a more accurate tokenization method
        event_str = str(event)
        # Rough estimate: 1 token per 4 characters
        return len(event_str) // 4
