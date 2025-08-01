#!/usr/bin/env python3
"""
Quick test to verify IPFS gateway connectivity
"""

import asyncio
import httpx

async def test_ipfs_gateway():
    """Test if we can reach IPFS content."""
    test_cid = "QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG"
    gateways = [
        "https://ipfs.io/ipfs/",
        "https://cloudflare-ipfs.com/ipfs/",
        "https://gateway.pinata.cloud/ipfs/"
    ]
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for gateway in gateways:
            try:
                print(f"Testing {gateway}...")
                response = await client.get(f"{gateway}{test_cid}")
                if response.status_code == 200:
                    print(f"✓ Success! Got {len(response.text)} bytes")
                else:
                    print(f"✗ Failed with status {response.status_code}")
            except Exception as e:
                print(f"✗ Error: {e}")

if __name__ == "__main__":
    print("Testing IPFS Gateway Connectivity")
    print("=" * 40)
    asyncio.run(test_ipfs_gateway())
