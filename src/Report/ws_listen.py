import sys, time
from websocket import WebSocketApp

def on_open(ws):
    print("✅ WS abierto")
    # keepalive: algunos servidores detectan desconexión si nunca envías nada
    def ping_loop():
        while True:
            time.sleep(20)
            try:
                ws.send("ping")
            except Exception:
                break
    import threading
    threading.Thread(target=ping_loop, daemon=True).start()

def on_message(ws, msg):
    print("<<", msg)

def on_close(ws, code, reason):
    print(f"🧹 WS cerrado code={code} reason={reason}")

def on_error(ws, err):
    print("❌ WS error:", err)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python ws_listen.py ws://127.0.0.1:8000/report/terminal/ws/<registration_id>")
        sys.exit(1)

    url = sys.argv[1]
    app = WebSocketApp(url, on_open=on_open, on_message=on_message, on_close=on_close, on_error=on_error)
    app.run_forever()
