"""Benchmark quadratic and n-log-n sorting algorithms."""

from __future__ import annotations

import argparse
import csv
import math
import random
import statistics
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


SortFunction = Callable[[list[int]], None]


def insertion_sort(values: list[int]) -> None:
    """Sort values in place using insertion sort."""
    for index in range(1, len(values)):
        value = values[index]
        position = index - 1
        while position >= 0 and values[position] > value:
            values[position + 1] = values[position]
            position -= 1
        values[position + 1] = value


def merge_sort(values: list[int]) -> None:
    """Sort values in place using iterative, stable merge sort."""
    length = len(values)
    if length < 2:
        return

    buffer = values.copy()
    width = 1
    while width < length:
        buffer[:] = values
        for start in range(0, length, 2 * width):
            middle = min(start + width, length)
            end = min(start + 2 * width, length)
            left, right, target = start, middle, start

            while left < middle and right < end:
                if buffer[left] <= buffer[right]:
                    values[target] = buffer[left]
                    left += 1
                else:
                    values[target] = buffer[right]
                    right += 1
                target += 1

            while left < middle:
                values[target] = buffer[left]
                left += 1
                target += 1
            while right < end:
                values[target] = buffer[right]
                right += 1
                target += 1
        width *= 2


ALGORITHMS: dict[str, tuple[SortFunction, str]] = {
    "insertion": (insertion_sort, "O(n^2)"),
    "merge": (merge_sort, "O(n log n)"),
}


@dataclass(frozen=True)
class BenchmarkResult:
    algorithm: str
    complexity: str
    size: int
    trials: int
    status: str
    median_seconds: float | None
    min_seconds: float | None
    max_seconds: float | None


def parse_sizes(value: str) -> list[int]:
    try:
        sizes = [int(part.strip()) for part in value.split(",")]
    except ValueError as error:
        raise argparse.ArgumentTypeError("sizes must be comma-separated integers") from error
    if not sizes or any(size < 1 for size in sizes):
        raise argparse.ArgumentTypeError("every size must be a positive integer")
    if len(set(sizes)) != len(sizes):
        raise argparse.ArgumentTypeError("sizes must not contain duplicates")
    return sorted(sizes)


def write_csv(path: Path, results: list[BenchmarkResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.writer(output)
        writer.writerow(
            [
                "algorithm",
                "complexity",
                "size",
                "trials",
                "status",
                "median_seconds",
                "min_seconds",
                "max_seconds",
            ]
        )
        for result in results:
            writer.writerow(
                [
                    result.algorithm,
                    result.complexity,
                    result.size,
                    result.trials,
                    result.status,
                    result.median_seconds if result.median_seconds is not None else "",
                    result.min_seconds if result.min_seconds is not None else "",
                    result.max_seconds if result.max_seconds is not None else "",
                ]
            )


def write_svg(path: Path, results: list[BenchmarkResult]) -> None:
    measured = [result for result in results if result.status == "ok"]
    if not measured:
        return

    width, height = 900, 560
    left, right, top, bottom = 90, 40, 50, 85
    plot_width = width - left - right
    plot_height = height - top - bottom
    log_sizes = [result.size for result in measured]
    log_times = [result.median_seconds for result in measured if result.median_seconds]
    min_x, max_x = min(log_sizes), max(log_sizes)
    min_y, max_y = min(log_times), max(log_times)
    x_low, x_high = math.log10(min_x), math.log10(max_x)
    y_low, y_high = math.log10(min_y), math.log10(max_y)
    if x_low == x_high:
        x_low, x_high = x_low - 0.5, x_high + 0.5
    if y_low == y_high:
        y_low, y_high = y_low - 0.5, y_high + 0.5

    def coordinates(size: int, seconds: float) -> tuple[float, float]:
        x = left + (math.log10(size) - x_low) / (x_high - x_low) * plot_width
        y = top + (y_high - math.log10(seconds)) / (y_high - y_low) * plot_height
        return x, y

    colors = {"insertion": "#d1495b", "merge": "#00798c"}
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="450" y="28" text-anchor="middle" font-family="sans-serif" font-size="20">Sorting benchmark (log-log scale)</text>',
        f'<path d="M {left} {top} V {height - bottom} H {width - right}" fill="none" stroke="#333"/>',
        f'<text x="450" y="{height - 20}" text-anchor="middle" font-family="sans-serif" font-size="14">Input size n</text>',
        f'<text x="22" y="280" text-anchor="middle" transform="rotate(-90 22 280)" font-family="sans-serif" font-size="14">Median time (seconds)</text>',
    ]

    x_ticks = {min_x, max_x}
    x_ticks.update(10**power for power in range(math.floor(x_low), math.ceil(x_high) + 1) if min_x <= 10**power <= max_x)
    y_ticks = {min_y, max_y}
    y_ticks.update(10**power for power in range(math.floor(y_low), math.ceil(y_high) + 1) if min_y <= 10**power <= max_y)
    for tick in sorted(x_ticks):
        x, _ = coordinates(tick, min_y)
        parts.extend(
            [
                f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{height - bottom}" stroke="#e5e5e5"/>',
                f'<text x="{x:.1f}" y="{height - bottom + 20}" text-anchor="middle" font-family="sans-serif" font-size="11">{tick:g}</text>',
            ]
        )
    for tick in sorted(y_ticks):
        _, y = coordinates(min_x, tick)
        parts.extend(
            [
                f'<line x1="{left}" y1="{y:.1f}" x2="{width - right}" y2="{y:.1f}" stroke="#e5e5e5"/>',
                f'<text x="{left - 10}" y="{y + 4:.1f}" text-anchor="end" font-family="sans-serif" font-size="11">{tick:.2g}</text>',
            ]
        )

    for algorithm, color in colors.items():
        points = sorted(
            (
                coordinates(result.size, result.median_seconds)
                for result in measured
                if result.algorithm == algorithm and result.median_seconds is not None
            ),
            key=lambda point: point[0],
        )
        if not points:
            continue
        point_text = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
        parts.append(f'<polyline points="{point_text}" fill="none" stroke="{color}" stroke-width="2"/>')
        for x, y in points:
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{color}"/>')

    plotted_algorithms = {result.algorithm for result in measured}
    for index, (algorithm, complexity) in enumerate(ALGORITHMS.items()):
        if algorithm not in plotted_algorithms:
            continue
        y = top + 20 + index * 24
        color = colors[algorithm]
        parts.extend(
            [
                f'<line x1="{width - 230}" y1="{y}" x2="{width - 200}" y2="{y}" stroke="{color}" stroke-width="3"/>',
                f'<text x="{width - 192}" y="{y + 5}" font-family="sans-serif" font-size="13">{algorithm} sort ({complexity})</text>',
            ]
        )
    parts.append("</svg>")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(parts), encoding="utf-8")


def run_benchmark(
    sizes: list[int],
    trials: int,
    seed: int,
    max_quadratic_size: int,
    selected_algorithms: list[str],
) -> list[BenchmarkResult]:
    generator = random.Random(seed)
    results: list[BenchmarkResult] = []

    for size in sizes:
        dataset = [generator.randrange(0, max(size * 10, 1)) for _ in range(size)]
        expected = sorted(dataset)
        for name in selected_algorithms:
            algorithm, complexity = ALGORITHMS[name]
            if name == "insertion" and size > max_quadratic_size:
                results.append(BenchmarkResult(name, complexity, size, 0, "skipped", None, None, None))
                print(f"{name:10} n={size:>10,}: skipped (over quadratic size limit {max_quadratic_size:,})")
                continue

            durations: list[float] = []
            for _ in range(trials):
                values = dataset.copy()
                started = time.perf_counter()
                algorithm(values)
                durations.append(time.perf_counter() - started)
                if values != expected:
                    raise RuntimeError(f"{name} sort returned an incorrect result for n={size}")

            result = BenchmarkResult(
                name,
                complexity,
                size,
                trials,
                "ok",
                statistics.median(durations),
                min(durations),
                max(durations),
            )
            results.append(result)
            print(
                f"{name:10} n={size:>10,}: "
                f"median {result.median_seconds:.6f}s "
                f"(min {result.min_seconds:.6f}s, max {result.max_seconds:.6f}s)"
            )
    return results


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare insertion sort O(n^2) with merge sort O(n log n)."
    )
    parser.add_argument(
        "--sizes",
        type=parse_sizes,
        default=parse_sizes("100,1000,5000,10000,100000,1000000"),
        help="comma-separated positive input sizes",
    )
    parser.add_argument("--trials", type=int, default=3, help="number of runs per algorithm and size")
    parser.add_argument("--seed", type=int, default=42, help="seed for reproducible random data")
    parser.add_argument(
        "--max-quadratic-size",
        type=int,
        default=5000,
        help="skip insertion sort above this size (default: 5000)",
    )
    parser.add_argument("--output", type=Path, default=Path("benchmark_results.csv"), help="CSV output path")
    parser.add_argument(
        "--algorithms",
        nargs="+",
        choices=sorted(ALGORITHMS),
        default=list(ALGORITHMS),
        help="algorithms to run",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.trials < 1:
        parser.error("--trials must be at least 1")
    if args.max_quadratic_size < 0:
        parser.error("--max-quadratic-size cannot be negative")

    results = run_benchmark(
        args.sizes,
        args.trials,
        args.seed,
        args.max_quadratic_size,
        args.algorithms,
    )
    write_csv(args.output, results)
    svg_path = args.output.with_suffix(".svg")
    write_svg(svg_path, results)
    print(f"\nCSV saved to: {args.output}")
    if any(result.status == "ok" for result in results):
        print(f"Chart saved to: {svg_path}")


if __name__ == "__main__":
    main()
