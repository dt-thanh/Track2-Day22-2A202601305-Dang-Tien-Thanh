# Evidence Summary — Day 22 Lab

## Prompt V1 vs V2

Prompt V1 performed best overall. Its concise, strictly context-grounded style
reached `0.9791` faithfulness and `0.9186` answer relevancy. Prompt V2 also met
the target with `0.8338` faithfulness, but its longer structured format and
confidence note introduced more claims for the evaluator to verify.

Both versions achieved perfect `1.0000` context recall. Context precision was
also strong and nearly identical (`0.9483` for V1 and `0.9450` for V2), showing
that the FAISS retriever consistently returned useful passages. For this
knowledge base, V1 is the better production default because it is more faithful,
slightly more relevant, and more concise.

## Verified runs

- LangSmith root runs: 301 at verification time.
- Step 1: 50 `rag-query` root traces.
- Step 2: 50 `ab-rag-query` root traces; deterministic routing produced 19 V1
  and 31 V2 requests.
- Step 3: 50 evaluation samples for each prompt and all four required metrics.
- Step 4: six PII cases and five JSON formatting/repair cases completed.
