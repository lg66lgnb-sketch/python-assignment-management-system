from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from assignment_system import create_app
from assignment_system.database import ensure_db, init_db


def main():
    parser = argparse.ArgumentParser(description="初始化作业管理系统数据库")
    parser.add_argument("--reset", action="store_true", help="重建数据库并恢复演示数据")
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        if args.reset:
            init_db(seed=True)
            print("数据库已重置，默认账号已准备好。")
        else:
            ensure_db(seed=True)
            print("数据库已检查，默认账号已准备好。")


if __name__ == "__main__":
    main()
