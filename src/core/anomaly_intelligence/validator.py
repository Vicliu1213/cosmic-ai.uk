import json

class Validator:
    @staticmethod
    def verify_and_fix(raw_ai_json, current_price):
        try:
            data = json.loads(raw_ai_json) if isinstance(raw_ai_json, str) else raw_ai_json

            # 強制校驗止損單是否存在
            if 'sl' not in data or data['sl'] is None:
                # 自動補齊保險止損 (1.5%)
                data['sl'] = current_price * 0.985 if data['side'] == 'LONG' else current_price * 1.015

            # 確保信心度為 float
            data['confidence'] = float(data.get('confidence', 0.5))

            print(f"🛡️ [邏輯驗證] JSON 合規，信心值: {data['confidence']}")
            return True, data
        except Exception as e:
            print(f"🚨 [驗證失敗] AI 格式錯誤: {e}")
            return False, None
