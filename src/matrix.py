"""요구사항 01: n×n 2차원 패턴/필터 데이터 구조."""


def make_matrix(n, fill=0):
    """n×n 격자를 만든다. 행마다 새 리스트를 만들어야 행끼리 공유되지 않는다."""
    return [[fill for _ in range(n)] for _ in range(n)]


def get_value(matrix, row, col):
    """(row, col) 위치의 값을 읽는다. (0부터 시작)"""
    return matrix[row][col]


def set_value(matrix, row, col, value):
    """(row, col) 위치에 값을 저장한다. (0부터 시작)"""
    matrix[row][col] = value


def is_square(matrix, n):
    """matrix가 정확히 n×n 크기의 2차원 리스트인지 검사한다."""
    if not isinstance(matrix, list) or len(matrix) != n:
        return False
    for row in matrix:
        if not isinstance(row, list) or len(row) != n:
            return False
    return True


def make_cross(n, value=1):
    """(보너스 2) N×N 십자가 패턴: 가운데 행과 가운데 열이 value."""
    m = make_matrix(n)
    mid = n // 2
    for i in range(n):
        m[mid][i] = value
        m[i][mid] = value
    return m


def make_x(n, value=1):
    """(보너스 2) N×N X 패턴: 두 대각선이 value."""
    m = make_matrix(n)
    for i in range(n):
        m[i][i] = value
        m[i][n - 1 - i] = value
    return m


def flatten(matrix):
    """(보너스 1) 2차원 리스트를 길이 N²의 1차원 리스트로 펼친다."""
    flat = []
    for row in matrix:
        for v in row:
            flat.append(v)
    return flat
