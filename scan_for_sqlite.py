# scan_for_sqlite.py
from pathlib import Path

ROOT = Path(__file__).resolve().parent

PATTERNS = ("sqlite3", "DB_PATH", ".db\"")


def main():
    for path in ROOT.rglob("*.py"):
        # сам скрипт можно пропустить
        if path.name == "scan_for_sqlite.py":
            continue

        text = path.read_text(encoding="utf-8", errors="ignore")
        if any(p in text for p in PATTERNS):
            print(f"Found in {path}:")
            for line_no, line in enumerate(text.splitlines(), start=1):
                if any(p in line for p in PATTERNS):
                    print(f"  {line_no}: {line}")
            print()


if __name__ == "__main__":
    main()
