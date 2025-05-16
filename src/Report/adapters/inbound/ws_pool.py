# src/Report/adapters/inbound/ws_pool.py
from fastapi import WebSocket

# Un set global de websockets conectados
connected: set[WebSocket] = set()
