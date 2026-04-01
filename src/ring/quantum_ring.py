import hashlib
import secrets
import time
import json
import os
from typing import Optional, Tuple, List, Dict
from collections import deque
import numpy as np

# 简单行为模型（将在 behavior_ai.py 中细化）
class SimpleBehaviorAI:
    def __init__(self):
        self.history = deque(maxlen=100)
        self.mean = None
        self.std = None

    def update(self, features: List[float]):
        self.history.append(features)
        if len(self.history) >= 10:
            arr = np.array(self.history)
            self.mean = np.mean(arr, axis=0)
            self.std = np.std(arr, axis=0) + 1e-8

    def confidence(self, features: List[float]) -> float:
        if self.mean is None:
            return 0.5
        z = np.abs((features - self.mean) / self.std)
        return float(np.mean(np.exp(-z)))

class SecretSharing:
    """Shamir秘密共享（简化版，用于演示）"""
    def __init__(self, threshold=3, total_shares=5, prime=257):
        self.threshold = threshold
        self.total = total_shares
        self.prime = prime

    def split(self, secret_hex: str) -> Dict[int, str]:
        secret_int = int(secret_hex, 16) % self.prime
        coeffs = [secret_int] + [secrets.randbelow(self.prime) for _ in range(self.threshold-1)]
        shares = {}
        for x in range(1, self.total+1):
            y = 0
            for p, c in enumerate(coeffs):
                y = (y + c * pow(x, p, self.prime)) % self.prime
            shares[x] = f"{x}:{y}"
        return shares

    def recover(self, shares: Dict[int, str]) -> str:
        points = [(int(k), int(v.split(':')[1])) for k, v in shares.items()]
        if len(points) < self.threshold:
            raise ValueError("份额不足")
        secret = 0
        for i, (xi, yi) in enumerate(points[:self.threshold]):
            li = 1
            for j, (xj, _) in enumerate(points[:self.threshold]):
                if i != j:
                    li = li * (0 - xj) * pow(xi - xj, -1, self.prime) % self.prime
            secret = (secret + yi * li) % self.prime
        return hex(secret)[2:].zfill(64)

class QuantumRing:
    def __init__(self, user_id: str = "default", data_dir: str = "data"):
        self.user_id = user_id
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

        self.master_key = None
        self.session_key = None
        self.session_expiry = 0
        self.authenticated = False

        self.behavior_ai = SimpleBehaviorAI()
        self.secret_sharing = SecretSharing()
        self.secret_shares = {}

        self._load_state()

    def initialize(self, passphrase: Optional[str] = None) -> str:
        if passphrase:
            salt = secrets.token_bytes(16)
            dk = hashlib.pbkdf2_hmac('sha256', passphrase.encode(), salt, 100000, dklen=32)
            self.master_key = dk.hex()
        else:
            self.master_key = secrets.token_hex(32)
        self.secret_shares = self.secret_sharing.split(self.master_key)
        self._save_state()
        return self.master_key[:16] + "..."

    def authenticate(self, features: Optional[List[float]] = None) -> Tuple[bool, float]:
        if features is None:
            features = [np.random.randn() for _ in range(10)]  # 模拟特征
        self.behavior_ai.update(features)
        confidence = self.behavior_ai.confidence(features)

        # 验证秘密共享（取前3份验证）
        if self.secret_shares and len(self.secret_shares) >= 3:
            subset = dict(list(self.secret_shares.items())[:3])
            recovered = self.secret_sharing.recover(subset)
            if recovered != self.master_key:
                return False, 0.0

        if confidence > 0.6:
            self.session_key = secrets.token_hex(32)
            self.session_expiry = time.time() + 3600
            self.authenticated = True
            self._save_state()
            return True, confidence
        return False, confidence

    def check_session(self) -> bool:
        return self.authenticated and time.time() < self.session_expiry

    def get_session_token(self) -> Optional[str]:
        if not self.check_session():
            return None
        return hashlib.sha256(f"{self.user_id}|{self.session_key}".encode()).hexdigest()

    def encrypt(self, data: str) -> str:
        if not self.check_session():
            raise Exception("未认证")
        key = hashlib.sha3_256(self.session_key.encode()).digest()
        data_bytes = data.encode()
        key_stream = b""
        while len(key_stream) < len(data_bytes):
            key_stream += hashlib.sha3_256(key_stream[-32:] + key).digest()
        encrypted = bytes(a ^ b for a, b in zip(data_bytes, key_stream[:len(data_bytes)]))
        import base64
        return base64.b64encode(encrypted).decode()

    def decrypt(self, encrypted_b64: str) -> str:
        if not self.check_session():
            raise Exception("未认证")
        import base64
        encrypted = base64.b64decode(encrypted_b64)
        key = hashlib.sha3_256(self.session_key.encode()).digest()
        key_stream = b""
        while len(key_stream) < len(encrypted):
            key_stream += hashlib.sha3_256(key_stream[-32:] + key).digest()
        decrypted = bytes(a ^ b for a, b in zip(encrypted, key_stream[:len(encrypted)]))
        return decrypted.decode()

    def _save_state(self):
        state = {
            'user_id': self.user_id,
            'master_key': self.master_key,
            'secret_shares': {k: v for k, v in self.secret_shares.items()},
            'authenticated': self.authenticated,
            'session_expiry': self.session_expiry,
            'behavior_history': list(self.behavior_ai.history)
        }
        with open(os.path.join(self.data_dir, f"{self.user_id}_ring.json"), 'w') as f:
            json.dump(state, f, indent=2)

    def _load_state(self):
        path = os.path.join(self.data_dir, f"{self.user_id}_ring.json")
        if not os.path.exists(path):
            return
        with open(path, 'r') as f:
            state = json.load(f)
        self.master_key = state.get('master_key')
        self.secret_shares = {int(k): v for k, v in state.get('secret_shares', {}).items()}
        self.authenticated = state.get('authenticated', False)
        self.session_expiry = state.get('session_expiry', 0)
        self.behavior_ai.history = deque(state.get('behavior_history', []), maxlen=100)
        # 重建行为模型
        if len(self.behavior_ai.history) >= 10:
            arr = np.array(self.behavior_ai.history)
            self.behavior_ai.mean = np.mean(arr, axis=0)
            self.behavior_ai.std = np.std(arr, axis=0) + 1e-8
