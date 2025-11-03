"""
Customer Service Knowledge Base (S3-only)

Simple local JSON storage with in-memory cache.
Categories: company, product_faq, policy, new_release
"""
from __future__ import annotations

import json
import os
from typing import List, Dict, Optional


class CSKnowledgeBase:
    def __init__(self, storage_path: str = "backend/data/cs_kb.json"):
        self.storage_path = storage_path
        self._data: Dict[str, List[Dict]] = {
            "company": [],
            "product_faq": [],
            "policy": [],
            "new_release": []
        }
        self._load()

    def _load(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except Exception:
                pass

    def _save(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def add_entry(self, category: str, title: str, content: str) -> Dict:
        if category not in self._data:
            raise ValueError("invalid category")
        entry = {"id": f"KB_{len(self._data[category]) + 1}", "title": title, "content": content}
        self._data[category].append(entry)
        self._save()
        return entry

    def list_entries(self, category: Optional[str] = None) -> List[Dict]:
        if category:
            return list(self._data.get(category, []))
        # flatten with category
        result: List[Dict] = []
        for cat, items in self._data.items():
            for it in items:
                result.append({**it, "category": cat})
        return result

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        # naive keyword match for demo
        corpus = self.list_entries()
        scored = []
        q = query.lower()
        for it in corpus:
            text = (it.get("title", "") + "\n" + it.get("content", "")).lower()
            score = text.count(q) if q else 0
            if q and q in text:
                score += 1
            if score > 0:
                scored.append((score, it))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [it for _, it in scored[:top_k]]


# singleton
_kb_instance: Optional[CSKnowledgeBase] = None


def get_cs_kb() -> CSKnowledgeBase:
    global _kb_instance
    if _kb_instance is None:
        _kb_instance = CSKnowledgeBase()
    return _kb_instance


