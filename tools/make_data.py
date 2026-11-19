"""(선택) 연습용 data_sample.json / 예외 처리 확인용 data_error.json 생성기.

data_sample.json은 공식 data.json과 같은 구조와 결과
(필터 3종, 패턴 6개, 그중 3개는 설계된 동점)를 재현한다.
공식 data.json은 절대 덮어쓰지 않는다.
실행: 프로젝트 루트에서  python -m tools.make_data
"""

import json
import os

from src.matrix import make_cross, make_x

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def with_center(matrix, value):
    n = len(matrix)
    matrix[n // 2][n // 2] = value
    return matrix


def build_data():
    filters = {
        # 십자가 필터: 팔 1.0, 가운데 0.9 / X 필터: 대각선 0.1
        "size_5": {"cross": with_center(make_cross(5, 1.0), 0.9),
                   "x": make_x(5, 0.1)},
        # 십자가 필터: 전체 0.3 / X 필터: 대각선 0.3, 가운데 7.5
        "size_13": {"cross": make_cross(13, 0.3),
                    "x": with_center(make_x(13, 0.3), 7.5)},
        # 십자가 필터: 팔 1.0, 가운데 4.9 / X 필터: 대각선 0.1
        "size_25": {"cross": with_center(make_cross(25, 1.0), 4.9),
                    "x": make_x(25, 0.1)},
    }
    patterns = {}
    for n in (5, 13, 25):
        patterns["size_%d_1" % n] = {"input": make_x(n, 1.0), "expected": "x"}
        patterns["size_%d_2" % n] = {"input": make_cross(n, 1.0), "expected": "+"}
    return {"meta": {"version": "1.0", "type": "json"},
            "filters": filters, "patterns": patterns}


def build_error_data():
    """예외 처리 확인용: 정상 1건 + 스키마 오류 4건."""
    data = build_data()
    data["patterns"] = {
        "size_5_2": {"input": make_cross(5, 1.0), "expected": "+"},
        "size_5_9": {"input": make_cross(13, 1.0), "expected": "+"},   # 크기 불일치
        "pattern_1": {"input": make_x(5, 1.0), "expected": "x"},       # 키 규칙 위반
        "size_13_9": {"input": make_x(13, 1.0), "expected": "circle"}, # 알 수 없는 라벨
        "size_7_1": {"input": make_x(7, 1.0), "expected": "x"},        # 필터 없음
    }
    return data


def write(name, data):
    path = os.path.join(ROOT, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print("생성:", path)


if __name__ == "__main__":
    write("data_sample.json", build_data())
    write("data_error.json", build_error_data())
