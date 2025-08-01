# IPFS MCP Server

An MCP (Model Context Protocol) server that exposes IPFS content as Resources. This allows LLMs to read content from IPFS using Content Identifiers (CIDs).

## Features

- **Resources**: Each IPFS CID is exposed as a readable resource
- **Dynamic Resource Management**: Add new IPFS resources on the fly
- **Multiple Gateway Support**: Configurable IPFS gateway URLs
- **Binary Content Handling**: Automatically handles both text and binary content

## Installation

1. Create a new directory for the project:
```bash
mkdir ipfs-mcp-server
cd ipfs-mcp-server
```

2. Copy the Python script as `ipfs_mcp_server.py` and the `pyproject.toml` file

3. Install using uv (recommended):
```bash
uv venv
uv pip install -e .
```

Or using pip:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

## Configuration

### Claude Desktop Configuration

Add the server to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "ipfs": {
      "command": "uv",
      "args": ["run", "ipfs-mcp-server"],
      "cwd": "/path/to/ipfs-mcp-server"
    }
  }
}
```

### Using a Local IPFS Node

If you're running a local IPFS node, edit the `IPFS_GATEWAY` variable in the script:

```python
IPFS_GATEWAY = "http://localhost:8080/ipfs/"
```

## Usage

### Resources

The server exposes IPFS content as resources with URIs in the format: `ipfs://[CID]`

For example:
- `ipfs://QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG`

### Tools

1. **add_ipfs_resource**: Add a new IPFS CID to track as a resource
   - Parameters:
     - `cid`: The IPFS CID to add
     - `name`: Human-readable name
     - `description`: Description of the content
     - `mime_type`: MIME type (optional)

2. **fetch_ipfs_content**: Fetch content from any IPFS CID
   - Parameters:
     - `cid`: The IPFS CID to fetch

## Example CIDs to Try

- `QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG` - IPFS documentation
- `QmXoypizjW3WknFiJnKLwHCnL72vedxjQkDDP1mXWo6uco` - Example content

## How Resources Work

Resources in MCP are different from Tools:
- **Resources** are for accessing content (like files or documents)
- **Tools** are for performing actions or computations

This server implements IPFS content as Resources because:
1. IPFS content is immutable (a CID always points to the same content)
2. The content can be "read" like a file
3. It follows the resource access pattern (URI → Content)

## Development

To modify the server:
1. Edit `ipfs_mcp_server.py`
2. The server will automatically reload if you're using `uv run` with `--reload`

## Troubleshooting

1. **Gateway Timeouts**: Try using a different IPFS gateway
2. **CID Not Found**: Ensure the content is pinned and available on the IPFS network
3. **Binary Content**: Binary files are returned as base64-encoded strings
