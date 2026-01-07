"""
Base agent class for creating custom agents.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..tools.base_tool import BaseTool


class BaseAgent(ABC):
    """
    Abstract base class for all agents.
    
    This class provides the foundation for creating agents that can use tools
    to accomplish tasks.
    """
    
    def __init__(self, name: str, description: str, tools: Optional[List[BaseTool]] = None):
        self.name = name
        self.description = description
        self.tools = tools or []
        self.conversation_history = []
    
    def add_tool(self, tool: BaseTool):
        """Add a tool to this agent's toolkit."""
        self.tools.append(tool)
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get schemas for all available tools."""
        return [tool.get_schema() for tool in self.tools]
    
    def execute_tool(self, tool_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific tool with the given input."""
        for tool in self.tools:
            if tool.name == tool_name:
                # Convert dict to appropriate input model
                input_model = self._create_tool_input(tool, input_data)
                result = tool.execute(input_model)
                return result.model_dump()
        
        raise ValueError(f"Tool '{tool_name}' not found")
    
    @abstractmethod
    def process_message(self, message: str) -> str:
        """
        Process a message and return a response.
        
        Args:
            message: The input message to process
            
        Returns:
            str: The agent's response
        """
        pass
    
    def _create_tool_input(self, tool: BaseTool, input_data: Dict[str, Any]):
        """Create the appropriate input model for a tool."""
        # This is a simplified implementation
        # In practice, you'd need more sophisticated input validation
        from ..tools.calculator_tool import CalculatorInput, CalculatorTool
        from ..tools.web_search_tool import WebSearchInput, WebSearchTool
        
        if isinstance(tool, CalculatorTool):
            return CalculatorInput(**input_data)
        elif isinstance(tool, WebSearchTool):
            return WebSearchInput(**input_data)
        else:
            raise ValueError(f"Unknown tool type: {type(tool)}")
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Get the agent's schema for use as a tool in other agents.
        
        This allows agents to be used as tools by other agents.
        """
        return {
            "name": self.name,
            "description": self.description,
            "available_tools": self.get_available_tools()
        }