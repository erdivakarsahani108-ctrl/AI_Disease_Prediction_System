"""
Lightweight retrieval over KnowledgeDocument table.
Uses keyword + tag overlap scoring (TF-style). Ready to swap for pgvector embeddings later.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.db.models import KnowledgeDocument


def retrieve(
    db: Session,
    query: str,
    medical_system: Optional[str] = None,
    category: Optional[str] = None,
    top_k: int = 5,
    lang: str = "en",
) -> List[Dict[str, Any]]:
    q = query.lower().strip()
    tokens = set(t for t in q.replace(",", " ").split() if len(t) > 2)

    q_filter = db.query(KnowledgeDocument).filter(KnowledgeDocument.is_verified == True)
    if medical_system:
        q_filter = q_filter.filter(KnowledgeDocument.medical_system == medical_system)
    if category:
        q_filter = q_filter.filter(KnowledgeDocument.category == category)

    docs = q_filter.all()
    scored: List[tuple] = []
    for doc in docs:
        score = 0.0
        tags = [t.lower() for t in (doc.tags or [])]
        title_l = (doc.title or "").lower()
        content_l = (doc.content or "").lower()

        for t in tags:
            if t in q or any(tok in t or t in tok for tok in tokens):
                score += 3.0
        for tok in tokens:
            if tok in title_l:
                score += 2.0
            if tok in content_l:
                score += 0.5
        if score > 0:
            scored.append((score, doc))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = []
    for score, doc in scored[:top_k]:
        content = doc.content_hi if lang in ("hi", "hinglish", "bhojpuri") and doc.content_hi else doc.content
        results.append({
            "id": doc.id,
            "title": doc.title,
            "content": content,
            "medical_system": doc.medical_system,
            "category": doc.category,
            "tags": doc.tags,
            "source": doc.source,
            "evidence_level": doc.evidence_level,
            "score": round(score, 2),
        })
    return results
