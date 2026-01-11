#!/usr/bin/env python3
"""Run OpenProject MCP Server - Python 3.9 Compatible Version."""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Import and run the compatible server
from mcp_server_compatible import main

if __name__ == "__main__":
    import asyncio
    
    # Print startup message
    print("🚀 Starting OpenProject MCP Server (Python 3.9 Compatible)", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(f"Server will be available on port 8080", file=sys.stderr)
    
    # Run the server
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 OpenProject MCP Server shutting down gracefully", file=sys.stderr)
    except Exception as e:
        print(f"❌ Server error: {e}", file=sys.stderr)
        sys.exit(1)
