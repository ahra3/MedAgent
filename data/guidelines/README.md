# Clinical Guidelines Knowledge Base

## Purpose
These guidelines form the RAG knowledge base for MediAgent's Guidelines RAG Agent.
They are chunked and embedded into ChromaDB for retrieval.

## Sources
All guidelines are from publicly available clinical practice guideline summaries:

| File | Source | Conditions Covered |
|:-----|:-------|:-------------------|
| `diabetes_ada_2025.md` | American Diabetes Association | T2DM, glycemic targets, CKD in diabetes |
| `hypertension_jnc_aha.md` | JNC 8 + ACC/AHA 2024 | Hypertension management, special populations |
| `copd_gold_2025.md` | GOLD 2025 Report | COPD diagnosis, treatment, exacerbations |
| `heart_failure_aha.md` | ACC/AHA 2024 | HF classification, GDMT, comorbidities |
| `ckd_kdigo.md` | KDIGO 2024 | CKD staging, progression, medication adjustments |

## Processing Pipeline 
1. Raw markdown files → chunked (500-800 tokens, ~100 token overlap)
2. Each chunk embedded with metadata (source, section, condition)
3. Stored in ChromaDB for hybrid retrieval (BM25 + vector search)

## Important Notes
- These are curated summaries of public guidelines, not the full guideline documents.
- Clinical recommendations are simplified for demonstration purposes.
- This is NOT intended for actual clinical use.
