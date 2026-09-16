# python3.11 の軽量ベース
FROM python:3.11-slim

# コンテナ内の作業ディレクトリ
WORKDIR /app

# 必要なパッケージをインストール
COPY requirements.txt .
# キャッシュ削除して(インス--no-cache-dir -r)インㇲトール
RUN pip install --no-cache-dir -r requirements.txt

# アプリのソースコードすべてコピー
COPY . .

# Flaskが起動するポートを開ける
EXPOSE 5000

# コンテナが起動したとき実行する
CMD [ "python", "main.py" ]