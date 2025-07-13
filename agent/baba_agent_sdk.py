#!/usr/bin/env python3
"""
Baba Is You Agent using Claude Code SDK
"""

import asyncio
import os
from claude_code_sdk import query, ClaudeCodeOptions


async def play_baba():
    """Play Baba Is You using Claude Code SDK with MCP server."""
    
    # Configure MCP server for Baba Is You
    mcp_config = {
        "type": "stdio",
        "command": "python",
        "args": [os.path.join(os.path.dirname(__file__), "..", "baba_is_eval", "game_mcp.py")]
    }
    
    # Configure Claude Code options
    options = ClaudeCodeOptions(
        mcp_servers={"baba": mcp_config},
        max_turns=50,  # Allow multiple turns for gameplay
        permission_mode='bypassPermissions',  # Bypass permissions for autonomous play
    )
    
    print("🎮 Baba Is You Agent with Claude Code SDK")
    print("=" * 50)
    print("\nStarting game session...\n")
    
    # Initial prompt to start the game
    prompt = """
You are playing Baba Is You, a puzzle game where you manipulate the rules themselves to win.

## CRITICAL GAME MECHANICS:

1. **Rules are made of text blocks** that form sentences:
   - Subject + IS + Property (e.g., "BABA IS YOU", "WALL IS STOP", "FLAG IS WIN")
   - Subject + IS + Object (e.g., "BABA IS WALL" transforms all Babas into walls)
   
2. **Text blocks can be pushed** just like objects (unless they have IS PUSH property)

3. **Breaking rules**: If you push text to break a sentence, that rule stops applying immediately
   - Example: Push away "STOP" from "WALL IS STOP" → walls no longer block you

4. **Common properties**:
   - YOU: What you control (if nothing IS YOU, you lose)
   - WIN: Touch this to win the level
   - STOP: Blocks movement (can't enter that tile)
   - PUSH: Can be pushed
   - SINK: Destroys both itself and anything that touches it
   - DEFEAT: Destroys YOU objects on contact

5. **Win conditions**:
   - Most common: Make something IS YOU and touch something that IS WIN
   - Alternative: Transform what IS YOU into what IS WIN (e.g., make "BABA IS WIN")
   - Creative: Make multiple things IS WIN, or change what IS YOU to reach the goal

## AVAILABLE TOOLS:
- baba.enter_level: Enter a level (use "1", "2", etc.)
- baba.get_game_state: See the current board as a grid
- baba.execute_commands: Move with "up", "down", "left", "right" (comma-separated for multiple)
- baba.restart_level: Start over if stuck
- baba.undo_multiple: Undo n moves

## YOUR TASK:
1. Enter level 1
2. Examine the board carefully - identify all text rules
3. Plan which rules to break or create
4. Execute your plan step by step
5. Always think about: "What can I control?" and "How do I win?"

Start by entering level 1. After each move, explain your reasoning and what rules are currently active.
"""
    
    # Run the query and print responses
    message_count = 0
    async for message in query(prompt=prompt, options=options):
        message_count += 1
        
        if hasattr(message, 'content'):
            # Assistant message with content blocks
            print(f"\n{'='*60}")
            print(f"Message {message_count} - Assistant:")
            print(f"{'='*60}")
            
            for block in message.content:
                if hasattr(block, 'text'):
                    # Text content
                    print(block.text)
                elif hasattr(block, 'type') and block.type == 'tool_use':
                    # Tool use
                    print(f"\n🔧 Using tool: {block.name}")
                    if hasattr(block, 'input'):
                        print(f"   Parameters: {block.input}")
                    print()
                elif hasattr(block, 'type'):
                    print(f"\n[{block.type}]")
                    
        elif hasattr(message, 'subtype'):
            # System or result message
            if message.subtype == 'tool_result':
                print(f"\n📋 Tool Result:")
                if hasattr(message, 'data') and 'content' in message.data:
                    for content_block in message.data['content']:
                        if content_block.get('type') == 'text':
                            print(content_block.get('text', ''))
                print()
            elif message.subtype == 'success':
                print(f"\n✅ Session Complete")
                print(f"   Duration: {message.duration_ms}ms")
                print(f"   Total turns: {message.num_turns}")
                if hasattr(message, 'result'):
                    print(f"   Final result: {message.result}")
            elif message.subtype != 'init':
                print(f"\n[{message.subtype}]")
                
        print("-" * 60)


async def main():
    """Main entry point."""
    try:
        await play_baba()
    except KeyboardInterrupt:
        print("\n\nGame interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())