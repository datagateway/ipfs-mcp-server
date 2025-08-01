# Troubleshooting Guide

## "Server Disconnected" Error

This is the most common issue when setting up an MCP server. Here's how to diagnose and fix it:

### 1. Check Dependencies

Run the debug script:
```bash
python debug_server.py
```

This will check:
- If all required packages are installed
- If the server can start properly
- If Claude Desktop is configured correctly

### 2. Verify Installation

Make sure the server is installed correctly:
```bash
# Using uv
uv venv
uv pip install -e .

# Or using pip
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

### 3. Test Manual Run

Try running the server manually:
```bash
python -m ipfs_mcp_server
```

You should see:
```
2025-01-15 10:00:00 - ipfs_mcp_server - INFO - Initializing IPFS MCP Server
2025-01-15 10:00:00 - ipfs_mcp_server - INFO - IPFS MCP Server initialized successfully
2025-01-15 10:00:00 - ipfs_mcp_server - INFO - Starting IPFS MCP Server
```

### 4. Check Configuration Path

Make sure your `claude_desktop_config.json` uses the correct path:

**For uv:**
```json
{
  "mcpServers": {
    "ipfs": {
      "command": "uv",
      "args": ["run", "ipfs-mcp-server"],
      "cwd": "/absolute/path/to/ipfs-mcp-server"
    }
  }
}
```

**For pip with venv:**
```json
{
  "mcpServers": {
    "ipfs": {
      "command": "/absolute/path/to/ipfs-mcp-server/venv/bin/python",
      "args": ["-m", "ipfs_mcp_server"],
      "cwd": "/absolute/path/to/ipfs-mcp-server"
    }
  }
}
```

### 5. Common Issues

#### Missing Entry Point
If you get "module not found", make sure `pyproject.toml` is correct and reinstall:
```bash
pip install -e .
```

#### Permission Issues
On macOS/Linux, make sure the script is executable:
```bash
chmod +x ipfs_mcp_server.py
```

#### Wrong Python Version
Make sure you're using Python 3.10 or later:
```bash
python --version
```

### 6. View Logs

The server logs to stderr, so errors should appear in Claude Desktop's developer console:
1. Open Claude Desktop
2. Press Cmd+Option+I (Mac) or Ctrl+Shift+I (Windows/Linux)
3. Check the Console tab for error messages

### 7. Network Issues

If the server starts but can't fetch IPFS content:
- Check your internet connection
- Try a different IPFS gateway in the code
- Make sure the CID you're testing actually exists

### 8. Clean Restart

If all else fails:
1. Close Claude Desktop completely
2. Remove and recreate the virtual environment
3. Reinstall the package
4. Restart Claude Desktop

## Still Having Issues?

Create an issue on GitHub with:
1. The output of `python debug_server.py`
2. Your `claude_desktop_config.json` (remove sensitive paths)
3. Any error messages from Claude Desktop's console
4. Your operating system and Python version
