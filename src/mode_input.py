"""요구사항 02: 모드 1 - 3×3 사용자 입력."""

import math

from src.judge import EPSILON, UNDECIDED, judge
from src.mac import mac
from src.matrix import make_cross, make_x
from src.perf import measure_mac_ms, print_perf_table

SIZE = 3
ERR_COUNT = "입력 형식 오류: 각 줄에 %d개의 숫자를 공백으로 구분해 입력하세요."
ERR_NUMBER = "입력 형식 오류: 숫자가 아닌 값이 있습니다. 숫자만 입력하세요."


def print_section(title):
    print()
    print("#" + "-" * 40)
    print("# " + title)
    print("#" + "-" * 40)


def parse_number(text):
    """int를 먼저 시도하고, 실패하면 float으로 변환한다.
    숫자가 아니거나 nan/inf처럼 비교할 수 없는 값이면 ValueError."""
    try:
        return int(text)
    except ValueError:
        value = float(text)
        if not math.isfinite(value):
            raise ValueError("not a finite number: %s" % text)
        return value


def read_matrix(name, n=SIZE):
    """n줄을 입력받아 n×n 리스트로 반환한다. 형식이 틀리면 안내 후 처음부터 다시 받는다."""
    print("%s (%d줄 입력, 공백 구분)" % (name, n))
    while True:
        rows = []
        ok = True
        for _ in range(n):
            parts = input().split()
            if len(parts) != n:
                print(ERR_COUNT % n)
                ok = False
                break
            try:
                rows.append([parse_number(p) for p in parts])
            except ValueError:
                print(ERR_NUMBER)
                ok = False
                break
        if ok:
            return rows
        print("[%s] 처음부터 다시 입력하세요." % name)


def print_matrix(matrix):
    for row in matrix:
        print("  " + " ".join(str(v) for v in row))


def ask_auto_filters():
    """(보너스 2) 엔터: 직접 입력 / g: 패턴 생성기로 A=십자가, B=X 자동 생성."""
    print("필터 입력 방식 - Enter: 직접 입력 / g: 십자가(A)·X(B) 자동 생성")
    while True:
        choice = input("선택: ").strip().lower()
        if choice in ("", "g"):
            return choice == "g"
        print("Enter 또는 g를 입력하세요.")


def run():
    print_section("[1] 필터 입력")
    if ask_auto_filters():
        filter_a = make_cross(SIZE)
        filter_b = make_x(SIZE)
        print("패턴 생성기로 필터 A(십자가), 필터 B(X)를 만들었습니다.")
    else:
        filter_a = read_matrix("필터 A")
        print()
        filter_b = read_matrix("필터 B")

    print("\n저장 확인:")
    print("필터 A")
    print_matrix(filter_a)
    print("필터 B")
    print_matrix(filter_b)

    print_section("[2] 패턴 입력")
    pattern = read_matrix("패턴")

    score_a = mac(pattern, filter_a)
    score_b = mac(pattern, filter_b)
    ms_a = measure_mac_ms(pattern, filter_a)
    ms_b = measure_mac_ms(pattern, filter_b)

    verdict = judge(score_a, score_b, "A", "B")
    print_section("[3] MAC 결과")
    print("A 점수:", score_a)
    print("B 점수:", score_b)
    print("연산 시간(평균/10회): %.4f ms" % ((ms_a + ms_b) / 2))
    if verdict == UNDECIDED:
        print("판정: 판정 불가 (|A-B| < %g)" % EPSILON)
    else:
        print("판정:", verdict)

    print_section("[4] 성능 분석 (평균/10회)")
    print_perf_table([(SIZE, ms_a)])
