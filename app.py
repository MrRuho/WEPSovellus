from flask import Flask
from flask import redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from os import getenv
from sqlalchemy.sql import text

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")

app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)

# Aplication start and render idex.html
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
            #Set /topics view
            result = db.session.execute(text("SELECT t.id, t.header,t.sender, t.tag,\
                                            COUNT(m.id) AS message_count FROM topic t\
                                            LEFT JOIN messages m ON t.id = m.topic_id GROUP BY t.id, t.header,t.sender, t.tag"))
            topics = result.fetchall()

            result = db.session.execute(text("SELECT id,header, sender, tag FROM topic WHERE id = (SELECT MAX(id) FROM topic)"))
            latest_topic = result.fetchone()

            return render_template("/topics.html", topics=topics, latest_topic=latest_topic)
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

    # Check if the username or email is in the database. Give a note if the user already exists. If not, create a new user.
    sql = text("SELECT COUNT(*) FROM users WHERE username LIKE :username OR email LIKE :email")
    userExists = db.session.execute(sql, {"username":username, "email":email}).scalar()

    if userExists > 0:
        return render_template("register.html", user_exists=True)
    else:
        sql = text("INSERT INTO users (username,first_name,last_name, email ,password) VALUES (:username, :first_name,:last_name,:email ,:password)")
        db.session.execute(sql, {"username":username, "first_name":first_name, "last_name":last_name, "email":email, "password":hash_value})
        db.session.commit()

    return render_template("index.html")

# Show all topics
@app.route("/topics", methods=["GET"])
def topic():
    query = request.args.get("query")

    # To determine the level of search precision. 0 show all topics
    if query is None:
        query = ""

    if  query:
        similarity_threshold = 10
    else:
        similarity_threshold = 0

    # Display the most popular topic at first, based on the highest number of points. if query not empty, searches for similarity in the header, sender, and tag.
    sql = """
    SELECT t.id, t.header, t.sender, t.tag, COUNT(m.id) AS message_count
    FROM topic t
    LEFT JOIN messages m ON t.id = m.topic_id
    WHERE (
        :query = ''
        OR (
            LOWER(t.tag) LIKE LOWER(:query)
            AND similarity(LOWER(t.tag), LOWER(:query)) * 100 >= :threshold
        )
        OR (
            LOWER(t.header) LIKE LOWER(:query)
            AND similarity(LOWER(t.header), LOWER(:query)) * 100 >= :threshold
        )
        OR (
            LOWER(t.sender) LIKE LOWER(:query)
            AND similarity(LOWER(t.sender), LOWER(:query)) * 100 >= :threshold
        )
    )
    GROUP BY t.id, t.header, t.sender, t.tag
    ORDER BY t.score DESC
    """
    params = {"query": f"%{query}%", "threshold": similarity_threshold}
    result = db.session.execute(text(sql), params)
    topics = result.fetchall()

    # Allways displays the newest topic at first.
    sql ="""
    SELECT id,header, sender, tag  
    FROM topic
    WHERE id = (SELECT MAX(id) FROM topic)
    """
    result = db.session.execute(text(sql))
    latest_topic = result.fetchone()

    return render_template("/topics.html", topics=topics, query=query, latest_topic=latest_topic)

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

    sql = text("INSERT INTO topic (header,content, sender, tag) VALUES (:header,:content,:sender,:tag)")
    db.session.execute(sql, {"header":header, "content":content, "sender":sender, "tag":tag})
    db.session.commit()
    update_topic_scores()
    return redirect("/topics")

# Shows the selected topic and comments
@app.route("/view_topic/<int:topic_id>")
def view_topic(topic_id):
    topic_query = text("SELECT id, header, content, sender FROM topic WHERE id = :topic_id")
    topic_result = db.session.execute(topic_query, {"topic_id": topic_id})
    selected_topic = topic_result.fetchone()

    comments_query = text("SELECT content, sender FROM messages WHERE topic_id = :topic_id")
    comments_result = db.session.execute(comments_query, {"topic_id": topic_id})
    topic_comments = comments_result.fetchall()

    return render_template("view_topic.html", topic=selected_topic, comments=topic_comments)

# Add new comment
@app.route("/comment", methods=["POST"])
def comment():
    content = request.form["comment"]
    sender = session["username"]
    topic_id = request.form["topic_id"]

    # Add new comment to db
    sql = text("INSERT INTO messages (content, sender, topic_id) VALUES (:content,:sender,:topic_id)")
    db.session.execute(sql, {"content":content, "sender":sender, "topic_id":topic_id})
    db.session.commit()

    # Every comment give a 10 points that specific topic."
    sql = text("UPDATE topic SET score = score + :score WHERE id = :topic_id")
    db.session.execute(sql, {"score": 10, "topic_id": topic_id})
    db.session.commit()

    return redirect(f"/view_topic/{topic_id}")


@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

# Update topic scores. These points determine which topic is shown first. The point count is based on how new the topic is and how much it has been commented on.
# The newest topic gets 100 points, the second 98, the third 94, and so on. Additionally, every comment linked to that topic gives it 10 points. 
def update_topic_scores():
   
    topics = db.session.execute(text("SELECT id FROM topic ORDER BY id DESC")).fetchall()
    
    score = 100
    reduction = 2
    for topic in topics:
        topic_id = topic[0]
        messages_count = db.session.execute(text("SELECT COUNT(*) FROM messages WHERE topic_id = :topic_id"), {"topic_id": topic_id}).scalar()
        total_score = score + messages_count * 10
      
        db.session.execute(text("UPDATE topic SET score = :score WHERE id = :topic_id"), {"score": total_score, "topic_id": topic_id})
        db.session.commit()

        score -= reduction
        reduction += 2