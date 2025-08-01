#!/usr/bin/env python3
"""
MCP Server that exposes IPFS content as Resources.
Each IPFS CID is exposed as a resource that can be read.
"""

import asyncio
import json
import logging
import sys
from typing import Any, Sequence

try:
    import httpx
    from mcp.server.models import InitializationOptions
    import mcp.types as types
    from mcp.server import NotificationOptions, Server
    import mcp.server.stdio
except ImportError as e:
    print(f"Error importing required packages: {e}", file=sys.stderr)
    print("Please install dependencies: pip install mcp httpx", file=sys.stderr)
    sys.exit(1)

# Configure logging to stderr to avoid interfering with stdio
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger(__name__)

# IPFS Gateway URL (using public gateway, but you can use your own)
IPFS_GATEWAY = "https://ipfs.io/ipfs/"
# Alternative gateways:
# IPFS_GATEWAY = "http://localhost:8080/ipfs/"  # Local IPFS node
# IPFS_GATEWAY = "https://gateway.pinata.cloud/ipfs/"
# IPFS_GATEWAY = "https://cloudflare-ipfs.com/ipfs/"

class IPFSServer:
    def __init__(self):
        logger.info("Initializing IPFS MCP Server")
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
        logger.info("IPFS MCP Server initialized successfully")
    
    def setup_handlers(self):
        @self.server.list_resources()
        async def handle_list_resources() -> list[types.Resource]:
            """List all known IPFS resources."""
            logger.info("Listing resources")
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
            logger.info(f"Returning {len(resources)} resources")
            return resources
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Read content from IPFS based on the URI."""
            logger.info(f"Reading resource: {uri}")
            
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
                    logger.info(f"Successfully fetched text content for CID: {cid}")
                    return content
                except UnicodeDecodeError:
                    # For binary content, encode as base64
                    import base64
                    content_b64 = base64.b64encode(response.content).decode('ascii')
                    logger.info(f"Successfully fetched binary content for CID: {cid}")
                    return f"[Binary content - Base64 encoded]\n{content_b64}"
                    
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error fetching IPFS content: {e}")
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
            logger.info("Listing tools")
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
            logger.info(f"Calling tool: {name} with arguments: {arguments}")
            
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
                
                logger.info(f"Added new IPFS resource: {resource_name} (CID: {cid})")
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
                    logger.error(f"Error fetching IPFS content: {e}")
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
        logger.info("Starting IPFS MCP Server")
        try:
            async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
                logger.info("Connected to stdio transport")
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
        except Exception as e:
            logger.error(f"Server error: {e}", exc_info=True)
            raise
    
    async def cleanup(self):
        """Clean up resources."""
        logger.info("Cleaning up IPFS MCP Server")
        await self.http_client.aclose()

async def main():
    """Main entry point."""
    server = IPFSServer()
    try:
        await server.run()
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        await server.cleanup()

if __name__ == "__main__":
    # Run with proper async handling
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed to start server: {e}", exc_info=True)
        sys.exit(1)
