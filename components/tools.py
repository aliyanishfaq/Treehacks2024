from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool

@tool 
def get_weather(query: str) -> str:
  """Get current weather information at San Francisco"""
  return "60 Farenheit. Very pleasant weather. A bit cloudy"


agent_tools = []
agent_tools.append(get_weather)


# https://python.langchain.com/docs/modules/agents/tools/custom_tools