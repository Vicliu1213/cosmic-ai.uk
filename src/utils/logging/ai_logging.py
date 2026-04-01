import json
import os
from datetime import datetime

class AILogger:
    def __init__(self, log_dir="logs/ai_thought/"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)

    def log_thought(self, symbol, prompt, response, metrics):
        filename = f"{self.log_dir}{datetime.now().strftime('%Y%m%d')}.jsonl"
        entry = {
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "input_prompt": prompt,
            "raw_response": response,
            "market_metrics": metrics # 當時的斜率、成交量等
        }
        with open(filename, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
