import os
import re

class KnowledgeBase:
    def __init__(self, docs_path):
        self.docs_path = docs_path
        self.theories = {}
        self._load_all()

    def _load_all(self):
        for filename in os.listdir(self.docs_path):
            if not filename.endswith(".md"):
                continue
            if not re.match(r'^\d{2}_.+\.md$', filename):
                continue
            filepath = os.path.join(self.docs_path, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            theory_name = self._extract_title(content) or filename.replace('.md', '')
            self.theories[theory_name] = {
                'filename': filename,
                'content': content,
                'summary': self._extract_summary(content)
            }
        print(f"知識庫已載入 {len(self.theories)} 個理論: {', '.join(self.theories.keys())}")

    def _extract_title(self, content):
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        return match.group(1).strip() if match else None

    def _extract_summary(self, content):
        match = re.search(r'## 概述\s+(.+?)(?=\n##|\Z)', content, re.DOTALL)
        if match:
            para = match.group(1).strip().split('\n\n')[0]
            return para[:200] + '...' if len(para) > 200 else para
        return ""

    def get_theory(self, name):
        return self.theories.get(name)

    def list_theories(self):
        return list(self.theories.keys())

    def search(self, keyword):
        results = []
        for name, data in self.theories.items():
            if keyword in data['content']:
                results.append(name)
        return results
