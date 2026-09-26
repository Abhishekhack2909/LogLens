"""Deterministic anomaly detection module for LogLens.

Evaluates hourly error counts against configurable thresholds and baseline rates.
Note: This module implements deterministic statistical thresholding and does NOT
use machine learning or probabilistic black-box models.
"""

from __future__ import annotations

from typing import Mapping

from .models import AnomalyResult


class AnomalyDetector:
    """Detects hourly error spikes using deterministic threshold and multiplier rules.

    Detection Algorithm:
    1. Input: A mapping of hourly time buckets ('YYYY-MM-DD HH:00') to error counts
       (sum of ERROR and CRITICAL entries).
    2. Baseline Calculation:
       - Let N be the number of active hours.
       - If N == 0: baseline error rate is 0.0, no anomalies.
       - If N > 0: baseline_mean = sum(errors) / N.
    3. Sparse & Zero Baseline Handling:
       - Zero baseline (baseline_mean == 0.0): An hour is flagged if error_count >= min_errors.
       - Single-hour log (N == 1): Baseline historical comparator is unavailable;
         an hour is flagged if error_count >= min_errors.
       - Multi-hour non-zero baseline (N >= 2, baseline_mean > 0.0):
         effective_threshold = max(float(min_errors), multiplier * baseline_mean).
         An hour is flagged if error_count >= effective_threshold.
    """

    def __init__(self, min_errors: int = 5, multiplier: float = 2.0) -> None:
        """Initializes the AnomalyDetector.

        Args:
            min_errors: Minimum absolute errors in an hour to qualify as a spike.
            multiplier: Multiplier factor against the hourly baseline error rate.

        Raises:
            ValueError: If min_errors < 1 or multiplier <= 0.0.
        """
        if min_errors < 1:
            raise ValueError(f"min_errors must be an integer >= 1, got {min_errors}")
        if multiplier <= 0.0:
            raise ValueError(f"multiplier must be a positive float > 0.0, got {multiplier}")

        self.min_errors = min_errors
        self.multiplier = float(multiplier)

    def detect_anomalies(self, hourly_errors: Mapping[str, int]) -> tuple[float, list[AnomalyResult]]:
        """Detects anomalous hours from hourly error distribution.

        Args:
            hourly_errors: Mapping of hour string ('YYYY-MM-DD HH:00') to error count.

        Returns:
            A tuple of (baseline_mean, list_of_detected_anomalies).
        """
        if not hourly_errors:
            return 0.0, []

        total_hours = len(hourly_errors)
        total_errors = sum(hourly_errors.values())
        baseline_mean = total_errors / total_hours

        anomalies: list[AnomalyResult] = []

        # Sort hours chronologically for deterministic output
        for hour in sorted(hourly_errors.keys()):
            count = hourly_errors[hour]

            if count < self.min_errors:
                continue

            # Sparse / Single-hour log rule
            if total_hours == 1:
                threshold = float(self.min_errors)
                reason = (
                    f"Sparse baseline (single hour observed): error count ({count}) "
                    f"meets minimum error threshold ({self.min_errors})"
                )
                anomalies.append(
                    AnomalyResult(
                        hour_key=hour,
                        error_count=count,
                        baseline_mean=baseline_mean,
                        threshold=threshold,
                        multiplier=self.multiplier,
                        min_errors=self.min_errors,
                        reason=reason,
                    )
                )
            # Zero-baseline multi-hour rule
            elif baseline_mean == 0.0:
                threshold = float(self.min_errors)
                reason = (
                    f"Zero baseline: error count ({count}) meets minimum error "
                    f"threshold ({self.min_errors}) with zero overall baseline"
                )
                anomalies.append(
                    AnomalyResult(
                        hour_key=hour,
                        error_count=count,
                        baseline_mean=baseline_mean,
                        threshold=threshold,
                        multiplier=self.multiplier,
                        min_errors=self.min_errors,
                        reason=reason,
                    )
                )
            # Multi-hour non-zero baseline rule
            else:
                threshold = max(float(self.min_errors), self.multiplier * baseline_mean)
                if count >= threshold:
                    ratio = count / baseline_mean if baseline_mean > 0 else float("inf")
                    reason = (
                        f"Hourly spike: error count ({count}) exceeded threshold ({threshold:.2f}) "
                        f"[{ratio:.1f}x baseline {baseline_mean:.2f}, min {self.min_errors}]"
                    )
                    anomalies.append(
                        AnomalyResult(
                            hour_key=hour,
                            error_count=count,
                            baseline_mean=baseline_mean,
                            threshold=threshold,
                            multiplier=self.multiplier,
                            min_errors=self.min_errors,
                            reason=reason,
                        )
                    )

        return baseline_mean, anomalies
