# src/Report/ws_client.py
"""Cliente de prueba para el WebSocket de Report.

Ejemplos:
  python src/Report/ws_client.py --session <UUID>
  python src/Report/ws_client.py --uri "ws://127.0.0.1:8000/report/ws/<UUID>"

Este script NO forma parte del pipeline; es solo una herramienta de debug.
"""

import argparse
import asyncio
import json

import websockets


def _build_uri(host: str, port: int, session_id: str) -> str:
    return f"ws://{host}:{port}/report/ws/{session_id}"


async def run(uri: str) -> None:
    # ping_interval evita que algunos proxies cierren el socket por inactividad
    async with websockets.connect(uri, ping_interval=20, ping_timeout=20) as ws:
        print("WS conectado a", uri)
        try:
            while True:
                msg = await ws.recv()
                print("RAW MSG>", msg)
                try:
                    data = json.loads(msg)
                except Exception:
                    print("<no-json>", msg)
                    continue

                kind = data.get("type", "entry")
                if kind in ("state_change", "entry"):
                    ts = data.get("timestamp", "<no-ts>")
                    sid = data.get("session_id", "<no-session>")
                    lbl = data.get("label", "<no-label>")
                    idx = data.get("event_index")
                    if idx is not None:
                        print(f"[{ts}] ({idx}) {sid} -> {lbl}")
                    else:
                        print(f"[{ts}] {sid} -> {lbl}")
                elif kind == "summary":
                    print("SUMMARY:", data)
                else:
                    print(f"<mensaje desconocido tipo={kind}>:", data)
        except websockets.ConnectionClosed:
            print("Socket cerrado")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--uri", default=None, help="WebSocket URI completo")
    ap.add_argument("--session", default=None, help="UUID de sesión (construye el URI)")
    ap.add_argument("--host", default="127.0.0.1", help="Host del server FastAPI")
    ap.add_argument("--port", default=8000, type=int, help="Puerto del server FastAPI")
    args = ap.parse_args()

    if args.uri:
        uri = args.uri
    elif args.session:
        uri = _build_uri(args.host, args.port, args.session)
    else:
        ap.error("Debes pasar --uri o --session")
        return

    asyncio.run(run(uri))


if __name__ == "__main__":
    main()
