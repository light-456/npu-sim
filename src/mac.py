"""요구사항 05: MAC(Multiply-Accumulate) 연산. 외부 라이브러리 없이 반복문으로 구현."""


def mac(pattern, filt):
    """같은 위치끼리 곱해서 모두 더한 점수를 반환한다. (이중 for문, N²번 연산)"""
    total = 0
    n = len(pattern)
    for i in range(n):
        for j in range(n):
            total += pattern[i][j] * filt[i][j]
    return total


def mac_flat(pattern_flat, filt_flat):
    """(보너스 1) 1차원으로 펼친 리스트에 대한 MAC. 단일 for문."""
    total = 0
    for k in range(len(pattern_flat)):
        total += pattern_flat[k] * filt_flat[k]
    return total
