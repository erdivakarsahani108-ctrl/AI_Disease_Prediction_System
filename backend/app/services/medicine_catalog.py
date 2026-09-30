
from __future__ import annotations
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db.models import Medicine

def search_medicines(db: Session, query: str, medical_system: Optional[str]=None,
                     verified_only: bool=True, limit:int=20):
    q=f"%{query.strip()}%"
    filters=[or_(Medicine.canonical_name.ilike(q), Medicine.brand_name.ilike(q),
                 Medicine.manufacturer.ilike(q))]
    if medical_system: filters.append(Medicine.medical_system==medical_system)
    if verified_only: filters.append(Medicine.verified.is_(True))
    return db.query(Medicine).filter(*filters).order_by(Medicine.canonical_name).limit(limit).all()
