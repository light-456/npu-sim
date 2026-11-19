"""요구사항 07: 크기별 MAC 연산 시간 측정."""

import time
import unicodedata

from src.mac import mac, mac_flat
from src.matrix import flatten

REPEAT = 10


def measure_mac_ms(pattern, filt, repeat=REPEAT):
    """mac() 호출 구간만 repeat회 측정해 평균 시간(ms)을 반환한다. I/O는 포함하지 않는다."""
    mac(pattern, filt)  # 워밍업 1회 (측정에서 제외): 첫 호출의 캐시/할당 비용을 걸러낸다
    elapsed = 0.0
    for _ in range(repeat):
        t0 = time.perf_counter()
        mac(pattern, filt)
        elapsed += time.perf_counter() - t0
    return elapsed / repeat * 1000


def measure_mac_flat_ms(pattern, filt, repeat=REPEAT):
    """(보너스 1) 1차원 MAC의 평균 시간(ms). 펼치는 시간은 측정에서 제외한다."""
    p_flat = flatten(pattern)
    f_flat = flatten(filt)
    mac_flat(p_flat, f_flat)  # 워밍업 1회 (측정에서 제외)
    elapsed = 0.0
    for _ in range(repeat):
        t0 = time.perf_counter()
        mac_flat(p_flat, f_flat)
        elapsed += time.perf_counter() - t0
    return elapsed / repeat * 1000


def _width(text):
    """콘솔 표시 폭: 한글 등 전각 문자는 2칸으로 센다."""
    return sum(2 if unicodedata.east_asian_width(c) in ("W", "F") else 1 for c in text)


def pad(text, width, align="left"):
    """전각 문자를 고려해 text를 width칸에 맞춘다."""
    text = str(text)
    space = " " * max(0, width - _width(text))
    return text + space if align == "left" else space + text


def print_table(headers, rows, widths):
    """첫 열은 왼쪽, 나머지 열은 오른쪽 정렬로 표를 출력한다."""
    def line(cells):
        return "  ".join(pad(c, w, "left" if i == 0 else "right")
                         for i, (c, w) in enumerate(zip(cells, widths)))
    print(line(headers))
    print("-" * (sum(widths) + 2 * (len(widths) - 1)))
    for row in rows:
        print(line(row))


def size_label(n):
    return "%dx%d" % (n, n)


def print_perf_table(rows):
    """rows: [(n, 평균ms), ...] → 크기 / 평균 시간(ms) / 연산 횟수(N²) 표 출력."""
    print_table(["크기(N×N)", "평균 시간(ms)", "연산 횟수(N²)"],
                [(size_label(n), "%.4f" % ms, n * n) for n, ms in rows],
                [10, 14, 14])


def print_flat_compare_table(rows):
    """rows: [(n, 2차원ms, 1차원ms), ...] → 보너스 1 최적화 전/후 비교표 출력."""
    table = []
    for n, ms_2d, ms_1d in rows:
        ratio = ms_2d / ms_1d if ms_1d > 0 else 0.0
        table.append((size_label(n), "%.4f" % ms_2d, "%.4f" % ms_1d, "%.2fx" % ratio))
    print_table(["크기(N×N)", "2차원(ms)", "1차원(ms)", "속도 향상"], table, [10, 10, 10, 10])
