#!/usr/bin/env python3
"""
Tests for the IPFS MCP Server
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import httpx
from ipfs_mcp_server import IPFSServer
import mcp.types as types


@pytest.fixture
async def server():
    """Create a test server instance."""
    server = IPFSServer()
    yield server
    await server.cleanup()


@pytest.mark.asyncio
async def test_list_resources(server):
    """Test listing IPFS resources."""
    # Mock the handler
    resources = await server.server._resource_handlers["list"]()[0]()
    
    assert len(resources) > 0
    assert all(isinstance(r, types.Resource) for r in resources)
    assert all(r.uri.startswith("ipfs://") for r in resources)


@pytest.mark.asyncio
async def test_read_resource_success(server):
    """Test successfully reading an IPFS resource."""
    # Mock the HTTP response
    mock_response = AsyncMock()
    mock_response.text = "Test content from IPFS"
    mock_response.raise_for_status = Mock()
    
    with patch.object(server.http_client, 'get', return_value=mock_response):
        content = await server.server._resource_handlers["read"]()[0]("ipfs://QmTest123")
        assert content == "Test content from IPFS"


@pytest.mark.asyncio
async def test_read_resource_invalid_uri(server):
    """Test reading resource with invalid URI."""
    with pytest.raises(ValueError, match="Invalid IPFS URI"):
        await server.server._resource_handlers["read"]()[0]("http://example.com")


@pytest.mark.asyncio
async def test_read_resource_invalid_cid(server):
    """Test reading resource with invalid CID."""
    with pytest.raises(ValueError, match="Invalid IPFS CID"):
        await server.server._resource_handlers["read"]()[0]("ipfs://short")


@pytest.mark.asyncio
async def test_add_ipfs_resource(server):
    """Test adding a new IPFS resource."""
    # Get the tool handler
    tools = await server.server._tool_handlers["list"]()[0]()
    tool_handler = server.server._tool_handlers["call"]()[0]
    
    # Mock the session to prevent notification errors
    mock_session = AsyncMock()
    mock_session.send_resource_list_changed = AsyncMock()
    server.server.request_context = Mock()
    server.server.request_context.session = mock_session
    
    # Call the tool
    result = await tool_handler(
        "add_ipfs_resource",
        {
            "cid": "QmNewResource123456789012345678901234567890123456",
            "name": "Test Resource",
            "description": "A test resource"
        }
    )
    
    assert len(result) == 1
    assert "Successfully added" in result[0].text
    assert "QmNewResource123456789012345678901234567890123456" in server.known_cids


@pytest.mark.asyncio
async def test_fetch_ipfs_content(server):
    """Test fetching arbitrary IPFS content."""
    # Mock the HTTP response
    mock_response = AsyncMock()
    mock_response.text = "Fetched content"
    mock_response.raise_for_status = Mock()
    
    tool_handler = server.server._tool_handlers["call"]()[0]
    
    with patch.object(server.http_client, 'get', return_value=mock_response):
        result = await tool_handler(
            "fetch_ipfs_content",
            {"cid": "QmTest123456789012345678901234567890123456789012"}
        )
        
        assert len(result) == 1
        assert result[0].text == "Fetched content"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
