from flask import redirect, render_template, request, session
from app import app
from sqlalchemy.sql import text
from sql import update_topic_scores,publish_topic,selected_topic,topic_comments,show_topics,latest_topic,new_user,add_comment,hide_topic, update_topic,hide_comment,get_topic_id_from_comment_id,selected_comment,update_comment,db
from werkzeug.security import check_password_hash, generate_password_hash

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

# "Delete" topic. (This only hides it but no one can see it anymore)
@app.route("/hide_topic/<int:topic_id>", methods=["POST"])
def delete_topic(topic_id):

    topic = selected_topic(topic_id)
    
    if topic is not None and topic.sender == session["username"]:
        hide_topic(topic_id)

    return redirect("/topics")


@app.route('/edit_topic/<int:topic_id>', methods=['POST'])
def edit_topic(topic_id):

    topic = selected_topic(topic_id)
   
    return render_template('edit_topic.html',topic=topic)


@app.route('/update_topic', methods=['POST'])
def modify_topic():

    topic_id = request.form["topic_id"]
    header = request.form["header"]
    content = request.form["content"]
    tag = request.form["tag"]
    
    update_topic(topic_id, header, content, tag)
    
    topic = selected_topic(topic_id)
    comments = topic_comments(topic_id)

    return render_template("view_topic.html", topic=topic, comments=comments)


@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
def delete_comment(comment_id):

    hide_comment(comment_id)
 
    topic_id = get_topic_id_from_comment_id(comment_id)
    topic = selected_topic(topic_id)
    comments = topic_comments(topic_id)

    return render_template("view_topic.html", topic=topic, comments=comments)

@app.route('/edit_comment/<int:comment_id>', methods=['POST'])
def edit_comment(comment_id):

    comment = selected_comment(comment_id)

    return render_template("edit_comment.html", comment=comment)

@app.route('/update_comment', methods=['POST'])
def modify_comment():

    topic_id = request.form["topic_id"]
    comment_id = request.form["comment_id"]
    content = request.form["content"]
   
    update_comment(comment_id, content)

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