"""Entry point for running as a module."""

from ipfs_mcp_server import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
