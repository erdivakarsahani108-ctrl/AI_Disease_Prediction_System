# AI-Based Disease Prediction System v4

Educational human-health AI platform with persistent DB, ML evaluation metrics, structured disease knowledge, nutrition, multilingual chatbot, and safety gates.

> **⚠️ NOT a clinical product.** Educational / research use only. Not for diagnosis or treatment decisions.

## Voice & Multimodal (v4)

- Browser **Web Speech API** microphone capture with explicit consent
- `POST /api/v1/voice/scan` — transcript → safety → symptoms → predictions
- `POST /api/v1/multimodal/scan` — text description of image/document (no CV diagnosis claim)
- Quality notes + emergency gates

## UI

Dark cinematic **3D/4D-style** interface: floating orbs, particle field, glass cards with perspective hover, rotating depth rings, gradient glows.

## Quick start

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# other terminal
cd frontend && npm install && npm run dev
```

- App: http://localhost:3000  
- API: http://localhost:8000/docs  

## What v3.1 adds (vs the 100-item gap list)

| Area | Status in v3.1 |
|------|----------------|
| Real dataset CSV + train/val/test | ✅ `data/symptom_disease_dataset.csv` (320 rows, 40 diseases) |
| ML evaluation metrics | ✅ accuracy/precision/recall/F1 + feature importance → `models/metrics_v3.1.json` + `GET /api/v1/metrics/model` |
| Train script | ✅ `scripts/train_and_evaluate.py` |
| SQLAlchemy DB + history | ✅ Users, predictions, chats, nutrition logs |
| Auth JWT + bcrypt + roles | ✅ Persistent (not in-memory) |
| Structured disease knowledge | ✅ risk factors, red flags, specialist, tests, prevention (`disease_knowledge.py`) |
| Knowledge seed + RAG retrieval | ✅ Expanded educational docs + keyword RAG |
| BMI/BMR/TDEE/macros/allergy tips | ✅ |
| Rate limiting | ✅ on predict/chat |
| Alembic skeleton | ✅ `backend/alembic/` |
| Repository pattern | ✅ `repositories/user_repo.py` |
| Unit tests | ✅ `backend/tests/` |
| Frontend login/dashboard/nutrition | ✅ |

## Still intentionally limited (honest)

- **Not** trained on real EHR/clinical datasets (licensing + privacy)
- **Not** official ICD-10/SNOMED licensed content (uses educational codes)
- **Not** a production LLM (deterministic + retrieval; plug your own LLM key if needed)
- **Not** full pgvector embedding stack in this ZIP (architecture ready; needs embedding model)
- **Not** drug–drug interaction DB / dosage engine (safety boundary: we refuse dosage advice)
- **Not** food-image / barcode / Whisper / Zomato integrations
- Metrics on synthetic data ≠ clinical performance

## Retrain model

```bash
cd AI_Disease_Prediction_System
PYTHONPATH=backend python scripts/train_and_evaluate.py
```

## API highlights

| Method | Path | Notes |
|--------|------|-------|
| POST | `/api/v1/auth/register` | Persistent user |
| POST | `/api/v1/predict` | + history if logged in |
| GET | `/api/v1/predict/history` | |
| POST | `/api/v1/chat` | Multilingual + RAG citations |
| POST | `/api/v1/nutrition/calculate` | BMI/BMR/macros |
| GET | `/api/v1/metrics/model` | Train/test metrics |
| GET | `/api/v1/knowledge/disease/{name}` | Red flags, specialist, tests |
| GET | `/api/v1/dashboard` | Stats |

## License / data

No copyrighted book text. No real patient records. Synthetic educational content only.


## V4.1 hardening included in this build
- Server-side prevention of self-assigned privileged roles.
- Verified email/contact OTP challenge storage with expiry, attempt limits and hashed codes.
- Audited organization ownership-transfer workflow.
- Multi-tenant organization/member entities.
- Verified-medicine catalog schema designed for large-scale ingestion.
- Safe scan gateway with explicit consent, quality gates and high-risk human-review flags.
- Security headers and safer CORS behavior.
- Alembic bootstrap migration.
- Frontend Admin, Scan and Medicine knowledge pages.
- Pytest path configuration and quality-gate script.

## Validation
The backend compiles and the existing test suite passes in the build environment. Model artifacts should be retrained/revalidated whenever the production scikit-learn version or training dataset changes.

## Production blockers before clinical deployment
Real verified medical data, external validation, clinical governance, licensed medicine sources, provider-backed email/SMS delivery, secret management, HTTPS, database backups, monitoring, penetration testing and regulatory/legal review remain mandatory.
