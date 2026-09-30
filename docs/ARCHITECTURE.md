# Architecture Overview

## Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14 (App Router), React 18, TypeScript, Tailwind CSS |
| Backend | FastAPI, Pydantic v2, Uvicorn |
| ML | scikit-learn (RandomForest) + rule-based ensemble |
| Database | PostgreSQL + pgvector (ready) |
| Cache | Redis (ready) |
| Auth | JWT (access + refresh) |
| Deploy | Docker Compose |

## Safety Pipeline (mandatory)

```
Input
  → Security / input validation
  → Emergency detection (multi-language patterns)
  → Intent classification
  → Language detection (EN / HI / Hinglish / Bhojpuri)
  → Medical-system classification
  → Context sufficiency check
  → Entity / symptom normalization
  → Hybrid retrieval (knowledge + ML)
  → Evidence / source filtering
  → Medical safety checks
  → Grounded generation
  → Citation verification
  → Uncertainty representation
  → Final safety validator
  → Response + disclaimer
```

## Medical Systems

Knowledge is partitioned by medical system. Claims are never silently merged across systems.

## Extensibility

- New diseases / symptoms → update `DISEASE_SYMPTOMS` + retrain
- New languages → extend `language.py` markers + knowledge content
- Real RAG → plug pgvector + embedding service into retrieval
- Real auth/users → replace in-memory store with SQLAlchemy models

## Important Constraints

- No copyrighted book text is stored or generated.
- No synthetic patient records created to inflate counts.
- All outputs carry explicit uncertainty and disclaimers.
- Emergency content is blocked from normal Q&A paths.
