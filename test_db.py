import sqlite3

conn = sqlite3.connect("royaltable.db")

tables = conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table'"
).fetchall()

admins = conn.execute(
    "SELECT username FROM admins"
).fetchall()

print("数据库表：", tables)
print("管理员：", admins)

conn.close()