from flask import Flask,redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from os import getenv
from sqlalchemy.sql import text
from db import update_topic_scores,publish_topic,selected_topic,topic_comments,show_topics,latest_topic,new_user,add_comment,db

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")

db.init_app(app)

if __name__ == "__main__":
    app.run()

@app.route("/")
def index():
    return render_template("index.html")

#Login or create new account
@app.route("/login",methods=["POST"])
def login():

    username = request.form["username"]
    password = request.form["password"]

    # Check the username and password. If they are correct, move to /topics; otherwise, display an error message
    sql = text("SELECT id, password FROM users WHERE username=:username")
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if not user:
        return render_template("index.html", not_user=True)
    else:
        hash_value = user.password
        if check_password_hash(hash_value, password):
            session["username"] = username
            query = ""
            topics = show_topics(query)
            latest = latest_topic()

            return render_template("/topics.html", topics=topics, latest_topic=latest)
        else:
            return render_template("index.html", not_password=True)

# New user register template
@app.route("/register")
def register():
    return render_template("register.html")

# Add new user to database
@app.route("/AddNewUser",methods=["POST"])
def AddNewUser():
   
    username = request.form["username"]
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    email = request.form["email"]
    password = request.form["password"]
    hash_value = generate_password_hash(password)

    if new_user(username, first_name, last_name, email, hash_value ) == False:    
        return render_template("register.html", user_exists=True)
    else:
        return render_template("index.html")

# Show all topics
@app.route("/topics", methods=["GET"])
def topic():
    query = request.args.get("query")
    if query is None:
        query = ""

    topics = show_topics(query) 
    latest = latest_topic()

    return render_template("/topics.html", topics=topics, query=query, latest_topic=latest)

# New topic template
@app.route("/new_topic")
def new_topic():
    return render_template("new_topic.html")

# Publish new topic
@app.route("/publish", methods=["POST"])
def send():
    header = request.form["header"]
    content = request.form["content"]
    sender = session["username"]
    tag = request.form["tag"]

    publish_topic(header, content, sender, tag)
    update_topic_scores()

    return redirect("/topics")

# Shows the selected topic and comments
@app.route("/view_topic/<int:topic_id>")
def view_topic(topic_id):

    topic = selected_topic(topic_id)
    comments = topic_comments(topic_id)

    return render_template("view_topic.html", topic=topic, comments=comments)

# Add new comment
@app.route("/comment", methods=["POST"])
def comment():
    content = request.form["comment"]
    sender = session["username"]
    topic_id = request.form["topic_id"]

    add_comment(content,sender,topic_id)

    return redirect(f"/view_topic/{topic_id}")

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")
