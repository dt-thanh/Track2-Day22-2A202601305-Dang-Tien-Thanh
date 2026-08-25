"""Recover interrupted RAGAS generation outputs from LangSmith root traces."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import config
from langsmith import Client

from qa_pairs import QA_PAIRS


def main():
    client = Client(api_key=config.LANGSMITH_API_KEY)
    runs = list(
        client.list_runs(
            project_name=config.LANGSMITH_PROJECT,
            is_root=True,
        )
    )
    sequences = sorted(
        (run for run in runs if run.name == "RunnableSequence"),
        key=lambda run: run.start_time,
    )
    retrievers = sorted(
        (run for run in runs if run.name == "VectorStoreRetriever"),
        key=lambda run: run.start_time,
    )

    expected_count = len(QA_PAIRS) * 2
    if len(sequences) != expected_count or len(retrievers) != expected_count:
        raise RuntimeError(
            "Cần đúng "
            f"{expected_count} answer/retriever root traces, nhận được "
            f"{len(sequences)}/{len(retrievers)}."
        )

    recovered = {"v1": [], "v2": []}
    for index, (sequence, retriever) in enumerate(zip(sequences, retrievers)):
        qa = QA_PAIRS[index % len(QA_PAIRS)]
        question = (sequence.inputs or {}).get("question")
        query = (retriever.inputs or {}).get("query")
        if question != qa["question"] or query != qa["question"]:
            raise RuntimeError(f"Trace order mismatch at index {index}.")

        documents = (retriever.outputs or {}).get("documents", [])
        contexts = [document["page_content"] for document in documents]
        answer = (sequence.outputs or {}).get("output")
        if not answer or not contexts:
            raise RuntimeError(f"Incomplete trace at index {index}.")

        version = "v1" if index < len(QA_PAIRS) else "v2"
        recovered[version].append(
            {
                "question": qa["question"],
                "reference": qa["reference"],
                "answer": answer,
                "contexts": contexts,
            }
        )

    data_dir = Path(__file__).parent.parent / "data"
    for version, results in recovered.items():
        output_path = data_dir / f"ragas_outputs_{version}.json"
        output_path.write_text(
            json.dumps(results, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"✅ Recovered {len(results)} samples → {output_path.name}")


if __name__ == "__main__":
    main()
