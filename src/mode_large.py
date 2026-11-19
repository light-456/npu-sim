"""모드 3: 패턴 생성기(보너스 2) + 대형 N 성능/메모리 분석(보너스 1 확장)."""

import time

from src import large
from src.judge import EPSILON, judge
from src.mac import mac, mac_flat
from src.matrix import flatten, make_cross, make_x
from src.mode_input import print_section
from src.perf import REPEAT, print_table

DEFAULT_N = 1000
MIN_N = 3
MAX_N = 2000          # 2000×2000 2차원 list ≈ 130MB. 그 이상은 메모리 부담이 커서 제한
LARGE_REPEAT = 3      # 대형 N은 1회가 수백 ms라 반복 횟수를 줄인다
LARGE_THRESHOLD = 100


def read_size():
    print("분석할 크기 N을 입력하세요 (%d~%d, Enter: %d)" % (MIN_N, MAX_N, DEFAULT_N))
    while True:
        text = input("N: ").strip()
        if not text:
            return DEFAULT_N
        try:
            n = int(text)
        except ValueError:
            print("입력 형식 오류: 정수를 입력하세요.")
            continue
        if MIN_N <= n <= MAX_N:
            return n
        print("입력 범위 오류: %d 이상 %d 이하로 입력하세요." % (MIN_N, MAX_N))


def time_ms(func, args, repeat):
    """func(*args)를 repeat회 실행한 평균 시간(ms)과 마지막 결과를 반환한다."""
    func(*args)  # 워밍업 1회 (측정 제외)
    elapsed = 0.0
    result = None
    for _ in range(repeat):
        t0 = time.perf_counter()
        result = func(*args)
        elapsed += time.perf_counter() - t0
    return elapsed / repeat * 1000, result


def show_generated(n, cross, x):
    print_section("[1] 패턴 생성기 (N=%d)" % n)
    if n <= 9:
        for name, m in (("십자가(Cross)", cross), ("X", x)):
            print(name)
            for row in m:
                print("  " + " ".join(str(v) for v in row))
    else:
        print("N×N 십자가/X 패턴 생성 완료 (칸 %d개, 화면 출력 생략)" % (n * n))

    # 생성한 패턴끼리 판정해 생성기가 올바른지 확인한다.
    for name, pattern, expected in (("십자가 패턴", cross, "Cross"), ("X 패턴", x, "X")):
        score_c = mac(pattern, cross)
        score_x = mac(pattern, x)
        verdict = judge(score_c, score_x)
        print("%s → Cross 점수: %s, X 점수: %s, 판정: %s (%s)"
              % (name, score_c, score_x, verdict,
                 "PASS" if verdict == expected else "FAIL"))


def show_memory(n):
    print_section("[2] 메모리 사용량 (N×N 실수 데이터 1개)")
    rows = []
    base = None
    for name, builder in (("2차원 list", large.make_real_matrix),
                          ("1차원 list", large.make_real_flat),
                          ("array('d')", large.make_real_array)):
        used, obj = large.measure_memory_bytes(builder, n)
        del obj
        base = base or used
        rows.append((name, "%.1f" % (used / 1024), "%.1f" % (used / (n * n)),
                     "%.2fx" % (used / base)))
    print_table(["저장 방식", "메모리(KB)", "칸당 바이트", "2차원 대비"], rows, [12, 11, 11, 10])
    if n < LARGE_THRESHOLD:
        print("* N이 작으면 파이썬 내부 객체 재사용 때문에 측정값이 흔들린다. N=1000 등 큰 값으로 확인하세요.")
    print("* list는 칸마다 실수 객체(약 24B) + 포인터(8B)를 따로 두고, array('d')는 숫자만 8B씩 연속 저장한다.")


def show_speed(n, pattern, filt):
    repeat = LARGE_REPEAT if n > LARGE_THRESHOLD else REPEAT
    print_section("[3] MAC 연산 시간 비교 (N=%d, 연산 %d회, 평균/%d회)" % (n, n * n, repeat))

    p_flat, f_flat = flatten(pattern), flatten(filt)
    p_arr, f_arr = large.to_array(pattern), large.to_array(filt)
    workers = large.default_workers()

    cases = [
        ("2차원 이중 for (기준)", mac, (pattern, filt)),
        ("1차원 펼침 (list)", mac_flat, (p_flat, f_flat)),
        ("1차원 array('d')", large.mac_array, (p_arr, f_arr)),
        ("블록 처리 (B=%d)" % large.BLOCK, large.mac_blocked, (pattern, filt)),
    ]
    results = []
    for name, func, args in cases:
        ms, score = time_ms(func, args, repeat)
        results.append((name, ms, score))

    # 프로세스 풀 생성 비용은 측정에서 제외하고, 작업 분배(데이터 전송) + 계산만 측정한다.
    executor = large.make_executor(workers)
    try:
        ms, score = time_ms(large.mac_parallel, (pattern, filt, executor, workers), repeat)
        results.append(("병렬 처리 (프로세스 %d개)" % workers, ms, score))
    finally:
        executor.shutdown()

    base_ms, base_score = results[0][1], results[0][2]
    rows = []
    for name, ms, score in results:
        same = "일치" if abs(score - base_score) < EPSILON else "불일치"
        rows.append((name, "%.3f" % ms, "%.2fx" % (base_ms / ms if ms > 0 else 0), same))
    print_table(["방식", "평균(ms)", "속도 향상", "점수"], rows, [26, 12, 10, 6])
    print("* 점수: 기준 방식과 결과가 같은지(|차이| < %g) 확인" % EPSILON)


def run():
    print_section("[0] 대형 N 분석 설정")
    n = read_size()
    cross = make_cross(n)
    x = make_x(n)
    show_generated(n, cross, x)
    show_memory(n)
    show_speed(n, x, cross)
    print("\n(대형 N의 문제점과 최적화 우선순위는 README.md의 \"대형 N 처리 분석\" 섹션 참고)")
