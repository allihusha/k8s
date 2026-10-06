import os
from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    name = os.getenv("NAME", "World")
    return f"<html><body><h1>Hello {name}</h1></body></html>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)