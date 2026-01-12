# src/Report/ws_client.py
import argparse
import asyncio
import json
from typing import Optional

import websockets


async def keepalive(ws, every_seconds: int = 20):
    """Envia texto 'ping' cada N segundos para que el server (receive_text) no quede colgado."""
    try:
        while True:
            await asyncio.sleep(every_seconds)
            await ws.send("ping")
    except Exception:
        return


def build_uri(host: str, port: int, session_id: Optional[str], raw_uri: Optional[str]) -> str:
    if raw_uri:
        return raw_uri
    if session_id:
        return f"ws://{host}:{port}/report/ws?session_id={session_id}"
    return f"ws://{host}:{port}/report/ws"


async def run(uri: str):
    async with websockets.connect(uri, ping_interval=None) as ws:
        print("✅ WS conectado a:", uri)

        ka = asyncio.create_task(keepalive(ws, every_seconds=20))

        try:
            while True:
                msg = await ws.recv()
                print("RAW MSG>", msg)

                try:
                    data = json.loads(msg)
                except Exception:
                    print("   (no es JSON)")
                    continue

                kind = data.get("type", "state_change")

                if kind in ("state_change", "entry"):
                    ts = data.get("timestamp", "<no-ts>")
                    sid = data.get("session_id", "<no-session>")
                    lbl = data.get("label", "<no-label>")
                    idx = data.get("event_index")
                    if idx is not None:
                        print(f"[{ts}] (#{idx}) {sid} → {lbl}")
                    else:
                        print(f"[{ts}] {sid} → {lbl}")

                elif kind == "summary":
                    print("SUMMARY:", data)

                else:
                    print(f"<mensaje desconocido tipo={kind}>:", data)

        except websockets.ConnectionClosed as e:
            print(f"🧹 Socket cerrado code={e.code} reason={e.reason}")
            if e.code == 1008:
                print("   ↳ 1008: registration_id inválido/no existe (o server se reinició y perdió memoria).")
        finally:
            ka.cancel()


def main():
    p = argparse.ArgumentParser("WS client para Report")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8000)
    p.add_argument("--session", default=None, help="UUID de sesión (modo directo)")
    p.add_argument("--uri", default=None, help="URI completa (modo registration_id)")
    args = p.parse_args()

    uri = build_uri(args.host, args.port, args.session, args.uri)
    asyncio.run(run(uri))


if __name__ == "__main__":
    main()
