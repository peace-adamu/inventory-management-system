"""
Calculator tool - demonstrates basic tool creation from Python functions.
"""

from typing import Dict, Any
from pydantic import BaseModel, Field
from src.tools.base_tool import BaseTool, ToolInput, ToolOutput


class CalculatorInput(ToolInput):
    """Input schema for calculator operations."""
    operation: str = Field(description="The operation to perform: add, subtract, multiply, divide")
    a: float = Field(description="First number")
    b: float = Field(description="Second number")


class CalculatorTool(BaseTool):
    """
    A simple calculator tool that demonstrates how to convert Python functions
    into agent-callable tools.
    """
    
    def __init__(self):
        super().__init__(
            name="calculator",
            description="Performs basic mathematical operations (add, subtract, multiply, divide)"
        )
    
    def execute(self, input_data: CalculatorInput) -> ToolOutput:
        """Execute the calculator operation."""
        try:
            result = self._calculate(input_data.operation, input_data.a, input_data.b)
            return ToolOutput(success=True, result=result)
        except Exception as e:
            return ToolOutput(success=False, result=None, error=str(e))
    
    def _calculate(self, operation: str, a: float, b: float) -> float:
        """Perform the actual calculation."""
        operations = {
            "add": lambda x, y: x + y,
            "subtract": lambda x, y: x - y,
            "multiply": lambda x, y: x * y,
            "divide": lambda x, y: x / y if y != 0 else None
        }
        
        if operation not in operations:
            raise ValueError(f"Unknown operation: {operation}")
        
        result = operations[operation](a, b)
        if result is None:
            raise ValueError("Division by zero")
        
        return result
    
    def _get_input_schema(self) -> Dict[str, Any]:
        """Get the input schema for this tool."""
        return CalculatorInput.model_json_schema()