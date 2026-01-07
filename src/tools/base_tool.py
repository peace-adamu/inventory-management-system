"""
Base tool class for creating custom agent tools.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel


class ToolInput(BaseModel):
    """Base class for tool input validation."""
    pass


class ToolOutput(BaseModel):
    """Base class for tool output formatting."""
    success: bool
    result: Any
    error: Optional[str] = None


class BaseTool(ABC):
    """
    Abstract base class for all agent tools.
    
    This class provides the foundation for creating custom tools that agents
    can use to perform specific tasks.
    """
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    def execute(self, input_data: ToolInput) -> ToolOutput:
        """
        Execute the tool with the given input.
        
        Args:
            input_data: Validated input data for the tool
            
        Returns:
            ToolOutput: The result of the tool execution
        """
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Get the tool's input schema for agent integration.
        
        Returns:
            Dict containing the tool's name, description, and input schema
        """
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self._get_input_schema()
        }
    
    @abstractmethod
    def _get_input_schema(self) -> Dict[str, Any]:
        """Get the input schema for this tool."""
        pass