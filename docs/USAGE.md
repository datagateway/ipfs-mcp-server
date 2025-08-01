# Using the IPFS MCP Server

## Quick Start

1. **Install the server**:
   ```bash
   git clone https://github.com/datagateway/ipfs-mcp-server
   cd ipfs-mcp-server
   uv venv
   uv pip install -e .
   ```

2. **Configure Claude Desktop** (see examples/claude_desktop_config.json)

3. **Restart Claude Desktop**

## Working with Resources

### Listing Resources

In Claude, you'll see IPFS resources in the resource picker. They appear with:
- Name: Human-readable name
- URI: `ipfs://[CID]`
- Description: What the content contains

### Reading Resources

You can ask Claude to read IPFS content:
- "Read the resource ipfs://QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG"
- "What's in the IPFS Introduction resource?"

### Adding New Resources

Use the `add_ipfs_resource` tool:
- "Add IPFS CID QmXoypizjW3WknFiJnKLwHCnL72vedxjQkDDP1mXWo6uco as 'Example Content'"

## Advanced Usage

### Using Different IPFS Gateways

Edit `ipfs_mcp_server.py` and change:
```python
IPFS_GATEWAY = "http://localhost:8080/ipfs/"  # For local node
```

### Fetching Arbitrary CIDs

Use the `fetch_ipfs_content` tool to fetch any CID without adding it as a resource:
- "Fetch content from IPFS CID QmXoypizjW3WknFiJnKLwHCnL72vedxjQkDDP1mXWo6uco"

## Common CIDs to Try

- `QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG` - IPFS readme
- `QmPZ9gcCEpqKTo6aq61g2nXGUhM4iCL3ewB6LDXZCtioEB` - IPFS paper
- `QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D` - Example content

## Troubleshooting

### Gateway Timeouts
- Try a different gateway (Cloudflare, Pinata, etc.)
- Check if the content is available on IPFS

### Binary Content
- Binary files are returned as base64
- Large files may take time to load

### Resource Not Showing
- Restart Claude Desktop after configuration changes
- Check the logs for errors
