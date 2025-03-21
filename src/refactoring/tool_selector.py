"""
Optimized Tool Selection Algorithm for Manus AI

This module implements a predictive tool selection system that uses historical
success patterns to improve tool selection accuracy and efficiency.
"""

class ToolSelector:
    """
    Selects appropriate tools based on context, task requirements, and historical
    performance data to optimize first-attempt success rate.
    """
    
    def __init__(self):
        """Initialize the tool selector with default configuration."""
        self.tool_history = {}
        self.context_patterns = {}
        self.success_metrics = {}
        self.available_tools = set()
        self.tool_capabilities = {}
        
    def register_tool(self, tool_name, capabilities, parameters):
        """
        Register a tool with its capabilities and parameters.
        
        Args:
            tool_name: Unique identifier for the tool
            capabilities: List of capabilities provided by the tool
            parameters: Dictionary of parameters accepted by the tool
        """
        self.available_tools.add(tool_name)
        self.tool_capabilities[tool_name] = {
            'capabilities': capabilities,
            'parameters': parameters
        }
        
        # Initialize metrics for new tool
        if tool_name not in self.success_metrics:
            self.success_metrics[tool_name] = {
                'calls': 0,
                'successes': 0,
                'failures': 0,
                'avg_latency': 0,
                'context_success_map': {}
            }
    
    def select_tool(self, task_context, user_intent, available_data):
        """
        Select the most appropriate tool based on context, intent, and available data.
        
        Args:
            task_context: Current task context including history
            user_intent: Parsed user intent
            available_data: Data available for tool use
            
        Returns:
            Dictionary containing selected tool and parameter recommendations
        """
        # Extract context features
        context_features = self._extract_context_features(task_context)
        
        # Match intent to capabilities
        capability_matches = self._match_capabilities(user_intent)
        
        # Calculate tool scores
        tool_scores = self._score_tools(context_features, capability_matches, available_data)
        
        # Select highest scoring tool
        selected_tool, score = max(tool_scores.items(), key=lambda x: x[1]['total_score'])
        
        # Generate parameter recommendations
        parameter_recommendations = self._generate_parameter_recommendations(
            selected_tool, 
            task_context,
            user_intent,
            available_data
        )
        
        return {
            'tool': selected_tool,
            'confidence': score['total_score'],
            'parameter_recommendations': parameter_recommendations,
            'alternative_tools': self._get_alternative_tools(tool_scores, selected_tool)
        }
    
    def record_tool_result(self, tool_name, context_features, success, latency, error_type=None):
        """
        Record the result of a tool execution to improve future selections.
        
        Args:
            tool_name: Name of the tool that was executed
            context_features: Features of the context when tool was selected
            success: Whether the tool execution was successful
            latency: Execution time in milliseconds
            error_type: Type of error if execution failed
        """
        if tool_name not in self.success_metrics:
            return
            
        # Update basic metrics
        metrics = self.success_metrics[tool_name]
        metrics['calls'] += 1
        
        if success:
            metrics['successes'] += 1
        else:
            metrics['failures'] += 1
            
        # Update average latency with exponential moving average
        if metrics['calls'] == 1:
            metrics['avg_latency'] = latency
        else:
            metrics['avg_latency'] = 0.9 * metrics['avg_latency'] + 0.1 * latency
            
        # Update context success mapping
        context_key = self._get_context_key(context_features)
        if context_key not in metrics['context_success_map']:
            metrics['context_success_map'][context_key] = {
                'attempts': 0,
                'successes': 0,
                'failures': 0
            }
            
        context_metrics = metrics['context_success_map'][context_key]
        context_metrics['attempts'] += 1
        if success:
            context_metrics['successes'] += 1
        else:
            context_metrics['failures'] += 1
            
        # Record error patterns if applicable
        if not success and error_type:
            if 'error_types' not in context_metrics:
                context_metrics['error_types'] = {}
            if error_type not in context_metrics['error_types']:
                context_metrics['error_types'][error_type] = 0
            context_metrics['error_types'][error_type] += 1
    
    def get_tool_statistics(self):
        """
        Get statistics about tool usage and success rates.
        
        Returns:
            Dictionary of tool statistics
        """
        stats = {}
        
        for tool_name, metrics in self.success_metrics.items():
            if metrics['calls'] == 0:
                success_rate = 0
            else:
                success_rate = metrics['successes'] / metrics['calls']
                
            stats[tool_name] = {
                'calls': metrics['calls'],
                'success_rate': success_rate,
                'avg_latency': metrics['avg_latency'],
                'context_patterns': len(metrics['context_success_map'])
            }
            
        return stats
    
    def _extract_context_features(self, task_context):
        """
        Extract relevant features from the task context.
        
        Args:
            task_context: Current task context
            
        Returns:
            Dictionary of context features
        """
        features = {
            'task_type': self._identify_task_type(task_context),
            'recent_tools': self._get_recent_tools(task_context),
            'data_types': self._identify_data_types(task_context),
            'complexity': self._estimate_task_complexity(task_context)
        }
        
        return features
    
    def _identify_task_type(self, task_context):
        """
        Identify the type of task from context.
        
        Args:
            task_context: Current task context
            
        Returns:
            Identified task type
        """
        # Simplified implementation - would use more sophisticated classification
        if 'plan' in task_context and 'current step' in task_context['plan']:
            return task_context['plan'].get('current step', 'unknown')
        return 'general'
    
    def _get_recent_tools(self, task_context):
        """
        Get list of recently used tools from context.
        
        Args:
            task_context: Current task context
            
        Returns:
            List of recently used tools
        """
        recent_tools = []
        
        # Extract tools from recent events
        if 'events' in task_context:
            for event in reversed(task_context['events'][-10:]):
                if event.get('type') == 'action' and 'tool' in event:
                    recent_tools.append(event['tool'])
                    
        return recent_tools[:5]  # Return up to 5 most recent tools
    
    def _identify_data_types(self, task_context):
        """
        Identify types of data available in the context.
        
        Args:
            task_context: Current task context
            
        Returns:
            Set of identified data types
        """
        data_types = set()
        
        # Check for file paths
        if 'files' in task_context:
            data_types.add('file')
            
        # Check for URLs
        if 'urls' in task_context:
            data_types.add('url')
            
        # Check for code
        if 'code' in task_context:
            data_types.add('code')
            
        return data_types
    
    def _estimate_task_complexity(self, task_context):
        """
        Estimate the complexity of the current task.
        
        Args:
            task_context: Current task context
            
        Returns:
            Complexity score (1-5)
        """
        complexity = 1
        
        # Increase complexity based on plan length
        if 'plan' in task_context and 'steps' in task_context['plan']:
            steps = len(task_context['plan']['steps'])
            complexity += min(2, steps // 3)
            
        # Increase complexity based on context size
        if 'events' in task_context:
            events = len(task_context['events'])
            complexity += min(2, events // 20)
            
        return min(5, complexity)
    
    def _match_capabilities(self, user_intent):
        """
        Match user intent to tool capabilities.
        
        Args:
            user_intent: Parsed user intent
            
        Returns:
            Dictionary mapping tools to capability match scores
        """
        matches = {}
        
        for tool_name, tool_info in self.tool_capabilities.items():
            score = 0
            capabilities = tool_info['capabilities']
            
            for intent_key, intent_value in user_intent.items():
                for capability in capabilities:
                    if intent_key in capability:
                        score += 1
                    if intent_value and intent_value in capability:
                        score += 0.5
                        
            matches[tool_name] = score
            
        return matches
    
    def _score_tools(self, context_features, capability_matches, available_data):
        """
        Calculate scores for each tool based on multiple factors.
        
        Args:
            context_features: Features extracted from context
            capability_matches: Capability match scores for each tool
            available_data: Data available for tool use
            
        Returns:
            Dictionary mapping tools to score breakdowns
        """
        scores = {}
        
        for tool_name in self.available_tools:
            # Skip tools with zero capability match
            if tool_name in capability_matches and capability_matches[tool_name] == 0:
                continue
                
            # Initialize score components
            score_components = {
                'capability_match': capability_matches.get(tool_name, 0),
                'historical_success': 0,
                'context_pattern': 0,
                'data_compatibility': 0
            }
            
            # Calculate historical success score
            if tool_name in self.success_metrics:
                metrics = self.success_metrics[tool_name]
                if metrics['calls'] > 0:
                    score_components['historical_success'] = metrics['successes'] / metrics['calls']
                    
            # Calculate context pattern score
            context_key = self._get_context_key(context_features)
            if (tool_name in self.success_metrics and 
                context_key in self.success_metrics[tool_name]['context_success_map']):
                context_metrics = self.success_metrics[tool_name]['context_success_map'][context_key]
                if context_metrics['attempts'] > 0:
                    score_components['context_pattern'] = (
                        context_metrics['successes'] / context_metrics['attempts']
                    ) * min(1, context_metrics['attempts'] / 5)
                    
            # Calculate data compatibility score
            score_components['data_compatibility'] = self._calculate_data_compatibility(
                tool_name, context_features, available_data
            )
            
            # Calculate total score with weights
            total_score = (
                0.3 * score_components['capability_match'] +
                0.3 * score_components['historical_success'] +
                0.3 * score_components['context_pattern'] +
                0.1 * score_components['data_compatibility']
            )
            
            scores[tool_name] = {
                'components': score_components,
                'total_score': total_score
            }
            
        return scores
    
    def _calculate_data_compatibility(self, tool_name, context_features, available_data):
        """
        Calculate compatibility score between available data and tool requirements.
        
        Args:
            tool_name: Name of the tool to evaluate
            context_features: Features extracted from context
            available_data: Data available for tool use
            
        Returns:
            Compatibility score (0-1)
        """
        # Simplified implementation
        if tool_name not in self.tool_capabilities:
            return 0
            
        required_params = self.tool_capabilities[tool_name]['parameters']
        available_params = set(available_data.keys())
        
        # Calculate what percentage of required parameters are available
        if not required_params:
            return 1
            
        matches = sum(1 for param in required_params if param in available_params)
        return matches / len(required_params)
    
    def _generate_parameter_recommendations(self, tool_name, task_context, user_intent, available_data):
        """
        Generate parameter recommendations for the selected tool.
        
        Args:
            tool_name: Name of the selected tool
            task_context: Current task context
            user_intent: Parsed user intent
            available_data: Data available for tool use
            
        Returns:
            Dictionary of parameter recommendations
        """
        if tool_name not in self.tool_capabilities:
            return {}
            
        recommendations = {}
        required_params = self.tool_capabilities[tool_name]['parameters']
        
        for param in required_params:
            # Check if parameter is directly available in data
            if param in available_data:
                recommendations[param] = available_data[param]
                continue
                
            # Try to extract from user intent
            if param in user_intent:
                recommendations[param] = user_intent[param]
                continue
                
            # Try to infer from context
            inferred_value = self._infer_parameter_from_context(param, task_context)
            if inferred_value is not None:
                recommendations[param] = inferred_value
                
        return recommendations
    
    def _infer_parameter_from_context(self, param_name, task_context):
        """
        Attempt to infer parameter value from context.
        
        Args:
            param_name: Name of the parameter to infer
            task_context: Current task context
            
        Returns:
            Inferred parameter value or None
        """
        # Simplified implementation - would use more sophisticated inference
        
        # Check for file paths
        if param_name in ['file', 'path', 'filepath'] and 'files' in task_context:
            return task_context['files'][0] if task_context['files'] else None
            
        # Check for URLs
        if param_name in ['url', 'link'] and 'urls' in task_context:
            return task_context['urls'][0] if task_context['urls'] else None
            
        return None
    
    def _get_context_key(self, context_features):
        """
        Generate a key representing the context features for pattern matching.
        
        Args:
            context_features: Features extracted from context
            
        Returns:
            String key representing context
        """
        task_type = context_features.get('task_type', 'unknown')
        complexity = context_features.get('complexity', 1)
        data_types = ','.join(sorted(context_features.get('data_types', [])))
        
        return f"{task_type}|{complexity}|{data_types}"
    
    def _get_alternative_tools(self, tool_scores, selected_tool, max_alternatives=2):
        """
        Get alternative tools that could also be appropriate.
        
        Args:
            tool_scores: Dictionary of tool scores
            selected_tool: Name of the selected tool
            max_alternatives: Maximum number of alternatives to return
            
        Returns:
            List of alternative tools with scores
        """
        alternatives = []
        
        # Sort tools by score excluding the selected tool
        sorted_tools = sorted(
            [(t, s['total_score']) for t, s in tool_scores.items() if t != selected_tool],
            key=lambda x: x[1],
            reverse=True
        )
        
        # Return top alternatives
        return sorted_tools[:max_alternatives]
