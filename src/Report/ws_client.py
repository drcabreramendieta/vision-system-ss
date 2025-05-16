# src/Report/ws_client.py
import asyncio, json, websockets

async def run():
    uri = "ws://127.0.0.1:8000/report/ws"
    async with websockets.connect(uri) as ws:
        print("WS conectado a", uri)
        try:
            while True:
                msg = await ws.recv()
                print("RAW MSG>", msg)           # 1) Ver lo que realmente llegó
                data = json.loads(msg)
                kind = data.get("type", "entry")  # 2) usar .get con default
                if kind == "entry":
                    ts   = data.get("timestamp", "<no-ts>")
                    sid  = data.get("session_id", "<no-session>")
                    lbl  = data.get("label", "<no-label>")
                    print(f"[{ts}] {sid} → {lbl}")
                elif kind == "summary":
                    print("SUMMARY:", data)
                else:
                    print(f"<mensaje desconocido tipo={kind}>:", data)
        except websockets.ConnectionClosed:
            print("Socket cerrado")

if __name__ == "__main__":
    asyncio.run(run())
