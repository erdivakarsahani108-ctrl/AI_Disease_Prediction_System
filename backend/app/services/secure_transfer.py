
from __future__ import annotations
import hashlib, secrets
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db.models import OtpChallenge, OwnershipTransfer, Organization, OrganizationMember, AuditEvent, User

OTP_TTL_MIN=10
MAX_ATTEMPTS=5

def _hash(v: str)->str:
    return hashlib.sha256(v.encode()).hexdigest()

def issue_otp(db: Session, user_id: str, purpose: str, channel: str, destination: str):
    code=f"{secrets.randbelow(1_000_000):06d}"
    ch=OtpChallenge(user_id=user_id,purpose=purpose,channel=channel,
                    destination_hash=_hash(destination.lower().strip()),
                    code_hash=_hash(code),expires_at=datetime.utcnow()+timedelta(minutes=OTP_TTL_MIN))
    db.add(ch); db.commit(); db.refresh(ch)
    # In production, send via verified email/SMS provider. Never expose the code.
    return ch, code

def verify_otp(db: Session, challenge_id: str, code: str, user_id: str):
    ch=db.query(OtpChallenge).filter(OtpChallenge.id==challenge_id,
                                     OtpChallenge.user_id==user_id,
                                     OtpChallenge.consumed==False).first()
    if not ch: return False, "Invalid challenge"
    if ch.expires_at < datetime.utcnow(): return False, "Challenge expired"
    if ch.attempts >= MAX_ATTEMPTS: return False, "Too many attempts"
    ch.attempts += 1
    if _hash(code) != ch.code_hash:
        db.commit(); return False, "Invalid code"
    ch.consumed=True; db.commit()
    return True, "verified"

def audit(db, actor, action, target_type=None, target_id=None, org=None, metadata=None):
    db.add(AuditEvent(actor_user_id=actor, action=action, target_type=target_type,
                      target_id=target_id, organization_id=org, metadata_json=metadata or {}))
    db.commit()
