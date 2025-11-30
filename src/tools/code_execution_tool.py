"""Code execution tool for running Python snippets safely."""
import sys
from io import StringIO
from typing import Dict, Any
from config.logging_config import logger
import contextlib


class CodeExecutionTool:
    """Tool for executing Python code safely."""
    
    def __init__(self):
        self.name = "code_execution"
        self.description = "Execute Python code snippets"
        self.allowed_imports = [
            'math', 'datetime', 'json', 'statistics', 
            'collections', 'itertools', 're'
        ]
    
    def execute(self, code: str) -> Dict[str, Any]:
        """
        Execute Python code in a restricted environment.
        
        WARNING: This is a simplified implementation for demo purposes.
        In production, use proper sandboxing like:
        - Docker containers
        - PyPy sandbox
        - AWS Lambda
        - Google Cloud Functions
        """
        logger.info(f"Executing code: {code[:100]}...")
        
        # Capture output
        output_buffer = StringIO()
        error_buffer = StringIO()
        
        try:
            # Create restricted namespace
            namespace = {
                '__builtins__': {
                    'print': print,
                    'len': len,
                    'range': range,
                    'sum': sum,
                    'min': min,
                    'max': max,
                    'abs': abs,
                    'round': round,
                    'sorted': sorted,
                    'str': str,
                    'int': int,
                    'float': float,
                    'list': list,
                    'dict': dict,
                    'set': set,
                    'tuple': tuple,
                }
            }
            
            # Allow safe imports
            for module in self.allowed_imports:
                try:
                    namespace[module] = __import__(module)
                except:
                    pass
            
            # Execute code
            with contextlib.redirect_stdout(output_buffer), \
                 contextlib.redirect_stderr(error_buffer):
                exec(code, namespace)
            
            output = output_buffer.getvalue()
            result = namespace.get('result', output)
            
            return {
                "success": True,
                "result": result,
                "output": output,
                "error": None
            }
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Code execution error: {error_msg}")
            
            return {
                "success": False,
                "result": None,
                "output": output_buffer.getvalue(),
                "error": error_msg
            }
    
    def calculate_productivity_score(self, tasks_completed: int, 
                                     tasks_created: int,
                                     meetings: int,
                                     focus_time: int) -> float:
        """Calculate productivity score."""
        code = f"""
import math

# Weights
TASK_WEIGHT = 0.4
COMPLETION_RATE_WEIGHT = 0.3
MEETING_WEIGHT = 0.1
FOCUS_WEIGHT = 0.2

tasks_completed = {tasks_completed}
tasks_created = {tasks_created}
meetings = {meetings}
focus_time = {focus_time}

# Calculate components
task_score = min(tasks_completed / 10, 1.0) * 100
completion_rate = (tasks_completed / max(tasks_created, 1)) * 100 if tasks_created > 0 else 100
meeting_score = min(meetings / 5, 1.0) * 100
focus_score = min(focus_time / 240, 1.0) * 100  # 4 hours ideal

# Weighted average
result = (
    task_score * TASK_WEIGHT +
    completion_rate * COMPLETION_RATE_WEIGHT +
    meeting_score * MEETING_WEIGHT +
    focus_score * FOCUS_WEIGHT
)

result = round(result, 2)
"""
        
        return self.execute(code)
    
    def analyze_time_distribution(self, events: list) -> Dict[str, Any]:
        """Analyze time distribution across events."""
        code = f"""
from datetime import datetime
from collections import defaultdict

events = {events}

# Calculate time spent per category
time_by_category = defaultdict(int)

for event in events:
    category = event.get('category', 'other')
    duration = event.get('duration', 0)
    time_by_category[category] += duration

result = dict(time_by_category)
"""
        
        return self.execute(code)


# Global instance
code_execution_tool = CodeExecutionTool()