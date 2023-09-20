from flask import Flask
from flask import redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text

from os import getenv

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")

app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)

# aplication start and render idex.html
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login",methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    # check username and password
    sql = text("SELECT id, password FROM users WHERE username=:username")
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if not user:
        return render_template("index.html", not_user=True)
    else:
        hash_value = user.password
        if check_password_hash(hash_value, password):
            session["username"] = username
            result = db.session.execute(text("SELECT t.id, t.header,t.sender, t.tag,\
                                            COUNT(m.id) AS message_count FROM topic t\
                                            LEFT JOIN messages m ON t.id = m.topic_id GROUP BY t.id, t.header,t.sender, t.tag"))
            topics = result.fetchall()
            return render_template("/topics.html", topics=topics)
        else:
            return render_template("index.html", not_password=True)

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/AddNewUser",methods=["POST"])
def AddNewUser():
   
    username = request.form["username"]
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    email = request.form["email"]
    password = request.form["password"]
    hash_value = generate_password_hash(password)

    # Check if username or email are in database. Come note if user is already exist. If not, create new user.
    sql = text("SELECT COUNT(*) FROM users WHERE username LIKE :username OR email LIKE :email")
    userExists = db.session.execute(sql, {"username":username, "email":email}).scalar()

    if userExists > 0:
        return render_template("register.html", user_exists=True)
    else:
        sql = text("INSERT INTO users (username,first_name,last_name, email ,password) VALUES (:username, :first_name,:last_name,:email ,:password)")
        db.session.execute(sql, {"username":username, "first_name":first_name, "last_name":last_name, "email":email, "password":hash_value})
        db.session.commit()

    return render_template("index.html")

@app.route("/topics")
def topic():
    result = db.session.execute(text("SELECT t.id, t.header,t.sender, t.tag,\
                                    COUNT(m.id) AS message_count FROM topic t\
                                    LEFT JOIN messages m ON t.id = m.topic_id GROUP BY t.id, t.header,t.sender, t.tag"))
    topics = result.fetchall()
    return render_template("/topics.html", topics=topics)

@app.route("/new")
def new():
    return render_template("new.html")

@app.route("/send", methods=["POST"])
def send():
    header = request.form["header"]
    content = request.form["content"]
    sender = session["username"]
    tag = request.form["tag"]

    sql = text("INSERT INTO topic (header,content, sender, tag) VALUES (:header,:content,:sender,:tag)")
    db.session.execute(sql, {"header":header, "content":content, "sender":sender, "tag":tag})
    db.session.commit()
    return redirect("/topics")

@app.route("/view_topic/<int:topic_id>")
def view_topic(topic_id):
    topic_query = text("SELECT id, header, content, sender FROM topic WHERE id = :topic_id")
    topic_result = db.session.execute(topic_query, {"topic_id": topic_id})
    selected_topic = topic_result.fetchone()

    comments_query = text("SELECT content, sender FROM messages WHERE topic_id = :topic_id")
    comments_result = db.session.execute(comments_query, {"topic_id": topic_id})
    topic_comments = comments_result.fetchall()

    return render_template("view_topic.html", topic=selected_topic, comments=topic_comments)

@app.route("/comment", methods=["POST"])
def comment():
    content = request.form["comment"]
    sender = session["username"]
    topic_id = request.form["topic_id"]
    sql = text("INSERT INTO messages (content, sender, topic_id) VALUES (:content,:sender,:topic_id)")
    db.session.execute(sql, {"content":content, "sender":sender, "topic_id":topic_id})
    db.session.commit()
    return redirect(f"/view_topic/{topic_id}")


@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")