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

    # Pricing per 1M tokens: (input_$/1M, output_$/1M)
    PRICING = {
        "gpt-4o-mini":        (0.15,  0.60),
        "gpt-4o":             (2.50, 10.00),
        "gemini-1.5-flash":   (0.075, 0.30),
        "gemini-1.5-pro":     (1.25,  5.00),
        "gemini-2.0-flash":   (0.10,  0.40),
    }

    def _calculate_cost(self, model: str, usage: Dict[str, int]) -> float:
        input_tokens  = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        price_in, price_out = self.PRICING.get(model, (0.01, 0.01))
        return (input_tokens * price_in + output_tokens * price_out) / 1_000_000

# Global tracker instance
tracker = PerformanceTracker()
