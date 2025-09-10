

cd /home/opc/dx-agent
nohup uv run hold_resolve_mcp.py &

cd /home/opc/mcpo/
source .venv/bin/activate

mcpo --port 3001 --api-key "top-secret" --server-type "streamable-http" -- http://127.0.0.1:3000/mcp
