import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import json

class KnowledgeBase:
    """宇宙知識庫系統 - 管理所有理論、資料和學習記錄"""
    
    def __init__(self, docs_path: str, cache_dir: Optional[str] = None):
        self.docs_path = docs_path
        self.cache_dir = cache_dir or os.path.join(docs_path, '.cache')
        self.theories = {}
        self.theory_relationships = {}  # 理論之間的關係
        self.theory_metrics = {}  # 每個理論的性能指標
        self.access_history = {}  # 訪問歷史
        self.learning_records = {}  # 學習記錄
        self._init_cache()
        self._load_all()
        self._initialize_builtin_theories()

    def _init_cache(self):
        """初始化快取目錄"""
        os.makedirs(self.cache_dir, exist_ok=True)

    def _initialize_builtin_theories(self):
        """初始化內建理論庫"""
        builtin_theories = {
            "量子糾纏理論": {
                'content': '量子糾纏是指兩個或多個粒子之間存在的一種特殊物理狀態...',
                'category': 'quantum',
                'weight': 1.0,
                'citations': 156
            },
            "交易策略理論": {
                'content': '基於技術分析和風險管理的交易策略體系...',
                'category': 'trading',
                'weight': 0.9,
                'citations': 89
            },
            "共識機制": {
                'content': '分佈式系統中達成一致性的演算法...',
                'category': 'consensus',
                'weight': 0.85,
                'citations': 120
            },
            "遺傳演算法": {
                'content': '基於自然選擇和遺傳機制的優化演算法...',
                'category': 'evolution',
                'weight': 0.95,
                'citations': 200
            },
            "量子退火": {
                'content': '利用量子隧穿效應尋找全局最優解的方法...',
                'category': 'quantum',
                'weight': 0.88,
                'citations': 145
            },
            "風險管理": {
                'content': '量化風險評估和對沖策略...',
                'category': 'trading',
                'weight': 0.92,
                'citations': 178
            }
        }
        
        for name, data in builtin_theories.items():
            if name not in self.theories:
                self.theories[name] = {
                    'filename': 'builtin',
                    'content': data['content'],
                    'summary': data['content'][:200] + '...',
                    'category': data.get('category', 'general'),
                    'weight': data.get('weight', 1.0),
                    'citations': data.get('citations', 0),
                    'created': datetime.now().isoformat(),
                    'last_accessed': None,
                    'reliability_score': 0.8
                }
                self.theory_metrics[name] = {
                    'access_count': 0,
                    'success_rate': 0.8,
                    'avg_computation_time': 0.0,
                    'relevance_score': 0.8
                }

    def _load_all(self):
        """載入所有理論文件"""
        if not os.path.exists(self.docs_path):
            os.makedirs(self.docs_path, exist_ok=True)
            print(f"知識庫路徑已建立: {self.docs_path}")
            return
            
        for filename in os.listdir(self.docs_path):
            if filename.endswith(".md"):
                filepath = os.path.join(self.docs_path, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    theory_name = self._extract_title(content) or filename.replace('.md', '')
                    self.theories[theory_name] = {
                        'filename': filename,
                        'content': content,
                        'summary': self._extract_summary(content),
                        'category': self._extract_category(content),
                        'weight': 1.0,
                        'citations': self._count_citations(content),
                        'created': datetime.now().isoformat(),
                        'last_accessed': None,
                        'reliability_score': 0.75
                    }
                    self.theory_metrics[theory_name] = {
                        'access_count': 0,
                        'success_rate': 0.75,
                        'avg_computation_time': 0.0,
                        'relevance_score': 0.75
                    }
                except Exception as e:
                    print(f"載入文件 {filename} 失敗: {e}")
                    
        print(f"知識庫已載入 {len(self.theories)} 個理論: {', '.join(self.theories.keys())}")

    def _extract_title(self, content: str) -> Optional[str]:
        """提取文件標題"""
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        return match.group(1).strip() if match else None

    def _extract_summary(self, content: str) -> str:
        """提取理論總結"""
        match = re.search(r'## 概述\s+(.+?)(?=\n##|\Z)', content, re.DOTALL)
        if match:
            para = match.group(1).strip().split('\n\n')[0]
            return para[:200] + '...' if len(para) > 200 else para
        return content[:200] + '...' if len(content) > 200 else content

    def _extract_category(self, content: str) -> str:
        """提取理論分類"""
        match = re.search(r'## 分類\s+(.+?)(?=\n##|\Z)', content, re.DOTALL)
        if match:
            return match.group(1).strip().split('\n')[0].lower()
        # 根據內容推斷分類
        keywords = {
            'quantum': ['量子', '糾纏', '退火'],
            'trading': ['交易', '策略', '市場'],
            'consensus': ['共識', '投票', '協議'],
            'evolution': ['演化', '遺傳', '變異']
        }
        content_lower = content.lower()
        for category, words in keywords.items():
            if any(word in content_lower for word in words):
                return category
        return 'general'

    def _count_citations(self, content: str) -> int:
        """計算引用次數"""
        return len(re.findall(r'\[.*?\]\(.*?\)', content))

    def get_theory(self, name: str) -> Optional[Dict[str, Any]]:
        """取得理論詳情並更新訪問記錄"""
        if name in self.theories:
            self.theories[name]['last_accessed'] = datetime.now().isoformat()
            if name in self.theory_metrics:
                self.theory_metrics[name]['access_count'] += 1
            return self.theories[name]
        return None

    def list_theories(self) -> List[str]:
        """列出所有理論"""
        return list(self.theories.keys())

    def get_theories_by_category(self, category: str) -> List[str]:
        """按分類取得理論"""
        return [name for name, data in self.theories.items() 
                if data.get('category') == category]

    def search(self, keyword: str) -> List[str]:
        """搜尋理論"""
        results = []
        keyword_lower = keyword.lower()
        for name, data in self.theories.items():
            if keyword_lower in data['content'].lower() or keyword_lower in name.lower():
                results.append(name)
        return results

    def update_theory_reliability(self, name: str, delta: float):
        """更新理論可靠性分數"""
        if name in self.theories:
            old_score = self.theories[name].get('reliability_score', 0.75)
            new_score = max(0.0, min(1.0, old_score + delta))
            self.theories[name]['reliability_score'] = new_score

    def update_theory_weight(self, name: str, new_weight: float):
        """更新理論權重"""
        if name in self.theories:
            self.theories[name]['weight'] = max(0.0, min(2.0, new_weight))

    def get_theory_metrics(self, name: str) -> Optional[Dict[str, Any]]:
        """取得理論性能指標"""
        return self.theory_metrics.get(name)

    def get_top_theories(self, limit: int = 5) -> List[Tuple[str, float]]:
        """取得最頂級的理論（按權重和可靠性）"""
        scored = []
        for name, data in self.theories.items():
            score = data.get('weight', 1.0) * data.get('reliability_score', 0.75)
            scored.append((name, score))
        return sorted(scored, key=lambda x: x[1], reverse=True)[:limit]

    def relate_theories(self, theory1: str, theory2: str, relationship_type: str = "related"):
        """建立理論之間的關係"""
        if theory1 not in self.theory_relationships:
            self.theory_relationships[theory1] = []
        self.theory_relationships[theory1].append({
            'target': theory2,
            'type': relationship_type,
            'timestamp': datetime.now().isoformat()
        })

    def export_knowledge_snapshot(self, filepath: str):
        """匯出知識快照"""
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'total_theories': len(self.theories),
            'theories': self.theories,
            'metrics': self.theory_metrics,
            'relationships': self.theory_relationships
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(snapshot, f, ensure_ascii=False, indent=2)
