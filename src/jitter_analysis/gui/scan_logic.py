from __future__ import annotations

import random


def parse_manual_scan_values(text: str) -> list[float]:
    raw_tokens = []
    for chunk in text.replace("\n", ",").replace(";", ",").split(","):
        token = chunk.strip()
        if token:
            raw_tokens.append(token)
    if not raw_tokens:
        raise ValueError("Enter one or more scan values, for example: -0.2, -0.1, 0.0, 0.1")
    try:
        return [float(token) for token in raw_tokens]
    except ValueError as exc:
        raise ValueError("Scan values must be numeric, separated by commas.") from exc


def generate_values_by_step(start: float, stop: float, step: float) -> list[float]:
    if step <= 0:
        raise ValueError("Step must be positive.")
    if start == stop:
        return [start]

    direction = 1.0 if stop >= start else -1.0
    delta = direction * abs(step)
    values = []
    current = start
    epsilon = abs(step) * 1.0e-6
    while (direction > 0 and current <= stop + epsilon) or (direction < 0 and current >= stop - epsilon):
        values.append(current)
        current += delta

    if not values:
        values = [start]
    if abs(values[-1] - stop) > epsilon:
        values.append(stop)
    return values


def generate_values_by_points(start: float, stop: float, num_points: int) -> list[float]:
    if num_points <= 0:
        raise ValueError("Num points must be positive.")
    if num_points == 1:
        return [start]
    step = (stop - start) / float(num_points - 1)
    return [start + step * index for index in range(num_points)]


def generate_random_targets(knob_ranges, distribution: str, num_points: int, seed: int):
    if num_points <= 0:
        raise ValueError("Num points must be positive.")
    rng = random.Random(seed)
    target_steps = []
    for _ in range(num_points):
        step_targets = {}
        for spec in knob_ranges:
            knob = spec["knob"]
            low = float(spec["low"])
            high = float(spec["high"])
            if low == high:
                value = low
            elif distribution == "uniform":
                value = rng.uniform(low, high)
            elif distribution == "normal_clipped":
                center = (low + high) / 2.0
                sigma = abs(high - low) / 6.0
                raw_value = center if sigma <= 0 else rng.gauss(center, sigma)
                value = min(max(raw_value, low), high)
            else:
                raise ValueError(f"Unsupported random distribution: {distribution}")
            step_targets[knob.id] = value
        target_steps.append(step_targets)
    return target_steps
