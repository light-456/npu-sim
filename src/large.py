"""대형 N(예: 1000×1000) 처리를 위한 메모리 측정과 MAC 최적화 기법.

- 메모리 레이아웃: 2차원 list → 1차원 list → array('d') (연속 메모리, 칸당 8바이트)
- 블록 처리(blocking/tiling): B×B 타일 단위로 나누어 계산
- 병렬 처리: 행 묶음을 여러 프로세스에 나누어 계산한 뒤 부분합을 더함 (NPU의 병렬 MAC 흉내)
모두 표준 라이브러리만 사용한다.
"""

import os
import tracemalloc
from array import array
from concurrent.futures import ProcessPoolExecutor

BLOCK = 64
MAX_WORKERS = 4


def to_array(matrix):
    """2차원 리스트를 연속 메모리 실수 배열 array('d')(길이 N²)로 변환한다."""
    arr = array("d")
    for row in matrix:
        arr.extend(row)
    return arr


def mac_array(a, b):
    """array('d') 두 개에 대한 MAC. 1차원 단일 for문."""
    total = 0.0
    for k in range(len(a)):
        total += a[k] * b[k]
    return total


def mac_blocked(pattern, filt, block=BLOCK):
    """블록 처리 MAC: 행렬을 block×block 타일로 나누어 타일마다 곱셈-누적한다.
    C/하드웨어에서는 타일이 캐시(또는 NPU 내부 메모리)에 들어가 메모리 왕복이 줄어든다."""
    n = len(pattern)
    total = 0
    for bi in range(0, n, block):
        i_end = min(bi + block, n)
        for bj in range(0, n, block):
            j_end = min(bj + block, n)
            for i in range(bi, i_end):
                p_row = pattern[i]
                f_row = filt[i]
                for j in range(bj, j_end):
                    total += p_row[j] * f_row[j]
    return total


def _mac_rows(chunk):
    """병렬 작업 단위: (패턴 행 묶음, 필터 행 묶음)의 부분합."""
    p_rows, f_rows = chunk
    total = 0
    for p_row, f_row in zip(p_rows, f_rows):
        for j in range(len(p_row)):
            total += p_row[j] * f_row[j]
    return total


def default_workers():
    return max(1, min(MAX_WORKERS, os.cpu_count() or 1))


def split_rows(pattern, filt, parts):
    """행을 parts개 묶음으로 나눈다."""
    n = len(pattern)
    size = (n + parts - 1) // parts
    return [(pattern[s:s + size], filt[s:s + size]) for s in range(0, n, size)]


def mac_parallel(pattern, filt, executor, parts):
    """행 묶음을 executor의 여러 프로세스에서 동시에 계산하고 부분합을 더한다."""
    return sum(executor.map(_mac_rows, split_rows(pattern, filt, parts)))


def make_executor(workers):
    return ProcessPoolExecutor(max_workers=workers)


def measure_memory_bytes(builder, *args):
    """builder(*args)가 새로 할당한 메모리(바이트)와 결과 객체를 반환한다."""
    tracemalloc.start()
    try:
        obj = builder(*args)
        current, _peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return current, obj


def make_real_matrix(n):
    """칸마다 서로 다른 실수 객체를 가진 N×N 행렬 (실제 이미지 데이터와 비슷한 메모리 사용)."""
    return [[((i * n + j) % 100) / 100 for j in range(n)] for i in range(n)]


def make_real_flat(n):
    return [((k % 100) / 100) for k in range(n * n)]


def make_real_array(n):
    return array("d", (((k % 100) / 100) for k in range(n * n)))
