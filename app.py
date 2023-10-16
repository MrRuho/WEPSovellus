from flask import Flask
from os import getenv
from sql import db

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")

db.init_app(app)

import routes

if __name__ == "__main__":
    app.run()

