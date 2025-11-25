import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import asyncio
import json
from app.clients.loki_client import LokiClient


async def main():
    client = LokiClient("http://localhost:3100")
    
    result = await client.query_logs(time_range="5m", limit=1000)
    
    # Print full JSON to see actual log objects
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
