# IPFS MCP Server Architecture

## Overview

This MCP server demonstrates the Resource pattern by exposing IPFS content as readable resources. Each IPFS CID (Content Identifier) is mapped to a resource URI that can be accessed by MCP clients.

## Key Components

### Resources vs Tools

The server implements both Resources and Tools to demonstrate their different use cases:

#### Resources
- **Purpose**: Expose IPFS content as readable documents
- **URI Format**: `ipfs://[CID]`
- **Access Pattern**: URI → Content
- **Example**: Reading a file from IPFS

#### Tools
- **Purpose**: Perform actions like adding new resources or fetching arbitrary CIDs
- **Parameters**: Accept structured input
- **Example**: Adding a new IPFS resource to track

### Design Decisions

1. **Immutable Content**: IPFS CIDs are perfect for the Resource pattern because they're content-addressed and immutable

2. **Dynamic Resource Management**: The server maintains a list of "known" CIDs that appear in the resource list, but can also fetch any valid CID

3. **Gateway Abstraction**: Uses HTTP gateways to access IPFS content, making it work without requiring a local IPFS node

4. **Binary Content Handling**: Automatically detects and handles both text and binary content appropriately

## Data Flow

1. **Resource Discovery**:
   ```
   Client → list_resources() → Server returns known IPFS resources
   ```

2. **Resource Access**:
   ```
   Client → read_resource("ipfs://Qm...") → Server fetches from IPFS → Returns content
   ```

3. **Dynamic Addition**:
   ```
   Client → add_ipfs_resource(cid, name) → Server updates known_cids → Notifies resource change
   ```

## Extension Points

- **Persistence**: Currently uses in-memory storage; could be extended to use a database
- **Gateway Selection**: Could implement smart gateway selection based on availability
- **Content Types**: Could add better MIME type detection
- **Pinning**: Could integrate with IPFS pinning services
