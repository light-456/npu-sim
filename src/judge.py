"""요구사항 04·06: 라벨 정규화와 허용오차(epsilon) 기반 판정."""

EPSILON = 1e-9
UNDECIDED = "UNDECIDED"

# 원본 라벨(소문자) → 표준 라벨
_LABEL_MAP = {
    "+": "Cross",
    "cross": "Cross",
    "x": "X",
}


def normalize_label(raw):
    """'+', 'cross' → 'Cross' / 'x', 'X' → 'X' / 알 수 없는 값 → None."""
    if raw is None:
        return None
    key = str(raw).strip().lower()
    return _LABEL_MAP.get(key)


def is_tie(a, b):
    """두 점수의 차이가 EPSILON보다 작으면 동점."""
    return abs(a - b) < EPSILON


def judge(score_a, score_b, label_a="Cross", label_b="X"):
    """점수를 비교해 label_a / label_b / UNDECIDED 중 하나를 반환한다."""
    if is_tie(score_a, score_b):
        return UNDECIDED
    return label_a if score_a > score_b else label_b
