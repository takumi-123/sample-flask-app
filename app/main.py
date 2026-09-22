# セキュリティ関連のimport
from werkzeug.security import generate_password_hash, check_password_hash
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
    
    # メッセージテーブル
    cur.execute("""
          CREATE TABLE IF NOT EXISTS messages (
              id SERIAL PRIMARY KEY,
              content TEXT NOT NULL
              );
            """)

    # ユーザーテーブルの作成
    cur.execute("""
          CREATE TABLE IF NOT EXISTS users (
          id SERIAL PRIMARY KEY,
          username TEXT UNIQUE NOT NULL,
          password TEXT NOT NULL
          );
          """)

    # いいねテーブル作成
    cur.execute("""
         CREATE TABLE IF NOT EXISTS likes (
            id SERIAL PRIMARY KEY,
            message_id INTEGER REFERENCES messages(id) ON DELETE CASCADE
         );
         """)

    # Todo用のusersテーブル
    cur.execute("""
         CREATE TABLE IF NOT EXISTS Todousers (
           id SERIAL PRIMARY KEY,
           username VARCHAR(50) UNIQUE NOT NULL,
           password VARCHAR(255) NOT NULL
        );
        """)
    
    conn.commit()
    cur.close()
    conn.close()

@app.route("/", methods=["GET", "POST"])
def index():
    conn = get_db_connection()
    cur = conn.cursor()

    # POST（新規投稿）されたとき
    if request.method == "POST":
        message = request.form.get("message")
        if message:
            cur.execute("INSERT INTO messages (content) VALUES (%s);", (message,))
            conn.commit()
        return redirect("/")
        
    # 検索キーワードを受け取る
    keyword = request.args.get("keyword")

    # 👇 基本のSQL（いいねの数も一緒に取ってくるパーツ）
    base_query = """
        SELECT messages.id, messages.content, COUNT(likes.id) AS like_count
        FROM messages
        LEFT JOIN likes ON messages.id = likes.message_id
    """

    if keyword:
        #  キーワードがある場合：基本のSQLに「WHERE（絞り込み）」をくっつける！
        cur.execute(base_query + """
            WHERE messages.content LIKE %s
            GROUP BY messages.id
            ORDER BY messages.id DESC;
        """, (f"%{keyword}%",))
    else:
        #  キーワードがない場合：そのままグループ化して並べる！
        cur.execute(base_query + """
            GROUP BY messages.id
            ORDER BY messages.id DESC;
        """)

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("index.html", rows=rows)
# 新規ユーザー登録フォーム(usersテーブル)
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username and password:
            #パスワードを安全にハッシュ化
            hashed_password = generate_password_hash(password)

            conn = get_db_connection()
            cur = conn.cursor()
            try:
                #データベースにユーザーがハッシュ化されたパスワードを保存
                cur.execute(
                    "INSERT INTO users (username, password) VALUES (%s, %s);",
                    (username, hashed_password)
                )
                conn.commit()
            except psycopg2.errors.UniqueViolation:
                # すでにユーザ名が存在していた場合のエラー
                conn.rollback()
                return "このユーザーはすでに使われています。"
            finally:
                cur.close()
                conn.close()

            return redirect("/login")
    return render_template("register.html")

# ログインページ
@app.route("/login", methods =["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db_connection()
        cur = conn.cursor()
        # データベースに接続されたユーザー名を探す
        cur.execute("SELECT id, username, password FROM users WHERE username = %s;", (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        # ユーザーが存在し、かつパスワードが一致すｒかチェック
        if user and check_password_hash(user[2], password):
            #トップへ飛ばす
            return redirect("/")
        else:
            return "ユーザー名又はパスワードが間違っています。"

    return render_template("login.html")

# メッセージ削除
@app.route("/delete/<int:id>", methods = ["POST"])
def delete_message(id):
    conn = get_db_connection()
    cur = conn.cursor()

    # 該当するidを削除するSQL
    cur.execute("DELETE FROM messages WHERE id = %s", (id,))

    conn.commit()
    cur.close()
    conn.close()

    return redirect("/")

# 編集と更新を実行
@app.route("/edit/<int:id>", methods = ["GET", "POST"])
def edit_message(id):
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == "POST":
        # 新しいメッセージの取得
        new_message = request.form.get("message")

        # データベース
        cur.execute("UPDATE messages SET content = %s WHERE id = %s", (new_message, id))
        conn.commit()
        cur.close()
        conn.close()

        # # 更新できたらトップページへ戻る
        return redirect("/")

    # GETの場合は、いまデータベースに入っているデータを取得して編集画面に渡す
    cur.execute("SELECT id, content FROM messages WHERE id = %s;", (id,))
    message = cur.fetchone()
    cur.close()
    conn.close()

    return render_template("edit.html", message=message)

# いいねが押されたときの√
@app.route("/like/<int:message_id>", methods=["POST"])
def like_messages(message_id):
    conn = get_db_connection()
    cur = conn.cursor()

    # likeテーブルにどのメッセージをいいねするか
    cur.execute("INSERT INTO likes (message_id) VALUES (%s);", (message_id,))
    conn.commit()

    cur.close()
    conn.close()

    #トップページに戻る
    return redirect("/")

# 新規登録　Todouser用
@app.route("/todo/register", methods=["GET", "POST"])
def todo_register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username and password:
           hashed_password = generate_password_hash(password)

           conn = get_db_connection()
           cur = conn.cursor()
           try:
               # Todoテーブルに追加
               cur.execute("INSERT INTO Todousers (username, password) VALUES (%s, %s);",
                           (username, hashed_password)
               )
               conn.commit()
           except psycopg2.errors.UniqueViolation:
               conn.rollback()
               return "このユーザーは既に使われています。"
           finally:
               cur.close()
               conn.close()

           return redirect("/todo/login")

    return render_template("todo-register.html")

# ログイン(Todousers)
@app.route("/todo/login", methods=["POST", "GET"])
def todo_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db_connection()
        cur = conn.cursor()

        # テーブルからユーザ情報を検索
        cur.execute("SELECT id, username, password FROM Todousers WHERE username = %s;", (username,))
        user = cur.fetchone() #1件取得
        cur.close()
        conn.close()

        if user and check_password_hash(user[2], password):
            return redirect("/todo/list")
        else:
            return "ユーザー名またはパスワードが間違っています。"

    return render_template("todo-login.html")

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)