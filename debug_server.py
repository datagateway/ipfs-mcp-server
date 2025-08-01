#!/usr/bin/env python3
"""
Debug script to test the IPFS MCP Server
"""

import sys
import subprocess
import json

def check_dependencies():
    """Check if required dependencies are installed."""
    print("Checking dependencies...")
    
    try:
        import mcp
        print("✓ mcp package is installed")
    except ImportError:
        print("✗ mcp package is NOT installed")
        print("  Run: pip install mcp")
        return False
    
    try:
        import httpx
        print("✓ httpx package is installed")
    except ImportError:
        print("✗ httpx package is NOT installed")
        print("  Run: pip install httpx")
        return False
    
    return True

def test_server_startup():
    """Test if the server can start without errors."""
    print("\nTesting server startup...")
    
    try:
        # Try to import and create server instance
        from ipfs_mcp_server import IPFSServer
        server = IPFSServer()
        print("✓ Server instance created successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to create server instance: {e}")
        return False

def check_claude_config():
    """Check Claude Desktop configuration."""
    print("\nChecking Claude Desktop configuration...")
    
    import os
    import platform
    
    if platform.system() == "Darwin":  # macOS
        config_path = os.path.expanduser("~/Library/Application Support/Claude/claude_desktop_config.json")
    elif platform.system() == "Windows":
        config_path = os.path.expanduser("~\\AppData\\Roaming\\Claude\\claude_desktop_config.json")
    else:
        print("⚠ Unknown platform, cannot check config location")
        return
    
    if os.path.exists(config_path):
        print(f"✓ Config file exists at: {config_path}")
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                if "mcpServers" in config and "ipfs" in config["mcpServers"]:
                    print("✓ IPFS server is configured")
                    print(f"  Config: {json.dumps(config['mcpServers']['ipfs'], indent=2)}")
                else:
                    print("✗ IPFS server is NOT configured in Claude Desktop")
        except Exception as e:
            print(f"✗ Error reading config: {e}")
    else:
        print(f"✗ Config file not found at: {config_path}")
        print("  Create the file with the example configuration")

def test_manual_run():
    """Test running the server manually."""
    print("\nTesting manual server run...")
    print("Running: python -m ipfs_mcp_server")
    print("Press Ctrl+C to stop\n")
    
    try:
        subprocess.run([sys.executable, "-m", "ipfs_mcp_server"])
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"\nError running server: {e}")

if __name__ == "__main__":
    print("IPFS MCP Server Debug Tool")
    print("=" * 50)
    
    if not check_dependencies():
        print("\n❌ Missing dependencies. Please install them first.")
        sys.exit(1)
    
    if not test_server_startup():
        print("\n❌ Server startup failed. Check the error messages above.")
        sys.exit(1)
    
    check_claude_config()
    
    print("\n" + "=" * 50)
    print("All checks passed! Now testing server run...")
    print("=" * 50)
    
    test_manual_run()
