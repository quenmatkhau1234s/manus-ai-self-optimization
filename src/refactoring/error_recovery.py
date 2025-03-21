"""
Error Recovery Mechanisms for Manus AI

This module implements predictive error detection and automated recovery strategies
to improve resilience and reduce user intervention requirements.
"""

class ErrorRecoverySystem:
    """
    Manages error detection, prediction, and recovery to enhance system resilience
    and reduce the need for user intervention during failures.
    """
    
    def __init__(self):
        """Initialize the error recovery system with default configuration."""
        self.error_patterns = {}
        self.recovery_strategies = {}
        self.error_history = []
        self.active_recoveries = {}
        self.max_history_size = 100
        self.max_recovery_attempts = 3
        
    def register_error_pattern(self, error_type, pattern, severity, recovery_strategy=None):
        """
        Register an error pattern with optional recovery strategy.
        
        Args:
            error_type: Type identifier for the error
            pattern: Pattern to match for error detection
            severity: Severity level (1-5, with 5 being most severe)
            recovery_strategy: Function or strategy name for recovery
        """
        self.error_patterns[error_type] = {
            'pattern': pattern,
            'severity': severity,
            'recovery_strategy': recovery_strategy,
            'occurrences': 0,
            'successful_recoveries': 0
        }
        
    def register_recovery_strategy(self, strategy_name, strategy_function, applicable_errors=None):
        """
        Register a recovery strategy for specific error types.
        
        Args:
            strategy_name: Unique identifier for the strategy
            strategy_function: Function implementing the recovery strategy
            applicable_errors: List of error types this strategy can handle
        """
        self.recovery_strategies[strategy_name] = {
            'function': strategy_function,
            'applicable_errors': applicable_errors or [],
            'success_rate': 0,
            'attempts': 0,
            'successes': 0
        }
        
    def detect_error(self, operation_result, operation_context):
        """
        Detect errors in operation results based on registered patterns.
        
        Args:
            operation_result: Result of the operation to check for errors
            operation_context: Context in which the operation was performed
            
        Returns:
            Detected error information or None if no error detected
        """
        result_str = str(operation_result)
        
        for error_type, error_info in self.error_patterns.items():
            pattern = error_info['pattern']
            
            # Check if pattern matches
            if pattern in result_str:
                # Update occurrence count
                self.error_patterns[error_type]['occurrences'] += 1
                
                # Create error record
                error = {
                    'type': error_type,
                    'severity': error_info['severity'],
                    'context': operation_context,
                    'result': operation_result,
                    'timestamp': self._get_timestamp(),
                    'recovery_strategy': error_info['recovery_strategy']
                }
                
                # Add to history
                self._add_to_history(error)
                
                return error
                
        return None
    
    def predict_potential_errors(self, planned_operation, operation_context):
        """
        Predict potential errors before operation execution.
        
        Args:
            planned_operation: Description of the operation to be performed
            operation_context: Context in which the operation will be performed
            
        Returns:
            List of potential errors with probabilities
        """
        potential_errors = []
        operation_str = str(planned_operation)
        
        # Check for similar operations in error history
        similar_operations = self._find_similar_operations(planned_operation, operation_context)
        
        # Calculate error probabilities based on history
        error_probabilities = self._calculate_error_probabilities(similar_operations)
        
        # Add high-probability errors to the result
        for error_type, probability in error_probabilities.items():
            if probability > 0.2:  # Only include errors with >20% probability
                potential_errors.append({
                    'type': error_type,
                    'probability': probability,
                    'severity': self.error_patterns[error_type]['severity'],
                    'recovery_strategy': self.error_patterns[error_type]['recovery_strategy']
                })
                
        return potential_errors
    
    def attempt_recovery(self, error, operation_context):
        """
        Attempt to recover from an error.
        
        Args:
            error: Error information
            operation_context: Context in which the error occurred
            
        Returns:
            Recovery result with success status and actions taken
        """
        error_type = error['type']
        
        # Check if we've exceeded max recovery attempts for this error
        error_id = f"{error_type}_{self._get_timestamp()}"
        if error_id in self.active_recoveries:
            if self.active_recoveries[error_id]['attempts'] >= self.max_recovery_attempts:
                return {
                    'success': False,
                    'error': error,
                    'actions': [],
                    'message': f"Exceeded maximum recovery attempts ({self.max_recovery_attempts})"
                }
            self.active_recoveries[error_id]['attempts'] += 1
        else:
            self.active_recoveries[error_id] = {'attempts': 1}
        
        # Get recovery strategy
        strategy_name = error.get('recovery_strategy')
        if not strategy_name or strategy_name not in self.recovery_strategies:
            # Find alternative strategy if none specified
            strategy_name = self._find_best_recovery_strategy(error_type)
            
        if not strategy_name:
            return {
                'success': False,
                'error': error,
                'actions': [],
                'message': "No suitable recovery strategy found"
            }
            
        # Execute recovery strategy
        strategy = self.recovery_strategies[strategy_name]
        strategy['attempts'] += 1
        
        try:
            recovery_result = strategy['function'](error, operation_context)
            
            # Update success statistics
            if recovery_result.get('success', False):
                strategy['successes'] += 1
                self.error_patterns[error_type]['successful_recoveries'] += 1
                
            # Update success rate
            strategy['success_rate'] = strategy['successes'] / strategy['attempts']
            
            return recovery_result
        except Exception as e:
            return {
                'success': False,
                'error': error,
                'actions': [],
                'message': f"Recovery strategy failed: {str(e)}"
            }
    
    def get_error_statistics(self):
        """
        Get statistics about errors and recovery strategies.
        
        Returns:
            Dictionary of error and recovery statistics
        """
        # Calculate error statistics
        error_stats = {}
        for error_type, error_info in self.error_patterns.items():
            occurrences = error_info['occurrences']
            recoveries = error_info['successful_recoveries']
            
            error_stats[error_type] = {
                'occurrences': occurrences,
                'successful_recoveries': recoveries,
                'recovery_rate': recoveries / occurrences if occurrences > 0 else 0,
                'severity': error_info['severity']
            }
            
        # Calculate recovery statistics
        recovery_stats = {}
        for strategy_name, strategy_info in self.recovery_strategies.items():
            recovery_stats[strategy_name] = {
                'attempts': strategy_info['attempts'],
                'successes': strategy_info['successes'],
                'success_rate': strategy_info['success_rate'],
                'applicable_errors': strategy_info['applicable_errors']
            }
            
        return {
            'errors': error_stats,
            'recovery_strategies': recovery_stats,
            'total_errors': sum(info['occurrences'] for info in self.error_patterns.values()),
            'total_recoveries': sum(info['successful_recoveries'] for info in self.error_patterns.values())
        }
    
    def _add_to_history(self, error):
        """
        Add an error to the history, maintaining maximum size.
        
        Args:
            error: Error information to add
        """
        self.error_history.append(error)
        
        # Trim history if needed
        if len(self.error_history) > self.max_history_size:
            self.error_history = self.error_history[-self.max_history_size:]
    
    def _find_similar_operations(self, planned_operation, operation_context):
        """
        Find similar operations in error history.
        
        Args:
            planned_operation: Operation to find similar ones for
            operation_context: Context of the planned operation
            
        Returns:
            List of similar operations from history
        """
        operation_str = str(planned_operation)
        similar_operations = []
        
        for error in self.error_history:
            # Check for similarity in operation description
            if 'context' in error and 'operation' in error['context']:
                history_operation = str(error['context']['operation'])
                
                # Simple string similarity check
                if self._calculate_string_similarity(operation_str, history_operation) > 0.7:
                    similar_operations.append(error)
                    
        return similar_operations
    
    def _calculate_error_probabilities(self, similar_operations):
        """
        Calculate error probabilities based on similar operations.
        
        Args:
            similar_operations: List of similar operations from history
            
        Returns:
            Dictionary mapping error types to probabilities
        """
        if not similar_operations:
            return {}
            
        # Count occurrences of each error type
        error_counts = {}
        for error in similar_operations:
            error_type = error['type']
            if error_type not in error_counts:
                error_counts[error_type] = 0
            error_counts[error_type] += 1
            
        # Calculate probabilities
        total_operations = len(similar_operations)
        probabilities = {
            error_type: count / total_operations
            for error_type, count in error_counts.items()
        }
        
        return probabilities
    
    def _find_best_recovery_strategy(self, error_type):
        """
        Find the best recovery strategy for an error type.
        
        Args:
            error_type: Type of error to find strategy for
            
        Returns:
            Name of the best recovery strategy or None
        """
        applicable_strategies = []
        
        for strategy_name, strategy_info in self.recovery_strategies.items():
            if error_type in strategy_info['applicable_errors']:
                applicable_strategies.append((
                    strategy_name,
                    strategy_info['success_rate']
                ))
                
        if not applicable_strategies:
            return None
            
        # Sort by success rate (descending)
        applicable_strategies.sort(key=lambda x: x[1], reverse=True)
        
        return applicable_strategies[0][0]
    
    def _calculate_string_similarity(self, str1, str2):
        """
        Calculate similarity between two strings.
        
        Args:
            str1: First string
            str2: Second string
            
        Returns:
            Similarity score (0-1)
        """
        # Simple implementation using Jaccard similarity of word sets
        words1 = set(str1.lower().split())
        words2 = set(str2.lower().split())
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        if union == 0:
            return 0
            
        return intersection / union
    
    def _get_timestamp(self):
        """
        Get current timestamp.
        
        Returns:
            Current timestamp string
        """
        import time
        return int(time.time())
