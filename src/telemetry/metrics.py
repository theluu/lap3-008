import time
from typing import Dict, Any, List
from src.telemetry.logger import logger

class PerformanceTracker:
    """
    Tracking industry-standard metrics for LLMs.
    """
    def __init__(self):
        self.session_metrics = []

    def track_request(self, provider: str, model: str, usage: Dict[str, int], latency_ms: int):
        """
        Logs a single request metric to our telemetry.
        """
        metric = {
            "provider": provider,
            "model": model,
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
            "latency_ms": latency_ms,
            "cost_estimate": self._calculate_cost(model, usage) # Mock cost calculation
        }
        self.session_metrics.append(metric)
        logger.log_event("LLM_METRIC", metric)

    def _calculate_cost(self, model: str, usage: Dict[str, int]) -> float:
        """Real OpenAI pricing (per 1M tokens, as of 2025)."""
        pricing = {
            # OpenAI — input_per_1m, output_per_1m
            "gpt-4o":              (2.50,  10.00),
            "gpt-4o-mini":         (0.15,   0.60),
            "gpt-4-turbo":         (10.00, 30.00),
            "gpt-3.5-turbo":       (0.50,   1.50),
            # Gemini
            "gemini-2.0-flash":    (0.10,   0.40),
            "gemini-1.5-flash":    (0.075,  0.30),
            "gemini-1.5-pro":      (1.25,   5.00),
        }
        # Default fallback nếu không match model
        input_rate, output_rate = pricing.get(model, (1.00, 3.00))
        prompt_cost = (usage.get("prompt_tokens", 0) / 1_000_000) * input_rate
        completion_cost = (usage.get("completion_tokens", 0) / 1_000_000) * output_rate
        return round(prompt_cost + completion_cost, 6)

    @property
    def total_tokens(self) -> int:
        return sum(m["total_tokens"] for m in self.session_metrics)

    @property
    def total_cost(self) -> float:
        return round(sum(m["cost_estimate"] for m in self.session_metrics), 6)

# Global tracker instance
tracker = PerformanceTracker()
