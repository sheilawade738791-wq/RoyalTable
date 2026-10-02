import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "royaltable.db"


def init_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 用户表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            nickname TEXT NOT NULL,
            avatar TEXT DEFAULT '',
            balance INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'normal',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login DATETIME
        )
    """)

    # 管理员表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 筹码变动记录
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chip_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            before_balance INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            after_balance INTEGER NOT NULL,
            transaction_type TEXT NOT NULL,
            operator TEXT NOT NULL,
            note TEXT DEFAULT '',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # 系统操作日志
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            operator TEXT NOT NULL,
            action TEXT NOT NULL,
            target TEXT DEFAULT '',
            detail TEXT DEFAULT '',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 创建初始管理员
    admin = cursor.execute(
        "SELECT id FROM admins WHERE username = ?",
        ("admin",)
    ).fetchone()

    if not admin:
        cursor.execute(
            """
            INSERT INTO admins (username, password_hash)
            VALUES (?, ?)
            """,
            ("admin", generate_password_hash("admin123456"))
        )
        print("初始管理员已创建")
        print("管理员账号：admin")
        print("管理员密码：admin123456")

    conn.commit()
    conn.close()

    print()
    print("================================")
    print("      RoyalTable 数据库")
    print("================================")
    print(f"数据库位置：{DB_PATH}")
    print("数据库初始化完成")
    print("================================")


if __name__ == "__main__":
    init_database()