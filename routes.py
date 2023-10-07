from flask import redirect, render_template, request, session
from app import app
from sqlalchemy.sql import text
from sql import update_topic_scores,publish_topic,selected_topic,topic_comments,show_topics,latest_topic,new_user,add_comment,hide_topic, update_topic,hide_comment,get_topic_id_from_comment_id,selected_comment,update_comment,add_topic_to_tag_table,add_tag_to_interests,my_interest_list,show_top_20_subjects,remove_tag_from_interests,show_tags,db
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
            show_interests = "false"
            show_interests_text = "Näytä seurattavat"
            topics = show_topics(query,show_interests,username)
            latest = latest_topic(username,show_interests)
           
            return render_template("/topics.html", topics=topics, latest_topic=latest,show_interests=show_interests,show_interests_text=show_interests_text)
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
    username = session["username"]
    query = request.args.get("query")
    if query is None:
        query = ""

    show_interests = request.args.get("show_interests")
    if show_interests is None:
        show_interests = "false"

    if show_interests == "true":
        show_interests_text = "Näytä kaikki"
        toggle_show_interests = "false"
    else:
        show_interests_text = "Näytä seurattavat"
        toggle_show_interests = "true"

    topics = show_topics(query,show_interests,username)
    latest = latest_topic(username,show_interests)

    return render_template("topics.html",topics=topics, latest_topic=latest, query=query, show_interests=show_interests, show_interests_text=show_interests_text, toggle_show_interests=toggle_show_interests)

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
    tag = request.form["tag"].lower()

    publish_topic(header, content, sender, tag)
    update_topic_scores()
    add_topic_to_tag_table(tag)

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


@app.route('/follow_tag/<string:tag>', methods=['GET'])
def follow_tag(tag):

    username = session['username']
    
    add_tag_to_interests(username, tag)
        
    from_page = request.args.get('from')
    if from_page == 'interests':
        return redirect("/my_interests")
    elif from_page == 'topics':
        return redirect("/topics")
    else:
        return redirect("/")


@app.route('/remove_tag/<string:tag>', methods=['GET'])
def remove_tag(tag):

    username = session['username']
    
    remove_tag_from_interests(username, tag)
        
    return redirect("/my_interests")


@app.route("/my_interests")
def my_interest():
    username = session["username"]

    query = request.args.get("query")
    if query is None:
        query = ""

    my_interest = my_interest_list(username)
    top_20_subjects = show_top_20_subjects()
    tags = show_tags(query)

    return render_template("interests.html", my_interest = my_interest, top_20_subjects = top_20_subjects, tags= tags)



@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")