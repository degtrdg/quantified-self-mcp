1. run mcp server:

npx -y supergateway --stdio "uv run sqlite_server.py"

2. run proxy:

ngrok http 8000

3. configure tool (cursor example):

mcp.json

```
{
  "mcpServers": {
    "sqlite-remote": {
      "url": "https://87650bcbb0f0.ngrok-free.app/sse"
    }
  }
}
```
