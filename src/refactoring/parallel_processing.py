"""
Parallel Processing System for Manus AI

This module implements task decomposition with parallel subtask execution
to improve performance for complex multi-step tasks.
"""

class ParallelProcessingSystem:
    """
    Manages task decomposition and parallel execution to optimize performance
    for complex multi-step tasks.
    """
    
    def __init__(self, max_parallel_tasks=4):
        """
        Initialize the parallel processing system.
        
        Args:
            max_parallel_tasks: Maximum number of tasks to execute in parallel
        """
        self.max_parallel_tasks = max_parallel_tasks
        self.active_tasks = {}
        self.task_dependencies = {}
        self.task_results = {}
        self.task_queue = []
        self.completed_tasks = set()
        self.failed_tasks = set()
        
    def decompose_task(self, task, subtask_definitions=None):
        """
        Decompose a complex task into subtasks that can be executed in parallel.
        
        Args:
            task: Main task to decompose
            subtask_definitions: Optional predefined subtask structure
            
        Returns:
            Task ID for the decomposed task
        """
        task_id = self._generate_task_id(task)
        
        if subtask_definitions:
            # Use provided subtask definitions
            subtasks = subtask_definitions
        else:
            # Auto-decompose the task
            subtasks = self._auto_decompose_task(task)
            
        # Set up task structure
        self.active_tasks[task_id] = {
            'main_task': task,
            'subtasks': subtasks,
            'status': 'decomposed',
            'progress': 0.0,
            'start_time': self._get_timestamp(),
            'end_time': None
        }
        
        # Set up dependencies
        self.task_dependencies[task_id] = {
            subtask['id']: subtask.get('dependencies', [])
            for subtask in subtasks
        }
        
        # Initialize results
        self.task_results[task_id] = {
            subtask['id']: None for subtask in subtasks
        }
        
        return task_id
    
    def execute_task(self, task_id):
        """
        Begin execution of a decomposed task.
        
        Args:
            task_id: ID of the decomposed task to execute
            
        Returns:
            Initial execution status
        """
        if task_id not in self.active_tasks:
            return {'status': 'error', 'message': 'Task not found'}
            
        task_info = self.active_tasks[task_id]
        
        # Update status
        task_info['status'] = 'executing'
        
        # Identify initial subtasks (those with no dependencies)
        initial_subtasks = []
        for subtask in task_info['subtasks']:
            subtask_id = subtask['id']
            dependencies = self.task_dependencies[task_id][subtask_id]
            
            if not dependencies:
                initial_subtasks.append(subtask)
                
        # Queue initial subtasks
        for subtask in initial_subtasks:
            self._queue_subtask(task_id, subtask)
            
        # Begin execution
        execution_status = self._process_task_queue(task_id)
        
        return execution_status
    
    def get_task_status(self, task_id):
        """
        Get the current status of a task.
        
        Args:
            task_id: ID of the task to check
            
        Returns:
            Current task status
        """
        if task_id not in self.active_tasks:
            return {'status': 'error', 'message': 'Task not found'}
            
        task_info = self.active_tasks[task_id]
        
        # Calculate progress
        total_subtasks = len(task_info['subtasks'])
        completed_subtasks = sum(
            1 for subtask_id in self.task_results[task_id]
            if self.task_results[task_id][subtask_id] is not None
        )
        
        progress = completed_subtasks / total_subtasks if total_subtasks > 0 else 0
        task_info['progress'] = progress
        
        # Check if all subtasks are complete
        if progress == 1.0 and task_info['status'] != 'completed':
            task_info['status'] = 'completed'
            task_info['end_time'] = self._get_timestamp()
            
        return {
            'task_id': task_id,
            'status': task_info['status'],
            'progress': task_info['progress'],
            'start_time': task_info['start_time'],
            'end_time': task_info['end_time'],
            'completed_subtasks': completed_subtasks,
            'total_subtasks': total_subtasks,
            'failed_subtasks': len([
                subtask_id for subtask_id in self.task_results[task_id]
                if subtask_id in self.failed_tasks
            ])
        }
    
    def get_task_results(self, task_id):
        """
        Get the results of a completed task.
        
        Args:
            task_id: ID of the task to get results for
            
        Returns:
            Task results or error
        """
        if task_id not in self.active_tasks:
            return {'status': 'error', 'message': 'Task not found'}
            
        task_info = self.active_tasks[task_id]
        
        if task_info['status'] != 'completed':
            return {
                'status': 'pending',
                'message': f"Task is still {task_info['status']}",
                'progress': task_info['progress']
            }
            
        # Compile results
        results = {
            'task_id': task_id,
            'status': 'completed',
            'execution_time': task_info['end_time'] - task_info['start_time'],
            'subtask_results': self.task_results[task_id],
            'failed_subtasks': [
                subtask_id for subtask_id in self.task_results[task_id]
                if subtask_id in self.failed_tasks
            ]
        }
        
        return results
    
    def cancel_task(self, task_id):
        """
        Cancel a running task.
        
        Args:
            task_id: ID of the task to cancel
            
        Returns:
            Cancellation status
        """
        if task_id not in self.active_tasks:
            return {'status': 'error', 'message': 'Task not found'}
            
        task_info = self.active_tasks[task_id]
        
        if task_info['status'] == 'completed':
            return {'status': 'error', 'message': 'Task already completed'}
            
        # Update status
        task_info['status'] = 'cancelled'
        task_info['end_time'] = self._get_timestamp()
        
        # Remove pending subtasks from queue
        self.task_queue = [
            item for item in self.task_queue
            if item['task_id'] != task_id
        ]
        
        return {
            'status': 'success',
            'message': 'Task cancelled',
            'task_id': task_id
        }
    
    def _auto_decompose_task(self, task):
        """
        Automatically decompose a task into subtasks.
        
        Args:
            task: Task to decompose
            
        Returns:
            List of subtasks
        """
        # This is a simplified implementation
        # In practice, would use more sophisticated task analysis
        
        task_str = str(task)
        subtasks = []
        
        # Check if task contains steps or numbered items
        if 'steps' in task and isinstance(task['steps'], list):
            # Use explicit steps
            for i, step in enumerate(task['steps']):
                subtask_id = f"subtask_{i+1}"
                dependencies = []
                
                # Add dependency on previous step unless specified otherwise
                if i > 0 and step.get('parallel', False) is False:
                    dependencies.append(f"subtask_{i}")
                    
                subtasks.append({
                    'id': subtask_id,
                    'description': step.get('description', f"Step {i+1}"),
                    'action': step.get('action', {}),
                    'dependencies': dependencies
                })
        else:
            # Simple sequential decomposition
            # In practice, would use NLP to identify logical steps
            subtasks = [
                {
                    'id': 'subtask_1',
                    'description': 'Initialize task',
                    'action': {'type': 'initialize', 'params': {}},
                    'dependencies': []
                },
                {
                    'id': 'subtask_2',
                    'description': 'Process main content',
                    'action': {'type': 'process', 'params': {}},
                    'dependencies': ['subtask_1']
                },
                {
                    'id': 'subtask_3',
                    'description': 'Finalize results',
                    'action': {'type': 'finalize', 'params': {}},
                    'dependencies': ['subtask_2']
                }
            ]
            
        return subtasks
    
    def _queue_subtask(self, task_id, subtask):
        """
        Add a subtask to the execution queue.
        
        Args:
            task_id: ID of the parent task
            subtask: Subtask to queue
        """
        self.task_queue.append({
            'task_id': task_id,
            'subtask_id': subtask['id'],
            'subtask': subtask,
            'queued_time': self._get_timestamp()
        })
    
    def _process_task_queue(self, task_id=None):
        """
        Process the task queue, executing subtasks in parallel.
        
        Args:
            task_id: Optional task ID to process subtasks for
            
        Returns:
            Execution status
        """
        # Filter queue for specific task if provided
        queue_to_process = self.task_queue
        if task_id:
            queue_to_process = [
                item for item in self.task_queue
                if item['task_id'] == task_id
            ]
            
        # Execute up to max_parallel_tasks
        executed = []
        for i, queue_item in enumerate(queue_to_process[:self.max_parallel_tasks]):
            task_id = queue_item['task_id']
            subtask_id = queue_item['subtask_id']
            subtask = queue_item['subtask']
            
            # Execute subtask
            try:
                result = self._execute_subtask(subtask)
                self.task_results[task_id][subtask_id] = result
                self.completed_tasks.add(subtask_id)
                
                # Queue dependent subtasks
                self._queue_dependent_subtasks(task_id, subtask_id)
            except Exception as e:
                self.failed_tasks.add(subtask_id)
                self.task_results[task_id][subtask_id] = {
                    'status': 'error',
                    'error': str(e)
                }
                
            executed.append(queue_item)
            
        # Remove executed items from queue
        for item in executed:
            self.task_queue.remove(item)
            
        return {
            'status': 'executing',
            'queued': len(self.task_queue),
            'executed': len(executed)
        }
    
    def _execute_subtask(self, subtask):
        """
        Execute a single subtask.
        
        Args:
            subtask: Subtask to execute
            
        Returns:
            Subtask execution result
        """
        # This is a simplified implementation
        # In practice, would dispatch to appropriate execution mechanism
        
        action = subtask.get('action', {})
        action_type = action.get('type', 'unknown')
        
        # Simulate execution
        import time
        time.sleep(0.1)  # Simulate processing time
        
        return {
            'status': 'completed',
            'result': f"Executed {action_type} action",
            'execution_time': 0.1
        }
    
    def _queue_dependent_subtasks(self, task_id, completed_subtask_id):
        """
        Queue subtasks that depend on a completed subtask.
        
        Args:
            task_id: ID of the parent task
            completed_subtask_id: ID of the completed subtask
        """
        task_info = self.active_tasks[task_id]
        
        for subtask in task_info['subtasks']:
            subtask_id = subtask['id']
            dependencies = self.task_dependencies[task_id][subtask_id]
            
            # Skip if already completed or queued
            if (subtask_id in self.completed_tasks or
                subtask_id in self.failed_tasks or
                any(item['subtask_id'] == subtask_id for item in self.task_queue)):
                continue
                
            # Check if all dependencies are satisfied
            if all(dep in self.completed_tasks for dep in dependencies):
                self._queue_subtask(task_id, subtask)
    
    def _generate_task_id(self, task):
        """
        Generate a unique ID for a task.
        
        Args:
            task: Task to generate ID for
            
        Returns:
            Unique task ID
        """
        import hashlib
        import json
        
        # Create deterministic representation of task
        if isinstance(task, dict):
            task_str = json.dumps(task, sort_keys=True)
        else:
            task_str = str(task)
            
        # Generate hash
        task_hash = hashlib.md5(task_str.encode()).hexdigest()[:8]
        
        # Add timestamp for uniqueness
        timestamp = self._get_timestamp()
        
        return f"task_{timestamp}_{task_hash}"
    
    def _get_timestamp(self):
        """
        Get current timestamp.
        
        Returns:
            Current timestamp
        """
        import time
        return int(time.time())
