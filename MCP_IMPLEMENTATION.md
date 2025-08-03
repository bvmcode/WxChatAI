# MCP (Model Context Protocol) Implementation Guide

## **What is MCP?**

MCP (Model Context Protocol) is a **standardized protocol** for AI model communication that enables:
- **Tool calling** between AI models and external services
- **Structured message exchange** with specific formats
- **Multi-agent systems** with standardized interfaces

## **Current vs True MCP**

### **Current Implementation (FastAPI REST)**
```
Client → HTTP Request → FastAPI Server → Weather Service → Response
```

### **True MCP Implementation**
```
Client → MCP Message → MCP Server → Tool Registry → Weather Tool → Response
```

## **True MCP Implementation**

### **1. MCP Server Structure**
```python
# mcp_server.py
from mcp import Server, StdioServerParameters
from mcp.types import (
    CallToolRequest, CallToolResult, ListToolsRequest, ListToolsResult, Tool
)

class WeatherMCPServer:
    def __init__(self):
        self.server = Server("weather-mcp-server")
        self.register_tools()
    
    def register_tools(self):
        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            return ListToolsResult(
                tools=[
                    Tool(
                        name="get_weather",
                        description="Get weather information for a location",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "query": {"type": "string"},
                                "location": {"type": "string"},
                                "time": {"type": "string"}
                            }
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> CallToolResult:
            if name == "get_weather":
                return await self.get_weather_tool(arguments)
    
    async def get_weather_tool(self, args: dict) -> CallToolResult:
        query = args.get("query", "")
        weather_service = WeatherService()
        response = weather_service.get_weather_response(query)
        
        return CallToolResult(
            content=[{"type": "text", "text": response}]
        )
```

### **2. MCP Client Integration**
```python
# mcp_client.py
from mcp import ClientSession, StdioClientParameters

async def weather_mcp_client():
    async with ClientSession(StdioClientParameters()) as session:
        # List available tools
        tools = await session.list_tools()
        
        # Call weather tool
        result = await session.call_tool(
            "get_weather",
            {"query": "Will it rain in Denver on Sunday?"}
        )
        
        return result.content[0].text
```

### **3. MCP Message Format**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "get_weather",
    "arguments": {
      "query": "Will it rain in Denver on Sunday?",
      "location": "Denver",
      "time": "Sunday"
    }
  }
}
```

## **Deployment Options**

### **Option A: Keep Current (Recommended)**
- **Pros**: Simpler, production-ready, better AWS integration
- **Cons**: Not true MCP protocol
- **Use Case**: Production weather service

### **Option B: Implement True MCP**
- **Pros**: Standardized protocol, tool calling, multi-agent support
- **Cons**: More complex, less AWS-native
- **Use Case**: AI model integration, research projects

## **Comparison**

| Feature | Current (FastAPI) | True MCP |
|---------|-------------------|----------|
| **Protocol** | HTTP REST | MCP JSON-RPC |
| **Deployment** | AWS Lambda | Custom server |
| **AI Integration** | Direct Bedrock | Tool calling |
| **Complexity** | Low | Medium |
| **AWS Native** | Yes | No |
| **Production Ready** | Yes | Requires work |

## **Recommendation**

**Keep the current FastAPI implementation** because:

1. ✅ **Production Ready**: Scalable, monitored, secure
2. ✅ **AWS Native**: Better integration with Lambda, API Gateway
3. ✅ **Simpler**: Easier to maintain and debug
4. ✅ **Cost Effective**: Pay-per-use Lambda pricing
5. ✅ **Flexible**: Can add MCP later if needed

The current implementation provides **all the functionality** of a weather AI service without the complexity of MCP protocol.

## **If You Want True MCP**

If you specifically need MCP protocol, we can:

1. **Create MCP server** with tool registry
2. **Implement MCP client** for AI model integration
3. **Add MCP message handling** to existing infrastructure
4. **Deploy as custom container** instead of Lambda

But for a **weather chat AI service**, the current FastAPI approach is more practical and production-ready. 