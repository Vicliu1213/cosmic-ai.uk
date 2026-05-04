import hashlib
import json
import time
from typing import Any, Dict, Optional


class MemoryMatrix:
    def __init__(self, short_term_limit: int = 1000, retention_seconds: int = 7 * 86400):
        self.short_term_limit = short_term_limit
        self.retention_seconds = retention_seconds
        self.l1 = {}  # pending / active patterns
        self.l2 = []  # short-term history
        self.l3 = {}  # long-term memory

    def _make_hash(self, pattern: Dict[str, Any]) -> str:
        if pattern.get('hash'):
            return str(pattern['hash'])
        payload = {
            'symbol': pattern.get('symbol'),
            'action': pattern.get('action'),
            'entry': pattern.get('entry'),
            'price': pattern.get('price'),
        }
        encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode('utf-8')
        return hashlib.sha1(encoded).hexdigest()[:16]

    def _remember_short_term(self, entry: Dict[str, Any]) -> None:
        self.l2.append(entry)
        if len(self.l2) > self.short_term_limit:
            self.l2 = self.l2[-self.short_term_limit:]

    def recall(self, vector: Optional[Dict[str, Any]], top_k: int = 5):
        now = time.time()
        candidates = []
        for pattern_hash, item in self.l3.items():
            score = item['confidence'] * (0.99 ** max(0, now - item['last_seen']))
            candidates.append((score, {
                'hash': pattern_hash,
                **item,
            }))
        candidates.sort(key=lambda item: item[0], reverse=True)
        return [candidate[1] for candidate in candidates[:top_k]]

    def commit(self, pattern: Dict[str, Any], outcome: Optional[Dict[str, Any]] = None, win: Optional[bool] = None):
        now = time.time()
        pattern_hash = self._make_hash(pattern)
        entry = {
            'hash': pattern_hash,
            'symbol': pattern.get('symbol'),
            'action': pattern.get('action', 'observe'),
            'confidence': float(pattern.get('confidence', 0.5)),
            'entry': pattern.get('entry', pattern.get('price')),
            'outcome': outcome or {},
            'win': win,
            'last_seen': now,
        }
        self._remember_short_term(entry)

        if win is None:
            self.l1[pattern_hash] = entry
            return {'status': 'pending', 'hash': pattern_hash}

        existing = self.l3.get(pattern_hash, {
            'action': entry['action'],
            'confidence': entry['confidence'],
            'last_seen': now,
            'wins': 0,
            'losses': 0,
            'symbol': entry['symbol'],
            'entry': entry['entry'],
        })

        if win:
            existing['confidence'] = min(1.0, max(existing['confidence'], entry['confidence']) + 0.05)
            existing['wins'] += 1
            status = 'promoted'
        else:
            existing['confidence'] = max(0.0, existing['confidence'] - 0.1)
            existing['losses'] += 1
            status = 'degraded'

        existing['last_seen'] = now
        existing['symbol'] = entry['symbol']
        existing['entry'] = entry['entry']
        existing['action'] = entry['action']

        if existing['confidence'] < 0.3 and existing['losses'] > existing['wins']:
            self.l3.pop(pattern_hash, None)
            status = 'evicted'
        else:
            self.l3[pattern_hash] = existing

        self.l1.pop(pattern_hash, None)
        return {'status': status, 'hash': pattern_hash, 'confidence': existing.get('confidence', 0.0)}

    def forget(self):
        now = time.time()
        before = len(self.l3)
        self.l3 = {
            key: value for key, value in self.l3.items()
            if now - value['last_seen'] < self.retention_seconds
        }
        removed = before - len(self.l3)
        return {'removed': removed, 'remaining': len(self.l3)}

    def status(self):
        return {
            'pending_patterns': len(self.l1),
            'short_term_items': len(self.l2),
            'long_term_items': len(self.l3),
        }