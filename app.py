from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from pathlib import Path
import secrets
import os

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "royaltable.db"

app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            nickname TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'normal',
            last_login TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("home"))

    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        nickname = request.form.get("nickname", "").strip()

        if not username or not password or not nickname:
            flash("请填写完整信息")
            return redirect(url_for("register"))

        if len(username) < 3:
            flash("账号至少需要3个字符")
            return redirect(url_for("register"))

        if len(password) < 6:
            flash("密码至少需要6个字符")
            return redirect(url_for("register"))

        conn = get_db()

        existing = conn.execute(
            "SELECT id FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        if existing:
            conn.close()
            flash("该账号已经存在")
            return redirect(url_for("register"))

        user_id = "RT" + secrets.token_hex(4).upper()

        conn.execute(
            """
            INSERT INTO users
            (user_id, username, password_hash, nickname)
            VALUES (?, ?, ?, ?)
            """,
            (
                user_id,
                username,
                generate_password_hash(password),
                nickname
            )
        )

        conn.commit()
        conn.close()

        flash("注册成功，请登录")
        return redirect(url_for("index"))

    return render_template("register.html")


@app.route("/login", methods=["POST"])
def login():

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    conn = get_db()

    user = conn.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    ).fetchone()

    if not user:
        conn.close()
        flash("账号或密码错误")
        return redirect(url_for("index"))

    if user["status"] != "normal":
        conn.close()
        flash("该账号已被禁用")
        return redirect(url_for("index"))

    if not check_password_hash(user["password_hash"], password):
        conn.close()
        flash("账号或密码错误")
        return redirect(url_for("index"))

    conn.execute(
        """
        UPDATE users
        SET last_login = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (user["id"],)
    )

    conn.commit()
    conn.close()

    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["nickname"] = user["nickname"]

    return redirect(url_for("home"))


@app.route("/home")
def home():

    if "user_id" not in session:
        return redirect(url_for("index"))

    conn = get_db()

    user = conn.execute(
        "SELECT * FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()

    conn.close()

    if not user:
        session.clear()
        return redirect(url_for("index"))

    return render_template("home.html", user=user)


@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("index"))


if __name__ == "__main__":

    init_db()

    print("================================")
    print("      ROYAL TABLE 已启动")
    print("================================")
    print("本机地址：http://127.0.0.1:5001")
    print("局域网地址：http://你的电脑IP:5001")
    print("================================")

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5001)),
        debug=False
    )