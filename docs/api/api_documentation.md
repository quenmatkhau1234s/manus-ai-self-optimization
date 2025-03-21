# Manus AI API Documentation

## Overview

This document provides comprehensive API documentation for the optimized Manus AI system. It covers the five core components implemented as part of the self-optimization project:

1. Context Management System
2. Tool Selection Algorithm
3. Knowledge Retrieval System
4. Error Recovery Mechanisms
5. Parallel Processing System

Each section includes class and method definitions, parameters, return values, and usage examples.

## Table of Contents

- [Context Management System](#context-management-system)
- [Tool Selection Algorithm](#tool-selection-algorithm)
- [Knowledge Retrieval System](#knowledge-retrieval-system)
- [Error Recovery Mechanisms](#error-recovery-mechanisms)
- [Parallel Processing System](#parallel-processing-system)
- [Integration Examples](#integration-examples)

## Context Management System

The Context Management System implements hierarchical context summarization to improve long-term memory capabilities while maintaining processing efficiency.

### Class: `ContextManager`

#### Constructor

```python
def __init__(self, max_context_size=10000, summarization_threshold=0.8)
```

**Parameters:**
- `max_context_size` (int): Maximum number of tokens to maintain in active context
- `summarization_threshold` (float): Threshold at which summarization is triggered (0.0-1.0)

**Example:**
```python
from manus_ai.context_manager import ContextManager

# Initialize with custom parameters
context_manager = ContextManager(
    max_context_size=15000,
    summarization_threshold=0.7
)
```

#### Method: `add_event`

```python
def add_event(self, event, importance=1.0)
```

**Parameters:**
- `event` (dict): The event to add to context
- `importance` (float): Importance score (0.0-1.0) affecting retention priority

**Example:**
```python
# Add a user message event with high importance
event = {
    'id': 'msg_123',
    'type': 'message',
    'source': 'user',
    'date': '2025-03-21T11:30:00Z',
    'payload': 'Important user instruction'
}
context_manager.add_event(event, importance=0.9)
```

#### Method: `get_full_context`

```python
def get_full_context(self)
```

**Returns:**
- Dictionary containing active context, summarized context, and metadata

**Example:**
```python
# Retrieve the full context
full_context = context_manager.get_full_context()
print(f"Active events: {len(full_context['active_context'])}")
print(f"Summarized sections: {len(full_context['summarized_context'])}")
print(f"Total events processed: {full_context['total_events_processed']}")
```

#### Method: `get_relevant_context`

```python
def get_relevant_context(self, query, max_items=10)
```

**Parameters:**
- `query` (str): The query to match against context
- `max_items` (int): Maximum number of items to return

**Returns:**
- List of most relevant context items

**Example:**
```python
# Retrieve context relevant to a specific query
relevant_items = context_manager.get_relevant_context(
    query="file processing operations",
    max_items=5
)

for item in relevant_items:
    print(f"Relevant item: {item['type']} - {item.get('payload', '')[:50]}...")
```

## Tool Selection Algorithm

The Tool Selection Algorithm uses historical success patterns to improve tool selection accuracy and efficiency.

### Class: `ToolSelector`

#### Constructor

```python
def __init__(self)
```

**Example:**
```python
from manus_ai.tool_selector import ToolSelector

# Initialize the tool selector
tool_selector = ToolSelector()
```

#### Method: `register_tool`

```python
def register_tool(self, tool_name, capabilities, parameters)
```

**Parameters:**
- `tool_name` (str): Unique identifier for the tool
- `capabilities` (list): List of capabilities provided by the tool
- `parameters` (dict): Dictionary of parameters accepted by the tool

**Example:**
```python
# Register a file reading tool
tool_selector.register_tool(
    "file_read",
    ["read file", "access file content", "view file"],
    {"file": "string", "start_line": "integer", "end_line": "integer"}
)
```

#### Method: `select_tool`

```python
def select_tool(self, task_context, user_intent, available_data)
```

**Parameters:**
- `task_context` (dict): Current task context including history
- `user_intent` (dict): Parsed user intent
- `available_data` (dict): Data available for tool use

**Returns:**
- Dictionary containing selected tool and parameter recommendations

**Example:**
```python
# Select the most appropriate tool for a task
task_context = {
    "events": [
        {"type": "message", "source": "user", "payload": "I need to read a file"}
    ]
}

user_intent = {
    "action": "read",
    "object": "file",
    "path": "/home/user/document.txt"
}

available_data = {
    "file": "/home/user/document.txt"
}

result = tool_selector.select_tool(task_context, user_intent, available_data)
print(f"Selected tool: {result['tool']}")
print(f"Confidence: {result['confidence']}")
print(f"Parameter recommendations: {result['parameter_recommendations']}")
```

#### Method: `record_tool_result`

```python
def record_tool_result(self, tool_name, context_features, success, latency, error_type=None)
```

**Parameters:**
- `tool_name` (str): Name of the tool that was executed
- `context_features` (dict): Features of the context when tool was selected
- `success` (bool): Whether the tool execution was successful
- `latency` (float): Execution time in milliseconds
- `error_type` (str, optional): Type of error if execution failed

**Example:**
```python
# Record the result of a tool execution
context_features = {
    "task_type": "read_file",
    "recent_tools": ["file_list"],
    "data_types": {"file"},
    "complexity": 1
}

tool_selector.record_tool_result(
    "file_read",
    context_features,
    success=True,
    latency=120
)
```

#### Method: `get_tool_statistics`

```python
def get_tool_statistics(self)
```

**Returns:**
- Dictionary of tool usage statistics

**Example:**
```python
# Get statistics about tool usage
stats = tool_selector.get_tool_statistics()

for tool_name, tool_stats in stats.items():
    print(f"Tool: {tool_name}")
    print(f"  Calls: {tool_stats['calls']}")
    print(f"  Success rate: {tool_stats['success_rate']:.2f}")
    print(f"  Avg latency: {tool_stats['avg_latency']:.2f}ms")
```

## Knowledge Retrieval System

The Knowledge Retrieval System implements semantic indexing and vector-based retrieval to improve the relevance and efficiency of knowledge retrieval.

### Class: `KnowledgeRetrievalSystem`

#### Constructor

```python
def __init__(self, dimensions=128, index_refresh_threshold=50)
```

**Parameters:**
- `dimensions` (int): Dimensionality of vector embeddings
- `index_refresh_threshold` (int): Number of updates before index refresh

**Example:**
```python
from manus_ai.knowledge_retrieval import KnowledgeRetrievalSystem

# Initialize with custom parameters
knowledge_system = KnowledgeRetrievalSystem(
    dimensions=256,
    index_refresh_threshold=100
)
```

#### Method: `add_knowledge_item`

```python
def add_knowledge_item(self, item_id, content, metadata=None, embedding=None)
```

**Parameters:**
- `item_id` (str): Unique identifier for the knowledge item
- `content` (str): Text content of the knowledge item
- `metadata` (dict, optional): Additional metadata for the knowledge item
- `embedding` (list, optional): Pre-computed embedding vector

**Example:**
```python
# Add a knowledge item
knowledge_system.add_knowledge_item(
    "python_basics",
    "Python is a high-level, interpreted programming language known for its readability and simplicity.",
    {"type": "language", "category": "programming"}
)
```

#### Method: `retrieve_knowledge`

```python
def retrieve_knowledge(self, query, max_results=5, threshold=0.6)
```

**Parameters:**
- `query` (str): Search query text
- `max_results` (int): Maximum number of results to return
- `threshold` (float): Minimum relevance score threshold

**Returns:**
- List of relevant knowledge items with scores

**Example:**
```python
# Retrieve knowledge relevant to a query
results = knowledge_system.retrieve_knowledge(
    "How do I use Python for data analysis?",
    max_results=3,
    threshold=0.5
)

for result in results:
    print(f"Result: {result['id']}")
    print(f"  Score: {result['combined_score']:.2f}")
    print(f"  Content: {result['content'][:100]}...")
```

#### Method: `get_related_knowledge`

```python
def get_related_knowledge(self, item_id, max_results=5)
```

**Parameters:**
- `item_id` (str): ID of the knowledge item to find related items for
- `max_results` (int): Maximum number of results to return

**Returns:**
- List of related knowledge items with similarity scores

**Example:**
```python
# Get knowledge items related to a specific item
related_items = knowledge_system.get_related_knowledge(
    "python_basics",
    max_results=3
)

for item in related_items:
    print(f"Related item: {item['id']}")
    print(f"  Similarity: {item['similarity']:.2f}")
    print(f"  Content: {item['content'][:100]}...")
```

#### Method: `remove_knowledge_item`

```python
def remove_knowledge_item(self, item_id)
```

**Parameters:**
- `item_id` (str): ID of the knowledge item to remove

**Example:**
```python
# Remove a knowledge item
knowledge_system.remove_knowledge_item("outdated_concept")
```

#### Method: `update_knowledge_item`

```python
def update_knowledge_item(self, item_id, content=None, metadata=None)
```

**Parameters:**
- `item_id` (str): ID of the knowledge item to update
- `content` (str, optional): New content
- `metadata` (dict, optional): New metadata

**Example:**
```python
# Update a knowledge item
knowledge_system.update_knowledge_item(
    "python_basics",
    content="Updated information about Python programming language.",
    metadata={"type": "language", "category": "programming", "updated": "2025-03-21"}
)
```

#### Method: `get_knowledge_statistics`

```python
def get_knowledge_statistics(self)
```

**Returns:**
- Dictionary of statistics about the knowledge store

**Example:**
```python
# Get statistics about the knowledge store
stats = knowledge_system.get_knowledge_statistics()

print(f"Total items: {stats['total_items']}")
print(f"Type distribution: {stats['type_distribution']}")
print(f"Needs reindexing: {stats['needs_reindexing']}")
```

## Error Recovery Mechanisms

The Error Recovery System implements predictive error detection and automated recovery strategies to improve resilience and reduce user intervention requirements.

### Class: `ErrorRecoverySystem`

#### Constructor

```python
def __init__(self)
```

**Example:**
```python
from manus_ai.error_recovery import ErrorRecoverySystem

# Initialize the error recovery system
recovery_system = ErrorRecoverySystem()
```

#### Method: `register_error_pattern`

```python
def register_error_pattern(self, error_type, pattern, severity, recovery_strategy=None)
```

**Parameters:**
- `error_type` (str): Type identifier for the error
- `pattern` (str): Pattern to match for error detection
- `severity` (int): Severity level (1-5, with 5 being most severe)
- `recovery_strategy` (str, optional): Strategy name for recovery

**Example:**
```python
# Register an error pattern
recovery_system.register_error_pattern(
    "file_not_found",
    "No such file or directory",
    severity=3,
    recovery_strategy="create_file"
)
```

#### Method: `register_recovery_strategy`

```python
def register_recovery_strategy(self, strategy_name, strategy_function, applicable_errors=None)
```

**Parameters:**
- `strategy_name` (str): Unique identifier for the strategy
- `strategy_function` (callable): Function implementing the recovery strategy
- `applicable_errors` (list, optional): List of error types this strategy can handle

**Example:**
```python
# Define a recovery strategy function
def create_file_strategy(error, context):
    file_path = context.get('file_path', '/tmp/default.txt')
    # Implementation to create the file
    return {
        'success': True,
        'error': error,
        'actions': [f"Created file {file_path}"],
        'message': "File created successfully"
    }

# Register the recovery strategy
recovery_system.register_recovery_strategy(
    "create_file",
    create_file_strategy,
    ["file_not_found"]
)
```

#### Method: `detect_error`

```python
def detect_error(self, operation_result, operation_context)
```

**Parameters:**
- `operation_result` (any): Result of the operation to check for errors
- `operation_context` (dict): Context in which the operation was performed

**Returns:**
- Detected error information or None if no error detected

**Example:**
```python
# Check an operation result for errors
operation_result = "Error: No such file or directory: /home/user/missing_file.txt"
operation_context = {
    "operation": "read_file",
    "file_path": "/home/user/missing_file.txt"
}

error = recovery_system.detect_error(operation_result, operation_context)
if error:
    print(f"Detected error: {error['type']}")
    print(f"Severity: {error['severity']}")
    print(f"Recovery strategy: {error['recovery_strategy']}")
```

#### Method: `predict_potential_errors`

```python
def predict_potential_errors(self, planned_operation, operation_context)
```

**Parameters:**
- `planned_operation` (str): Description of the operation to be performed
- `operation_context` (dict): Context in which the operation will be performed

**Returns:**
- List of potential errors with probabilities

**Example:**
```python
# Predict potential errors before executing an operation
planned_operation = "read_file"
operation_context = {
    "operation": "read_file",
    "file_path": "/home/user/restricted_file.txt"
}

potential_errors = recovery_system.predict_potential_errors(
    planned_operation,
    operation_context
)

for error in potential_errors:
    print(f"Potential error: {error['type']}")
    print(f"  Probability: {error['probability']:.2f}")
    print(f"  Severity: {error['severity']}")
```

#### Method: `attempt_recovery`

```python
def attempt_recovery(self, error, operation_context)
```

**Parameters:**
- `error` (dict): Error information
- `operation_context` (dict): Context in which the error occurred

**Returns:**
- Recovery result with success status and actions taken

**Example:**
```python
# Attempt to recover from an error
if error:
    recovery_result = recovery_system.attempt_recovery(error, operation_context)
    
    if recovery_result['success']:
        print("Recovery successful!")
        print(f"Actions taken: {recovery_result['actions']}")
        print(f"Message: {recovery_result['message']}")
    else:
        print("Recovery failed.")
        print(f"Reason: {recovery_result['message']}")
```

#### Method: `get_error_statistics`

```python
def get_error_statistics(self)
```

**Returns:**
- Dictionary of error and recovery statistics

**Example:**
```python
# Get statistics about errors and recovery strategies
stats = recovery_system.get_error_statistics()

print(f"Total errors: {stats['total_errors']}")
print(f"Total recoveries: {stats['total_recoveries']}")

for error_type, error_stats in stats['errors'].items():
    print(f"Error type: {error_type}")
    print(f"  Occurrences: {error_stats['occurrences']}")
    print(f"  Recovery rate: {error_stats['recovery_rate']:.2f}")
```

## Parallel Processing System

The Parallel Processing System implements task decomposition with parallel subtask execution to improve performance for complex multi-step tasks.

### Class: `ParallelProcessingSystem`

#### Constructor

```python
def __init__(self, max_parallel_tasks=4)
```

**Parameters:**
- `max_parallel_tasks` (int): Maximum number of tasks to execute in parallel

**Example:**
```python
from manus_ai.parallel_processing import ParallelProcessingSystem

# Initialize with custom parameters
parallel_system = ParallelProcessingSystem(max_parallel_tasks=8)
```

#### Method: `decompose_task`

```python
def decompose_task(self, task, subtask_definitions=None)
```

**Parameters:**
- `task` (dict): Main task to decompose
- `subtask_definitions` (list, optional): Predefined subtask structure

**Returns:**
- Task ID for the decomposed task

**Example:**
```python
# Decompose a task automatically
task = {
    "name": "Generate report",
    "description": "Generate a comprehensive report from multiple data sources"
}

task_id = parallel_system.decompose_task(task)
print(f"Task decomposed with ID: {task_id}")

# Decompose a task with custom subtask definitions
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
        "id": "generate_report",
        "description": "Generate final report",
        "action": {"type": "generate", "params": {"format": "pdf"}},
        "dependencies": ["analyze_data"]
    }
]

task_id = parallel_system.decompose_task(task, subtask_definitions)
```

#### Method: `execute_task`

```python
def execute_task(self, task_id)
```

**Parameters:**
- `task_id` (str): ID of the decomposed task to execute

**Returns:**
- Initial execution status

**Example:**
```python
# Execute a decomposed task
execution_status = parallel_system.execute_task(task_id)
print(f"Execution status: {execution_status['status']}")
print(f"Queued subtasks: {execution_status['queued']}")
print(f"Executed subtasks: {execution_status['executed']}")
```

#### Method: `get_task_status`

```python
def get_task_status(self, task_id)
```

**Parameters:**
- `task_id` (str): ID of the task to check

**Returns:**
- Current task status

**Example:**
```python
# Check the status of a task
status = parallel_system.get_task_status(task_id)
print(f"Task status: {status['status']}")
print(f"Progress: {status['progress']:.2f}")
print(f"Completed subtasks: {status['completed_subtasks']}/{status['total_subtasks']}")
```

#### Method: `get_task_results`

```python
def get_task_results(self, task_id)
```

**Parameters:**
- `task_id` (str): ID of the task to get results for

**Returns:**
- Task results or error

**Example:**
```python
# Get the results of a completed task
results = parallel_system.get_task_results(task_id)

if results['status'] == 'completed':
    print(f"Task completed in {results['execution_time']} seconds")
    print("Subtask results:")
    for subtask_id, result in results['subtask_results'].items():
        print(f"  {subtask_id}: {result['status']}")
else:
    print(f"Task is still {results['status']}")
    print(f"Progress: {results.get('progress', 0):.2f}")
```

#### Method: `cancel_task`

```python
def cancel_task(self, task_id)
```

**Parameters:**
- `task_id` (str): ID of the task to cancel

**Returns:**
- Cancellation status

**Example:**
```python
# Cancel a running task
cancel_result = parallel_system.cancel_task(task_id)
print(f"Cancellation status: {cancel_result['status']}")
print(f"Message: {cancel_result['message']}")
```

## Integration Examples

### Example 1: Processing User Requests with Error Recovery

```python
from manus_ai.context_manager import ContextManager
from manus_ai.tool_selector import ToolSelector
from manus_ai.error_recovery import ErrorRecoverySystem

# Initialize components
context_manager = ContextManager()
tool_selector = ToolSelector()
recovery_system = ErrorRecoverySystem()

# Register tools and error patterns
tool_selector.register_tool(
    "file_read",
    ["read file", "access file content", "view file"],
    {"file": "string"}
)

recovery_system.register_error_pattern(
    "file_not_found",
    "No such file or directory",
    severity=3,
    recovery_strategy="create_file"
)

# Define recovery strategy
def create_file_strategy(error, context):
    file_path = context.get('file_path')
    # Implementation to create the file
    return {
        'success': True,
        'error': error,
        'actions': [f"Created file {file_path}"],
        'message': "File created successfully"
    }

recovery_system.register_recovery_strategy(
    "create_file",
    create_file_strategy,
    ["file_not_found"]
)

# Process user request
def process_user_request(user_message):
    # Add to context
    event = {
        'id': f"msg_{int(time.time())}",
        'type': 'message',
        'source': 'user',
        'date': time.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'payload': user_message
    }
    context_manager.add_event(event)
    
    # Parse user intent (simplified)
    user_intent = {
        "action": "read",
        "object": "file",
        "path": "/home/user/document.txt"
    }
    
    # Get relevant context
    task_context = {
        "events": context_manager.get_relevant_context(user_message)
    }
    
    # Select tool
    available_data = {"file": user_intent["path"]}
    tool_result = tool_selector.select_tool(task_context, user_intent, available_data)
    
    # Execute tool (simplified)
    try:
        result = execute_tool(tool_result['tool'], tool_result['parameter_recommendations'])
        
        # Check for errors
        error = recovery_system.detect_error(result, {"file_path": user_intent["path"]})
        if error:
            # Attempt recovery
            recovery_result = recovery_system.attempt_recovery(error, {"file_path": user_intent["path"]})
            if recovery_result['success']:
                # Retry after recovery
                result = execute_tool(tool_result['tool'], tool_result['parameter_recommendations'])
                
        return result
    except Exception as e:
        return f"Error: {str(e)}"

# Simplified tool execution
def execute_tool(tool_name, parameters):
    # Implementation would call actual tool
    return f"Executed {tool_name} with parameters {parameters}"
```

### Example 2: Knowledge Retrieval with Parallel Processing

```python
from manus_ai.knowledge_retrieval import KnowledgeRetrievalSystem
from manus_ai.parallel_processing import ParallelProcessingSystem

# Initialize components
knowledge_system = KnowledgeRetrievalSystem()
parallel_system = ParallelProcessingSystem()

# Add knowledge items
knowledge_items = [
    {
        "id": "python_basics",
        "content": "Python is a high-level programming language...",
        "metadata": {"type": "language", "category": "programming"}
    },
    {
        "id": "data_analysis",
        "content": "Data analysis is the process of inspecting and modeling data...",
        "metadata": {"type": "concept", "category": "data_science"}
    },
    {
        "id": "machine_learning",
        "content": "Machine learning is a subset of artificial intelligence...",
        "metadata": {"type": "concept", "category": "ai"}
    }
]

for item in knowledge_items:
    knowledge_system.add_knowledge_item(item["id"], item["content"], item["metadata"])

# Define a complex research task
research_task = {
    "name": "Research Report",
    "description": "Generate a comprehensive research report on AI programming",
    "query": "Python programming for artificial intelligence and machine learning"
}

# Define subtasks for parallel processing
subtask_definitions = [
    {
        "id": "retrieve_knowledge",
        "description": "Retrieve relevant knowledge",
        "action": {"type": "retrieve", "params": {"query": research_task["query"]}},
        "dependencies": []
    },
    {
        "id": "analyze_content",
        "description": "Analyze retrieved content",
        "action": {"type": "analyze", "params": {}},
        "dependencies": ["retrieve_knowledge"]
    },
    {
        "id": "generate_outline",
        "description": "Generate report outline",
        "action": {"type": "outline", "params": {}},
        "dependencies": ["analyze_content"]
    },
    {
        "id": "write_sections",
        "description": "Write report sections",
        "action": {"type": "write", "params": {}},
        "dependencies": ["generate_outline"]
    },
    {
        "id": "compile_report",
        "description": "Compile final report",
        "action": {"type": "compile", "params": {}},
        "dependencies": ["write_sections"]
    }
]

# Decompose and execute the task
task_id = parallel_system.decompose_task(research_task, subtask_definitions)
parallel_system.execute_task(task_id)

# Monitor task progress
while True:
    status = parallel_system.get_task_status(task_id)
    print(f"Task progress: {status['progress']:.2f}")
    
    if status['status'] in ['completed', 'failed', 'cancelled']:
        break
        
    time.sleep(1)

# Get task results
results = parallel_system.get_task_results(task_id)
if results['status'] == 'completed':
    print("Research task completed successfully")
    # Process results
else:
    print(f"Research task failed: {results.get('message', 'Unknown error')}")
```
