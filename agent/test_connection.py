#!/usr/bin/env python3
"""
Simple test script to verify MCP connection
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import os

async def test_connection():
    """Test connection to the MCP server."""
    server_params = StdioServerParameters(
        command="python",
        args=["../baba_is_eval/game_mcp.py"],
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    
    print("Attempting to connect to MCP server...")
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the connection
                await session.initialize()
                print("✅ Successfully connected to MCP server!")
                
                # List available tools
                tools_response = await session.list_tools()
                print("\nAvailable tools:")
                for tool in tools_response.tools:
                    print(f"  - {tool.name}: {tool.description}")
                
                # Test getting game state
                print("\nTesting get_game_state tool...")
                result = await session.call_tool("get_game_state", {})
                if result.content:
                    print("✅ Successfully called get_game_state")
                    print(f"Response preview: {result.content[0].text[:100]}...")
                
                # Test game rules
                print("\nTesting game_rules tool...")
                result = await session.call_tool("game_rules", {"topic": "basic"})
                if result.content:
                    print("✅ Successfully called game_rules")
                    print(f"Response preview: {result.content[0].text[:100]}...")
                
                print("\n✅ All tests passed!")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure:")
        print("1. The game is running")
        print("2. You've run the setup.sh script in baba_is_eval/")
        print("3. The MCP server can be started")

if __name__ == "__main__":
    asyncio.run(test_connection())