import secrets
from flask import abort, redirect, render_template, request, session
from app import app
from sqlalchemy.sql import text
from sql import update_topic_scores,publish_topic,selected_topic,topic_comments,show_topics,latest_topic,new_user,add_comment,hide_topic, update_topic,hide_comment,get_topic_id_from_comment_id,selected_comment,update_comment,add_topic_to_tag_table,add_tag_to_interests,my_interest_list,show_top_subjects,remove_tag_from_interests,show_tags,user_profile,hide_user,user_new_password,role,all_users,add_topic_to_block_list,show_blocked_tags,remove_topic_from_block_list,user_penalty_time,are_user_in_block_list, block_time,remove_expired_blocks,get_blocked_users,give_admin_privileges,remove_admin_privileges,master_admin,db
from werkzeug.security import check_password_hash, generate_password_hash

def csrf_protect():
    if session.get("csrf_token") != request.form.get("csrf_token"):
        abort(403)

@app.route("/")
def index():
    session["csrf_token"] = secrets.token_hex(16)
    return render_template("index.html")

#Login or create new account
@app.route("/login",methods=["POST"])
def login():
    csrf_protect()
    username = request.form["username"]
    password = request.form["password"]

    # Check the username and password. If they are correct, move to /topics; otherwise, display an error message
    sql = text("SELECT id, password, visible FROM users WHERE username=:username")
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    
    if not user:
        return render_template("index.html", not_user=True)

    if user.visible == False:
        return render_template("index.html", deleted_user=True)

    hash_value = user.password
    
    if check_password_hash(hash_value, password):
        session["username"] = username
        query = ""
        tag_query = ""
        show_interests = "false"
        show_interests_text = "Näytä seurattavat"
        topics = show_topics(query,show_interests,username)
        latest = latest_topic(username,show_interests)
        my_interest = my_interest_list(username)
        top_subjects = show_top_subjects()
        tags = show_tags(tag_query)
        admin = role(username)
        penalty_time = ""
        blocked_user = are_user_in_block_list(username)
        if blocked_user:
            penalty_time = block_time(username)
           
        return render_template("/topics.html", topics=topics, latest_topic=latest,show_interests=show_interests,show_interests_text=show_interests_text,my_interest = my_interest, top_subjects = top_subjects, tags= tags,admin=admin,blocked_user=blocked_user,penalty_time=penalty_time)
    else:
        return render_template("index.html", not_password=True)

# New user register template
@app.route("/register")
def register():
    return render_template("register.html")

# Add new user to database
@app.route("/AddNewUser",methods=["POST"])
def AddNewUser():

    csrf_protect()
    
    username = request.form["username"]
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    email = request.form["email"]
    password = request.form["password"]
    hash_value = generate_password_hash(password)

    if len(username) < 3 or len(first_name) < 3 or len(last_name) < 3:
        return render_template("register.html", user_exists=False, invalid_username=True)

    if "@" not in email:
        return render_template("register.html", user_exists=False, invalid_email=True)

    if len(password) < 5:
        return render_template("register.html", user_exists=False, invalid_password=True)

    if new_user(username, first_name, last_name, email, hash_value ) == False:    
        return render_template("register.html", user_exists=True)
    else:
        return render_template("index.html")

# Show all topics
@app.route("/topics", methods=["GET"])
def topic():
 
    username = session["username"]

    blocked_user = are_user_in_block_list(username)
    penalty_time = ""
    if blocked_user:
        penalty_time = block_time(username)


    query = request.args.get("query")
    if query is None:
        query = ""
    
    tag_query = request.args.get("tag_query")
    if tag_query is None:
        tag_query = ""

    show_interests = request.args.get("show_interests")
    if show_interests is None:
        show_interests = "false"

    if show_interests == "true":
        show_interests_text = "Näytä kaikki"
        toggle_show_interests = "false"
    else:
        show_interests_text = "Näytä vain seurattavat"
        toggle_show_interests = "true"

    topics = show_topics(query,show_interests,username)
    latest = latest_topic(username,show_interests)

    my_interest = my_interest_list(username)
    top_subjects = show_top_subjects()
 
    tags = show_tags(tag_query)
    admin = role(username)

    return render_template("topics.html",topics=topics, latest_topic=latest, query=query, show_interests=show_interests, show_interests_text=show_interests_text, toggle_show_interests=toggle_show_interests,my_interest = my_interest, top_subjects = top_subjects, tags= tags, admin=admin,blocked_user=blocked_user, penalty_time=penalty_time)


@app.route('/follow_tag/<string:tag>', methods=['GET'])
def follow_tag(tag):
    username = session['username']

    add_tag_to_interests(username, tag)
        
    return redirect("/topics")


@app.route('/remove_tag/<string:tag>', methods=['GET'])
def remove_tag(tag):

    username = session['username']
    
    remove_tag_from_interests(username, tag)
        
    return redirect("/topics")

# New topic template
@app.route("/new_topic")
def new_topic():
    return render_template("new_topic.html")

# Publish new topic
@app.route("/publish", methods=["POST"])
def send():
    csrf_protect()
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
    username = session["username"]
    topic = selected_topic(topic_id)
    comments = topic_comments(topic_id)
    admin = role(username)
    blocked_user = are_user_in_block_list(username)
    penalty_time = ""
    if blocked_user:
        penalty_time = block_time(username)

    return render_template("view_topic.html", topic=topic, comments=comments,admin=admin, blocked_user=blocked_user,penalty_time=penalty_time)

# "Delete" topic. (This only hides it but no one can see it anymore)
@app.route("/hide_topic/<int:topic_id>", methods=["POST"])
def delete_topic(topic_id):
    csrf_protect()
    username = session["username"]
    topic = selected_topic(topic_id)
    admin = role(username)
    if topic is not None and topic.sender == session["username"] or admin:
        hide_topic(topic_id)

    return redirect("/topics")


@app.route('/edit_topic/<int:topic_id>', methods=['POST'])
def edit_topic(topic_id):
    csrf_protect()
    topic = selected_topic(topic_id)
   
    return render_template('edit_topic.html',topic=topic)


@app.route('/update_topic', methods=['POST'])
def modify_topic():
    csrf_protect()
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
    csrf_protect()
    username = session['username']
    hide_comment(comment_id)
    admin = role(username)
    topic_id = get_topic_id_from_comment_id(comment_id)
    topic = selected_topic(topic_id)
    comments = topic_comments(topic_id)

    return render_template("view_topic.html", topic=topic, comments=comments, admin=admin)


@app.route('/edit_comment/<int:comment_id>', methods=['POST'])
def edit_comment(comment_id):
    csrf_protect()
    comment = selected_comment(comment_id)

    return render_template("edit_comment.html", comment=comment)


@app.route('/update_comment', methods=['POST'])
def modify_comment():
    csrf_protect()
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
    csrf_protect()
    content = request.form["comment"]
    sender = session["username"]
    topic_id = request.form["topic_id"]

    add_comment(content,sender,topic_id)

    return redirect(f"/view_topic/{topic_id}")

@app.route("/profile",methods=["GET", "POST"])
def profile():
    
    username = session['username']
    user = user_profile(username)
    admin = role(username)
    confirm_delete = request.args.get("confirm_delete") == "1"
    wrong_password = request.args.get("wrong_password") == "1"
    change_password = request.args.get("change_password") == "1"
    password_changed = request.args.get("password_changed") == "1"
    short_password = request.args.get("short_password") == "1"
 
    if request.method == "POST":

        if "cancel" in request.form:
            return redirect("/profile")
    
    return render_template("my_profile.html", user=user, confirm_delete=confirm_delete, wrong_password=wrong_password, change_password=change_password, password_changed=password_changed, short_password = short_password, admin=admin)

@app.route("/change_password",methods=["POST"])
def change_password():
    csrf_protect()
    username = session['username']
    password = request.form["password"]
    new_password = request.form["new_password"]

    if len(new_password) < 5:
        return redirect("/profile?short_password=1")

    correct_password = user_new_password(username,password,new_password)

    if correct_password:
        return redirect("/profile?password_changed=1")
    else:
        return redirect("/profile?wrong_password=1")


@app.route("/delete_account",methods=["POST"])
def delete_account():
    csrf_protect()
    username = session['username']
    password = request.form["password"]
    correct_password = hide_user(username, password)

    if correct_password:
        return redirect("/logout")
    else:
        return redirect("/profile?wrong_password=1")

@app.route("/admin", methods=["GET"])
def admin_tools():

    username = session['username']
    admin = role(username)
    block_user = request.args.get("block_user")
    user_privileges = request.args.get("user_privileges")
    master = master_admin(username)
    remove_expired_blocks()

    query = request.args.get("query")
    if query is None:
        query = ""
    
    tag_query = request.args.get("tag_query")
    if tag_query is None:
        tag_query = ""

    blocked_tag_query = request.args.get("blocked_tag_query")
    if blocked_tag_query is None:
        blocked_tag_query = ""

    if admin:
        users = all_users(query)
        tags = show_tags(tag_query)
        blocked_tags = show_blocked_tags(blocked_tag_query)
        blocked_users = get_blocked_users()

    return render_template("admin.html", admin=admin, users=users, tags=tags, blocked_tags=blocked_tags,block_user=block_user, blocked_users=blocked_users, user_privileges = user_privileges, master=master )

@app.route('/block_tag/<string:tag>', methods=['GET'])
def block_tag(tag):

    add_topic_to_block_list(tag)

    return redirect("/admin")

@app.route('/release_tag/<string:tag>', methods=['GET'])
def release_tag(tag):

    remove_topic_from_block_list(tag)

    return redirect("/admin")


@app.route('/block_user', methods=['GET'])
def block_user():

    penalty_time = request.args.get("penalty_time")
    username = request.args.get("block_user")
    user_penalty_time(penalty_time,username)
    
    return redirect("/admin")

@app.route('/privileges', methods=['GET'])
def manage_privileges():
    username = session['username']
    user = request.args.get('user')
    new_admin = request.args.get('new_admin')
    remove_admin = request.args.get('remove_admin')

    master = master_admin(username)
    
    if user and master:
        if new_admin:
            give_admin_privileges(user)
        elif remove_admin:
            remove_admin_privileges(user)

    return redirect("/admin")

@app.route("/logout")
def logout():
    del session["username"]

    return redirect("/")