import os
import html
import time

import psycopg
from flask import Flask, request, redirect

app = Flask(__name__)

NAME = os.getenv("NAME", "World")


def get_conn():
    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )


def init_db():
    # база может стартовать позже приложения, поэтому несколько попыток
    for attempt in range(10):
        try:
            with get_conn() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id SERIAL PRIMARY KEY,
                        text TEXT NOT NULL,
                        created_at TIMESTAMP NOT NULL DEFAULT now()
                    )
                """)
            print("Database is ready")
            return
        except psycopg.OperationalError as e:
            print(f"DB not ready (attempt {attempt + 1}): {e}")
            time.sleep(3)
    raise RuntimeError("Could not connect to the database")


@app.route("/")
def index():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT text, created_at FROM messages ORDER BY id DESC"
        ).fetchall()

    items = "".join(
        f"<li>{html.escape(text)} <small>({created:%Y-%m-%d %H:%M})</small></li>"
        for text, created in rows
    )
    return f"""
    <html><body>
      <h1>Hello {html.escape(NAME)}</h1>
      <form method="post" action="/add">
        <input name="text" placeholder="Ваше сообщение" required>
        <button type="submit">Добавить</button>
      </form>
      <h2>Записи ({len(rows)})</h2>
      <ul>{items}</ul>
    </body></html>
    """


@app.route("/add", methods=["POST"])
def add():
    text = request.form.get("text", "").strip()
    if text:
        with get_conn() as conn:
            conn.execute("INSERT INTO messages (text) VALUES (%s)", (text,))
    return redirect("/")


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8080)