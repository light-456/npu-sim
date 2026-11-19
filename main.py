"""Mini NPU Simulator - 실행 진입점 (요구사항 09: 실행 흐름)."""

import os
import sys

from src import mode_input, mode_json

DEFAULT_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")


def select_mode():
    print("[모드 선택]")
    print("1. 사용자 입력 (3x3)")
    print("2. data.json 분석")
    while True:
        choice = input("선택: ").strip()
        if choice in ("1", "2"):
            return choice
        print("1 또는 2를 입력하세요.")


def main():
    print("=== Mini NPU Simulator ===\n")
    try:
        if select_mode() == "1":
            mode_input.run()
        else:
            # python main.py [data.json 경로] 로 다른 파일을 지정할 수 있다.
            path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DATA
            mode_json.run(path)
    except (EOFError, KeyboardInterrupt):
        print("\n입력이 종료되어 프로그램을 마칩니다.")


if __name__ == "__main__":
    main()
