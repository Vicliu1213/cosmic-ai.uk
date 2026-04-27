import threading
import requests
import json

class AsyncTelegramNotifier:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{token}/sendMessage"

    def send_opportunity(self, opp):
        message = f"🐊 *猎杀* {opp['symbol']} @ {opp['entry']}\nSL {opp['sl']} TP {opp['tp']}"
        def _send():
            try:
                requests.post(self.api_url, json={'chat_id': self.chat_id, 'text': message, 'parse_mode':'Markdown'}, timeout=1)
            except:
                pass
        threading.Thread(target=_send, daemon=True).start()