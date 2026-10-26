import argparse
import csv
import tempfile
import unittest
from pathlib import Path

from benchmark_tool import (
    insertion_sort,
    merge_sort,
    parse_sizes,
    run_benchmark,
    write_csv,
    write_svg,
)


class SortingTests(unittest.TestCase):
    def test_algorithms_sort_edge_cases_and_duplicates(self) -> None:
        samples = [[], [1], [4, -2, 4, 0, -2], list(range(20, -1, -1))]
        for algorithm in (insertion_sort, merge_sort):
            for sample in samples:
                with self.subTest(algorithm=algorithm.__name__, sample=sample):
                    result = sample.copy()
                    algorithm(result)
                    self.assertEqual(result, sorted(sample))

    def test_merge_sort_handles_non_power_of_two_lengths(self) -> None:
        for length in range(1, 40):
            sample = [((index * 17) % 23) - 11 for index in range(length)]
            result = sample.copy()
            merge_sort(result)
            self.assertEqual(result, sorted(sample))


class BenchmarkTests(unittest.TestCase):
    def test_parse_sizes_sorts_and_rejects_duplicates(self) -> None:
        self.assertEqual(parse_sizes("100, 10, 50"), [10, 50, 100])
        with self.assertRaises(argparse.ArgumentTypeError):
            parse_sizes("10,10")

    def test_benchmark_skips_quadratic_algorithm_over_limit(self) -> None:
        results = run_benchmark([5, 8], 1, 42, 5, ["insertion", "merge"])
        self.assertEqual(
            [(result.algorithm, result.size, result.status) for result in results],
            [
                ("insertion", 5, "ok"),
                ("merge", 5, "ok"),
                ("insertion", 8, "skipped"),
                ("merge", 8, "ok"),
            ],
        )

    def test_outputs_csv_and_svg(self) -> None:
        results = run_benchmark([4, 8], 1, 7, 4, ["insertion", "merge"])
        with tempfile.TemporaryDirectory() as directory:
            csv_path = Path(directory) / "results.csv"
            svg_path = Path(directory) / "results.svg"
            write_csv(csv_path, results)
            write_svg(svg_path, results)
            with csv_path.open(newline="", encoding="utf-8") as source:
                rows = list(csv.DictReader(source))
            self.assertEqual(len(rows), 4)
            self.assertTrue(svg_path.read_text(encoding="utf-8").startswith("<svg "))


if __name__ == "__main__":
    unittest.main()
