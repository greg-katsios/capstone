#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify MCP server resources are working correctly.
This tests the server directly without the inspector.
"""

import asyncio
import json
import sys
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_mcp_resources():
    """Test connecting to the MCP server and reading resources."""

    # Use the same Python interpreter that's running this script
    python_exe = sys.executable
    server_script = os.path.join(os.path.dirname(__file__), "participant_server.py")

    server_params = StdioServerParameters(
        command=python_exe,
        args=[server_script],
        env=None
    )

    print("=" * 60)
    print("Testing MCP Server Resources")
    print("=" * 60)
    print()

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()
            print("[OK] Session initialized successfully")
            print()

            # List available resources
            print("Listing resources...")
            resources = await session.list_resources()
            print(f"Found {len(resources.resources)} resource(s):")
            for resource in resources.resources:
                print(f"  - {resource.name}")
                print(f"    URI: {resource.uri}")
                print(f"    Type: {resource.mimeType}")
                print(f"    Description: {resource.description}")
            print()

            # Try to read the participant profile
            if len(resources.resources) > 0:
                uri = resources.resources[0].uri
                print(f"Reading resource: {uri}")
                try:
                    result = await session.read_resource(uri)
                    print("[OK] Resource read successfully!")
                    print()
                    print("Contents:")
                    for content in result.contents:
                        if hasattr(content, 'text'):
                            data = json.loads(content.text)
                            print(json.dumps(data, indent=2))
                    print()
                except Exception as e:
                    print(f"[ERROR] Error reading resource: {e}")
                    import traceback
                    traceback.print_exc()
                    print()

            print("=" * 60)
            print("Test Complete!")
            print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_mcp_resources())
