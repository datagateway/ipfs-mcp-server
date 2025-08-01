#!/usr/bin/env python3
"""
MCP Server that exposes IPFS content as Resources.
Each IPFS CID is exposed as a resource that can be read.
"""

import asyncio
import json
import logging
from typing import Any, Sequence
import httpx
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# IPFS Gateway URL (using public gateway, but you can use your own)
IPFS_GATEWAY = "https://ipfs.io/ipfs/"
# Alternative gateways:
# IPFS_GATEWAY = "http://localhost:8080/ipfs/"  # Local IPFS node
# IPFS_GATEWAY = "https://gateway.pinata.cloud/ipfs/"
# IPFS_GATEWAY = "https://cloudflare-ipfs.com/ipfs/"

class IPFSServer:
    def __init__(self):
        self.server = Server("ipfs-server")
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
        # Store known CIDs with metadata
        # In a real implementation, you might load this from a config file
        self.known_cids = {
            "QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG": {
                "name": "IPFS Introduction",
                "description": "An introduction to IPFS concepts",
                "mime_type": "text/plain"
            },
            # Add more known CIDs here
        }
        
        # Set up handlers
        self.setup_handlers()
    
    def setup_handlers(self):
        @self.server.list_resources()
        async def handle_list_resources() -> list[types.Resource]:
            """List all known IPFS resources."""
            resources = []
            for cid, metadata in self.known_cids.items():
                resources.append(
                    types.Resource(
                        uri=f"ipfs://{cid}",
                        name=metadata.get("name", f"IPFS File {cid[:8]}..."),
                        description=metadata.get("description", f"Content from IPFS CID: {cid}"),
                        mimeType=metadata.get("mime_type", "application/octet-stream")
                    )
                )
            return resources
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Read content from IPFS based on the URI."""
            # Parse the URI to extract CID
            if not uri.startswith("ipfs://"):
                raise ValueError(f"Invalid IPFS URI: {uri}")
            
            cid = uri[7:]  # Remove "ipfs://" prefix
            
            # Validate CID format (basic check)
            if not cid or len(cid) < 46:
                raise ValueError(f"Invalid IPFS CID: {cid}")
            
            try:
                # Fetch content from IPFS gateway
                url = f"{IPFS_GATEWAY}{cid}"
                logger.info(f"Fetching IPFS content from: {url}")
                
                response = await self.http_client.get(url)
                response.raise_for_status()
                
                # Try to decode as text, otherwise return base64
                try:
                    content = response.text
                    return content
                except UnicodeDecodeError:
                    # For binary content, encode as base64
                    import base64
                    content_b64 = base64.b64encode(response.content).decode('ascii')
                    return f"[Binary content - Base64 encoded]\n{content_b64}"
                    
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise ValueError(f"CID not found: {cid}")
                else:
                    raise ValueError(f"Error fetching from IPFS: {e}")
            except Exception as e:
                logger.error(f"Error fetching IPFS content: {e}")
                raise ValueError(f"Failed to fetch IPFS content: {str(e)}")
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List available tools."""
            return [
                types.Tool(
                    name="add_ipfs_resource",
                    description="Add a new IPFS CID to track as a resource",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "cid": {
                                "type": "string",
                                "description": "The IPFS CID to add"
                            },
                            "name": {
                                "type": "string",
                                "description": "Human-readable name for this resource"
                            },
                            "description": {
                                "type": "string",
                                "description": "Description of the content"
                            },
                            "mime_type": {
                                "type": "string",
                                "description": "MIME type of the content (default: application/octet-stream)",
                                "default": "application/octet-stream"
                            }
                        },
                        "required": ["cid", "name"]
                    }
                ),
                types.Tool(
                    name="fetch_ipfs_content",
                    description="Fetch content from any IPFS CID (not just tracked resources)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "cid": {
                                "type": "string",
                                "description": "The IPFS CID to fetch"
                            }
                        },
                        "required": ["cid"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(
            name: str, 
            arguments: dict | None
        ) -> Sequence[types.TextContent | types.ImageContent | types.EmbeddedResource]:
            """Handle tool calls."""
            if name == "add_ipfs_resource":
                cid = arguments.get("cid")
                resource_name = arguments.get("name")
                description = arguments.get("description", f"Content from IPFS CID: {cid}")
                mime_type = arguments.get("mime_type", "application/octet-stream")
                
                # Add to known CIDs
                self.known_cids[cid] = {
                    "name": resource_name,
                    "description": description,
                    "mime_type": mime_type
                }
                
                # Notify about resource list change
                await self.server.request_context.session.send_resource_list_changed()
                
                return [
                    types.TextContent(
                        type="text",
                        text=f"Successfully added IPFS resource: {resource_name} (CID: {cid})"
                    )
                ]
            
            elif name == "fetch_ipfs_content":
                cid = arguments.get("cid")
                
                try:
                    # Fetch content from IPFS
                    url = f"{IPFS_GATEWAY}{cid}"
                    response = await self.http_client.get(url)
                    response.raise_for_status()
                    
                    # Try to return as text
                    try:
                        content = response.text
                        return [
                            types.TextContent(
                                type="text",
                                text=content
                            )
                        ]
                    except UnicodeDecodeError:
                        # For binary content
                        return [
                            types.TextContent(
                                type="text",
                                text=f"[Binary content from CID: {cid}] - Use the resource URI ipfs://{cid} to access"
                            )
                        ]
                        
                except Exception as e:
                    return [
                        types.TextContent(
                            type="text",
                            text=f"Error fetching IPFS content: {str(e)}"
                        )
                    ]
            
            else:
                raise ValueError(f"Unknown tool: {name}")
    
    async def run(self):
        """Run the server."""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="ipfs-mcp-server",
                    server_version="0.1.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
    
    async def cleanup(self):
        """Clean up resources."""
        await self.http_client.aclose()

async def main():
    """Main entry point."""
    server = IPFSServer()
    try:
        await server.run()
    finally:
        await server.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
