"""요구사항 03·08: 모드 2 - data.json 로드, 검증, 일괄 판정, 결과 요약."""

import json

from src.judge import EPSILON, UNDECIDED, judge, normalize_label
from src.mac import mac
from src.matrix import is_square, make_cross, make_x
from src.mode_input import print_section
from src.perf import (measure_mac_flat_ms, measure_mac_ms,
                      print_flat_compare_table, print_perf_table)

# 실패 분류 태그
CAT_SCHEMA = "데이터/스키마"
CAT_LOGIC = "로직"
CAT_NUMERIC = "수치 비교"


def load_data(path):
    """JSON 파일을 읽는다. 파일이 없거나 깨졌으면 안내 후 None 반환."""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("오류: '%s' 파일을 찾을 수 없습니다." % path)
    except json.JSONDecodeError as e:
        print("오류: JSON 파싱 실패 (%s)" % e)
    return None


def parse_size_from_key(key):
    """'size_13' 또는 'size_13_1'에서 13을 꺼낸다. 규칙 위반이면 None."""
    parts = str(key).split("_")
    if len(parts) < 2 or parts[0] != "size":
        return None
    try:
        n = int(parts[1])
    except ValueError:
        return None
    return n if n > 0 else None


def is_numeric_matrix(matrix):
    for row in matrix:
        for v in row:
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                return False
    return True


def load_filters(raw_filters):
    """filters 섹션을 {N: {'Cross': 필터, 'X': 필터}}로 정규화해 반환한다."""
    filters = {}
    if not isinstance(raw_filters, dict):
        print("오류: filters 섹션이 없거나 형식이 잘못되었습니다.")
        return filters
    for key, group in raw_filters.items():
        n = parse_size_from_key(key)
        if n is None or not isinstance(group, dict):
            print("[ERROR] %s: 필터 키/형식 규칙 위반 -> 건너뜀" % key)
            continue
        loaded = {}
        for label_key, matrix in group.items():
            label = normalize_label(label_key)
            if label is None:
                print("[ERROR] %s.%s: 알 수 없는 필터 라벨 -> 건너뜀" % (key, label_key))
            elif not is_square(matrix, n) or not is_numeric_matrix(matrix):
                print("[ERROR] %s.%s: %dx%d 숫자 배열이 아님 -> 건너뜀" % (key, label_key, n, n))
            else:
                loaded[label] = matrix
        filters[n] = loaded
        if "Cross" in loaded and "X" in loaded:
            print("[OK] %-8s 필터 로드 완료 (Cross, X)" % key)
        else:
            print("[ERROR] %s: Cross/X 필터가 모두 필요합니다 (로드됨: %s)"
                  % (key, ", ".join(sorted(loaded)) or "없음"))
    return filters


def make_result(case_id, status, reason="", category="",
                score_cross=None, score_x=None, verdict="-", expected="-"):
    return {
        "id": case_id, "status": status, "reason": reason, "category": category,
        "score_cross": score_cross, "score_x": score_x,
        "verdict": verdict, "expected": expected,
    }


def run_case(case_id, case, filters):
    """패턴 1건을 판정한다. 예외를 밖으로 던지지 않고 FAIL + 사유로 기록한다."""
    def fail(reason, category=CAT_SCHEMA, **kw):
        return make_result(case_id, "FAIL", reason, category, **kw)

    n = parse_size_from_key(case_id)
    if n is None:
        return fail("키 규칙 위반 (size_{N}_{idx} 형식이 아님)")
    if not isinstance(case, dict) or "input" not in case or "expected" not in case:
        return fail("input 또는 expected 항목 누락")

    expected = normalize_label(case["expected"])
    if expected is None:
        return fail("알 수 없는 expected 라벨: %r" % (case["expected"],))

    group = filters.get(n)
    if not group or "Cross" not in group or "X" not in group:
        return fail("size_%d 필터 없음" % n, expected=expected)

    pattern = case["input"]
    if not is_square(pattern, n):
        return fail("패턴 크기 불일치 (키는 %dx%d)" % (n, n), expected=expected)
    if not is_numeric_matrix(pattern):
        return fail("패턴에 숫자가 아닌 값 포함", expected=expected)

    try:
        score_cross = mac(pattern, group["Cross"])
        score_x = mac(pattern, group["X"])
    except Exception as e:  # 예상 못한 데이터 문제도 케이스 단위 FAIL로 처리
        return fail("MAC 연산 오류: %s" % e, expected=expected)

    verdict = judge(score_cross, score_x)
    scores = {"score_cross": score_cross, "score_x": score_x,
              "verdict": verdict, "expected": expected}
    if verdict == expected:
        return make_result(case_id, "PASS", **scores)
    if verdict == UNDECIDED:
        return fail("동점 (|%r - %r| < %g)" % (score_cross, score_x, EPSILON),
                    CAT_NUMERIC, **scores)
    return fail("판정(%s)과 expected(%s) 불일치" % (verdict, expected), CAT_LOGIC, **scores)


def print_case(result):
    print("--- %s ---" % result["id"])
    if result["score_cross"] is not None:
        print("Cross 점수:", result["score_cross"])
        print("X 점수:", result["score_x"])
    line = "판정: %s | expected: %s | %s" % (
        result["verdict"], result["expected"], result["status"])
    if result["status"] == "FAIL":
        line += " (%s: %s)" % (result["category"], result["reason"])
    print(line)


def run_performance(filters):
    """3×3(생성 패턴) + data.json의 각 크기에 대해 10회 평균 시간을 측정한다."""
    targets = [(3, make_cross(3), make_cross(3))]
    for n in sorted(filters):
        group = filters[n]
        if "Cross" in group:
            targets.append((n, make_x(n), group["Cross"]))

    rows = []
    flat_rows = []
    for n, pattern, filt in targets:
        ms_2d = measure_mac_ms(pattern, filt)
        rows.append((n, ms_2d))
        flat_rows.append((n, ms_2d, measure_mac_flat_ms(pattern, filt)))

    print_section("[3] 성능 분석 (평균/10회)")
    print_perf_table(rows)
    print("\n(보너스) 2차원 vs 1차원 MAC 비교 (동일 입력, 각 10회 평균)")
    print_flat_compare_table(flat_rows)


def print_summary(results):
    passed = [r for r in results if r["status"] == "PASS"]
    failed = [r for r in results if r["status"] == "FAIL"]

    print_section("[4] 결과 요약")
    print("총 테스트: %d개" % len(results))
    print("통과: %d개" % len(passed))
    print("실패: %d개" % len(failed))
    if failed:
        print("\n실패 케이스:")
        for r in failed:
            print("- %s [%s] %s" % (r["id"], r["category"], r["reason"]))
        counts = {}
        for r in failed:
            counts[r["category"]] = counts.get(r["category"], 0) + 1
        print("\n실패 분류: " + ", ".join("%s %d건" % kv for kv in counts.items()))
    print('\n(상세 원인 분석 및 복잡도 설명은 README.md의 "결과 리포트" 섹션 참고)')


def run(path="data.json"):
    data = load_data(path)
    if data is None:
        return
    if not isinstance(data, dict):
        print("오류: data.json 최상위가 객체({})가 아닙니다.")
        return

    print_section("[1] 필터 로드")
    filters = load_filters(data.get("filters"))

    print_section("[2] 패턴 분석 (라벨 정규화 적용)")
    patterns = data.get("patterns")
    results = []
    if not isinstance(patterns, dict):
        print("오류: patterns 섹션이 없거나 형식이 잘못되었습니다.")
    else:
        for case_id, case in patterns.items():
            result = run_case(case_id, case, filters)
            results.append(result)
            print_case(result)

    run_performance(filters)
    print_summary(results)
