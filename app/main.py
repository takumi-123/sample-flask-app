from flask import Flask, redirect,render_template,request
import os
import psycopg2

app = Flask(__name__)

# データベースに接続
def get_db_connection():
    conn = psycopg2.connect(
        host=os.environ.get("DB_HOST", "db"),
        database=os.environ.get("DB_NAME", "postgres"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD","postgres"),
    )
    return conn

# テーブルを自動で作る
# めも　conn データベースに接続、cur 作業員 execute SQLの命令
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
          CREATE TABLE IF NOT EXISTS messages (
              id SERIAL PRIMARY KEY,
              content TEXT NOT NULL
              );
            """)
    conn.commit()
    cur.close()
    conn.close()

@app.route("/", methods=["GET", "POST"])
def index():
    conn = get_db_connection()
    cur = conn.cursor()

    # postから送信されたら
    if request.method == "POST":
        message = request.form.get("message")
        if message:
            # SQLでデータを保存する
            cur.execute("INSERT INTO messages (content) VALUES (%s);", (message,))
            conn.commit()
        return redirect("/")
    # GETならデータ一覧
    cur.execute("SELECT content FROM messages ORDER BY id DESC;")
    rows = cur.fetchall()

    return render_template("index.html", rows=rows)
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)