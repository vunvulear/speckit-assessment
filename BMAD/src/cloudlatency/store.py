"""In-memory store for latency measurement results."""

from __future__ import annotations

from cloudlatency.models import LatencyResult, Status


def _latency_sort_key(result: LatencyResult) -> tuple[bool, float]:
    """Sort key placing None-latency results last."""
    return (result.latency_ms is None, result.latency_ms if result.latency_ms is not None else float("inf"))


def _provider_summary(reachable: list[LatencyResult], total_count: int) -> dict:
    """Build a summary dict for a single provider from its reachable results."""
    if not reachable:
        return {
            "average_latency_ms": None,
            "closest_region": None,
            "closest_latency_ms": None,
            "total_regions": total_count,
            "reachable_regions": 0,
        }
    avg = sum(r.latency_ms for r in reachable) / len(reachable)  # type: ignore[arg-type]
    closest = min(reachable, key=lambda r: r.latency_ms)  # type: ignore[arg-type]
    return {
        "average_latency_ms": round(avg, 2),
        "closest_region": closest.region,
        "closest_latency_ms": closest.latency_ms,
        "total_regions": total_count,
        "reachable_regions": len(reachable),
    }


class LatencyStore:
    """Thread-safe in-memory store for latency results.

    All results are replaced atomically on each measurement cycle.
    Read operations never mutate state.
    """

    def __init__(self) -> None:
        self._results: dict[str, LatencyResult] = {}

    def update_all(self, results: list[LatencyResult]) -> None:
        """Replace all stored results atomically with a new measurement cycle."""
        self._results = {f"{r.provider}:{r.region}": r for r in results}

    def get_all_sorted(self) -> list[LatencyResult]:
        """Return all results sorted by latency ascending.

        Unreachable/error results (latency_ms=None) sort to the end.
        """
        return sorted(self._results.values(), key=_latency_sort_key)

    def get_by_provider(self, provider: str) -> list[LatencyResult]:
        """Return results for a specific provider, sorted by latency ascending."""
        filtered = [r for r in self._results.values() if r.provider == provider]
        return sorted(filtered, key=_latency_sort_key)

    def get_summary(self) -> dict:
        """Compute vendor averages and closest region per provider."""
        all_results = list(self._results.values())
        provider_names = sorted({r.provider for r in all_results})
        providers: dict[str, dict] = {}
        for provider in provider_names:
            total = [r for r in all_results if r.provider == provider]
            reachable = [r for r in total if r.status == Status.OK and r.latency_ms is not None]
            providers[provider] = _provider_summary(reachable, len(total))
        return {"providers": providers}

    def is_empty(self) -> bool:
        """Return True if no results are stored."""
        return len(self._results) == 0

    def count(self) -> int:
        """Return the number of stored results."""
        return len(self._results)
