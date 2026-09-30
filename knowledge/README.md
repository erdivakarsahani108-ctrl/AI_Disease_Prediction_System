# Knowledge Base Notes

This folder is reserved for **copyright-safe, educational** medical knowledge artifacts.

## Rules (from HyperSonic master prompt)

1. Book titles supplied by users are **candidate metadata only**.
2. Editions, sources, licensing/copyright and evidence status must be verified **before** any ingestion.
3. **No copyrighted or unauthorized book text** should be scraped or reproduced.
4. **No fake medical records** should be generated to meet a numeric target.
5. Knowledge is partitioned by medical system; claims are not silently merged.

## Current content

Educational synthetic snippets live inside `backend/app/services/chatbot.py` for the demo.
In production, replace with a proper ingestion pipeline + pgvector store.
