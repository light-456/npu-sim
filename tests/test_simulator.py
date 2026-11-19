"""표준 라이브러리 unittest로 핵심 함수를 검증한다.
실행: 프로젝트 루트에서  python -m unittest -v
"""

import os
import unittest

from src.judge import UNDECIDED, judge, normalize_label
from src.mac import mac, mac_flat
from src.matrix import (flatten, get_value, is_square, make_cross, make_matrix,
                        make_x, set_value)
from src.mode_input import parse_number
from src.mode_json import load_data, load_filters, parse_size_from_key, run_case

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CROSS3 = [[0, 1, 0], [1, 1, 1], [0, 1, 0]]
X3 = [[1, 0, 1], [0, 1, 0], [1, 0, 1]]


class MatrixTest(unittest.TestCase):
    def test_make_matrix_rows_are_independent(self):
        m = make_matrix(3)
        set_value(m, 1, 2, 7)
        self.assertEqual(m, [[0, 0, 0], [0, 0, 7], [0, 0, 0]])
        self.assertEqual(get_value(m, 1, 2), 7)

    def test_supported_sizes(self):
        for n in (3, 5, 13, 25):
            self.assertTrue(is_square(make_matrix(n), n))
        self.assertFalse(is_square([[1, 2], [3]], 2))

    def test_pattern_generator(self):
        self.assertEqual(make_cross(3), CROSS3)
        self.assertEqual(make_x(3), X3)
        self.assertEqual(sum(flatten(make_cross(25))), 49)


class MacTest(unittest.TestCase):
    def test_mission_examples(self):
        self.assertEqual(mac(CROSS3, CROSS3), 5)
        self.assertEqual(mac(CROSS3, X3), 1)

    def test_flat_equals_2d(self):
        p, f = make_x(13), make_cross(13, 0.3)
        self.assertEqual(mac(p, f), mac_flat(flatten(p), flatten(f)))


class JudgeTest(unittest.TestCase):
    def test_normalize_label(self):
        self.assertEqual(normalize_label("+"), "Cross")
        self.assertEqual(normalize_label(" cross "), "Cross")
        self.assertEqual(normalize_label("x"), "X")
        self.assertEqual(normalize_label("X"), "X")
        self.assertIsNone(normalize_label("circle"))

    def test_epsilon_tie(self):
        self.assertEqual(judge(0.9, 0.8999999999999999), UNDECIDED)
        self.assertEqual(judge(5.0, 1.0), "Cross")
        self.assertEqual(judge(1.0, 5.0, "A", "B"), "B")

    def test_parse_number(self):
        self.assertEqual(parse_number("3"), 3)
        self.assertEqual(parse_number("0.5"), 0.5)
        for bad in ("a", "nan", "inf"):
            self.assertRaises(ValueError, parse_number, bad)


class JsonModeTest(unittest.TestCase):
    def test_parse_size_from_key(self):
        self.assertEqual(parse_size_from_key("size_13_1"), 13)
        self.assertEqual(parse_size_from_key("size_5"), 5)
        self.assertIsNone(parse_size_from_key("pattern_1"))
        self.assertIsNone(parse_size_from_key("size_x_1"))

    def _run_file(self, name):
        data = load_data(os.path.join(ROOT, name))
        self.assertIsNotNone(data)
        filters = load_filters(data["filters"])
        return {k: run_case(k, v, filters) for k, v in data["patterns"].items()}

    def test_official_data(self):
        results = self._run_file("data.json")
        self.assertEqual(len(results), 6)
        failed = sorted(k for k, r in results.items() if r["status"] == "FAIL")
        self.assertEqual(failed, ["size_13_2", "size_25_1", "size_5_1"])
        for k in failed:
            self.assertEqual(results[k]["verdict"], UNDECIDED)
            self.assertEqual(results[k]["category"], "수치 비교")

    def test_error_data_does_not_crash(self):
        results = self._run_file("data_error.json")
        self.assertEqual(results["size_5_2"]["status"], "PASS")
        for k in ("size_5_9", "pattern_1", "size_13_9", "size_7_1"):
            self.assertEqual(results[k]["status"], "FAIL")
            self.assertEqual(results[k]["category"], "데이터/스키마")

    def test_missing_file(self):
        self.assertIsNone(load_data(os.path.join(ROOT, "no_such_file.json")))


if __name__ == "__main__":
    unittest.main()
