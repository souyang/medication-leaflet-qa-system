"""W&B evaluation runner."""

import logging
import re
import time
from typing import Any

import httpx
import wandb
from rag_health_core import Settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EVAL_DATASET = [
    {
        "query": "What is the recommended starting dose of metformin?",
        "drug": "metformin",
        "expected_section": "DOSAGE_AND_ADMINISTRATION",
        "expected_unit": "mg",
    },
    {
        "query": "What are the contraindications for lisinopril?",
        "drug": "lisinopril",
        "expected_section": "CONTRAINDICATIONS",
    },
    {
        "query": "What adverse reactions are associated with atorvastatin?",
        "drug": "atorvastatin",
        "expected_section": "ADVERSE_REACTIONS",
    },
    {
        "query": "How should levothyroxine be stored?",
        "drug": "levothyroxine",
        "expected_section": "HOW_SUPPLIED_STORAGE_AND_HANDLING",
    },
    {
        "query": "What should patients be counseled about when taking amlodipine?",
        "drug": "amlodipine",
        "expected_section": "PATIENT_COUNSELING_INFORMATION",
    },
    {
        "query": "Is metformin safe in renal impairment?",
        "drug": "metformin",
        "expected_section": "WARNINGS_AND_PRECAUTIONS",
    },
    {
        "query": "What is the maximum daily dose of lisinopril?",
        "drug": "lisinopril",
        "expected_section": "DOSAGE_AND_ADMINISTRATION",
        "expected_unit": "mg",
    },
]


class EvalRunner:
    """W&B evaluation runner for RAG pipeline."""

    def __init__(self, settings: Settings, api_base: str = "http://localhost:8000") -> None:
        """Initialize eval runner."""
        self.settings = settings
        self.api_base = api_base
        self.client = httpx.Client(timeout=30.0)

    def run(self) -> dict[str, Any]:
        """Run evaluation suite and log to W&B."""
        wandb.init(
            project=self.settings.wandb_project,
            entity=self.settings.wandb_entity,
            job_type="eval",
        )

        results = []
        total_latency = 0.0

        for item in EVAL_DATASET:
            result = self._eval_query(item)
            results.append(result)
            total_latency += result["latency_ms"]

        # Compute metrics
        metrics = self._compute_metrics(results)

        # Log to W&B
        wandb.log(metrics)

        # Create table
        table = wandb.Table(
            columns=["query", "drug", "answer", "grounded", "has_citation", "latency_ms"],
            data=[
                [
                    r["query"],
                    r["drug"],
                    r["answer"][:100] + "..." if len(r["answer"]) > 100 else r["answer"],
                    r["grounded"],
                    r["has_citation"],
                    r["latency_ms"],
                ]
                for r in results
            ],
        )
        wandb.log({"eval_results": table})

        wandb.finish()

        return metrics

    def _eval_query(self, item: dict[str, Any]) -> dict[str, Any]:
        """Evaluate a single query."""
        query = item["query"]
        drug = item.get("drug")

        # Call API
        start = time.time()
        try:
            response = self.client.post(
                f"{self.api_base}/ask",
                json={"query": query, "drug": drug, "top_k": 6},
            )
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            return {
                "query": query,
                "drug": drug,
                "answer": f"Error: {e}",
                "grounded": False,
                "has_citation": False,
                "latency_ms": 0.0,
            }

        latency_ms = (time.time() - start) * 1000

        answer = data.get("answer", "")
        contexts = data.get("contexts", [])

        # Check grounding
        grounded = len(contexts) > 0 and "Not in the label context provided" not in answer

        # Check citations
        has_citation = bool(re.search(r"\[Section:.*?\]\s*\(.*?#section=.*?\)", answer))

        return {
            "query": query,
            "drug": drug,
            "answer": answer,
            "grounded": grounded,
            "has_citation": has_citation,
            "latency_ms": latency_ms,
        }

    def _compute_metrics(self, results: list[dict[str, Any]]) -> dict[str, float]:
        """Compute aggregate metrics."""
        total = len(results)
        grounded_count = sum(1 for r in results if r["grounded"])
        citation_count = sum(1 for r in results if r["has_citation"])

        latencies = [r["latency_ms"] for r in results]
        latencies.sort()

        p50 = latencies[len(latencies) // 2] if latencies else 0.0
        p95 = latencies[int(len(latencies) * 0.95)] if latencies else 0.0

        return {
            "grounding_rate": grounded_count / total if total > 0 else 0.0,
            "citation_rate": citation_count / total if total > 0 else 0.0,
            "p50_latency_ms": p50,
            "p95_latency_ms": p95,
            "avg_latency_ms": sum(latencies) / len(latencies) if latencies else 0.0,
        }


def main() -> None:
    """Main entry point."""
    settings = Settings()
    runner = EvalRunner(settings)
    metrics = runner.run()

    logger.info("\n=== Eval Results ===")
    for key, value in metrics.items():
        logger.info(f"{key}: {value:.3f}")


if __name__ == "__main__":
    main()
