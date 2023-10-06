from sqlalchemy.sql import text
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Display the most popular topic at first, based on the highest number of points. 
# if query not empty, searches for similarity in the header, sender, and tag.
def show_topics(query,show_interests,username):

    sql = """
    SELECT t.id, t.header, t.sender, t.tag, 
           SUM(CASE WHEN m.visible THEN 1 ELSE 0 END) AS message_count, t.visible
    FROM topic t
    LEFT JOIN messages m ON t.id = m.topic_id
    WHERE (
        :query = ''
        OR (
            LOWER(t.tag) LIKE LOWER(:query)    
        )
        OR (
            LOWER(t.header) LIKE LOWER(:query)
        )
        OR (
            LOWER(t.sender) LIKE LOWER(:query)
        )
    )
    """
    params = {"query": f"%{query}%"}

    # If show_interests is "true",show only topics that user follows.
    if show_interests == "true":

        sql += """
            AND (
                t.tag IN (
                    SELECT subject
                    FROM tags
                    WHERE id = ANY (
                        SELECT unnest(interests)
                        FROM users
                        WHERE username = :username
                    )
                )
            )
        """
        params["username"] = username

    sql += """
        GROUP BY t.id, t.header, t.sender, t.tag, t.visible
        ORDER BY t.score DESC
    """

    result = db.session.execute(text(sql), params)
    topics = result.fetchall()

    return topics

def latest_topic():
    sql ="""
    SELECT t.id, t.header, t.sender, t.tag, 
       SUM(CASE WHEN m.visible THEN 1 ELSE 0 END) AS message_count, t.visible
    FROM topic t
    LEFT JOIN messages m ON t.id = m.topic_id
    WHERE t.id = (SELECT MAX(id) FROM topic)
    GROUP BY t.id, t.header, t.sender, t.tag, t.visible
    """
    result = db.session.execute(text(sql))
    latest_topic = result.fetchone()

    return latest_topic

def topic_comments(topic_id):
    comments_query = text("SELECT id, content, sender, visible FROM messages WHERE topic_id = :topic_id")
    comments_result = db.session.execute(comments_query, {"topic_id": topic_id})
    topic_comments = comments_result.fetchall()

    return topic_comments

def selected_comment(comment_id):
    sql = text("SELECT id, content, sender, topic_id FROM messages WHERE id = :comment_id")
    result = db.session.execute(sql, {"comment_id": comment_id})
    selected_comment = result.fetchone()

    return selected_comment


def selected_topic(topic_id):
    topic_query = text("SELECT id, header, content, sender, tag FROM topic WHERE id = :topic_id")
    topic_result = db.session.execute(topic_query, {"topic_id": topic_id})
    selected_topic = topic_result.fetchone()

    return selected_topic

def publish_topic(header, content, sender, tag):
    sql = text("INSERT INTO topic (header, content, sender, tag, visible) VALUES (:header, :content, :sender, :tag, true)")
    db.session.execute(sql, {"header": header, "content": content, "sender": sender, "tag": tag})
    db.session.commit()

# Save new tag to tag table. If tag is already exist add tag total value +1
def add_topic_to_tag_table(tag):
    try:
        sql = text("SELECT COUNT(*) FROM tags WHERE subject LIKE :tag")
        subjectExists = db.session.execute(sql, {"tag":tag}).scalar()

        if subjectExists > 0:
            sql = text("UPDATE tags SET total = total + 1 WHERE subject = :tag")
        else:
            sql = text("INSERT INTO tags(subject, total) VALUES(:tag,1)")

        db.session.execute(sql,{"tag":tag})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e

# These points determine which topic is shown first. The point count is based on how new the topic is and how much it has been commented on.
# The newest topic gets 100 points, the second 98, the third 94, and so on. Additionally, every comment linked to that topic gives it +10 points.
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

# Check if the username or email is in the database. If not, create a new user.
def new_user(username, first_name,last_name, email, hash_value):
    sql = text("SELECT COUNT(*) FROM users WHERE username LIKE :username OR email LIKE :email")
    userExists = db.session.execute(sql, {"username":username, "email":email}).scalar()

    if userExists > 0:
        return False
    else:
        sql = text("INSERT INTO users (username,first_name,last_name, email ,password) VALUES (:username, :first_name,:last_name,:email ,:password)")
        db.session.execute(sql, {"username":username, "first_name":first_name, "last_name":last_name, "email":email, "password":hash_value})
        db.session.commit()
        return
    
# Add new comment and comment give a 10 points that specific topic."
def add_comment(content,sender,topic_id):

    sql = text("INSERT INTO messages (content, sender, topic_id, visible) VALUES (:content, :sender, :topic_id, true)")
    db.session.execute(sql, {"content":content, "sender":sender, "topic_id":topic_id})
    db.session.commit()

    sql = text("UPDATE topic SET score = score + :score WHERE id = :topic_id")
    db.session.execute(sql, {"score": 10, "topic_id": topic_id})
    db.session.commit()

# Set topic visible to false
def hide_topic(topic_id):
    sql = text("UPDATE topic SET visible = false WHERE id = :topic_id")
    db.session.execute(sql, {"topic_id": topic_id})
    db.session.commit()


def update_topic(topic_id,header,content,tag):
    sql = text("UPDATE topic SET header = :header, content = :content, tag = :tag WHERE id = :topic_id")
    db.session.execute(sql, {"header": header, "content": content, "tag": tag, "topic_id": topic_id})
    db.session.commit()

# Set comment visible to fals
def hide_comment(comment_id): 
    sql = text("UPDATE messages SET visible = false WHERE id = :comment_id")
    db.session.execute(sql, {"comment_id": comment_id})
    db.session.commit()

def update_comment(comment_id, content):
    sql = text("UPDATE messages SET content = :content WHERE id = :comment_id")
    db.session.execute(sql, {"content": content, "comment_id": comment_id})
    db.session.commit()

def get_topic_id_from_comment_id(comment_id):
    sql = text("SELECT topic_id FROM messages WHERE id = :comment_id")
    result = db.session.execute(sql, {"comment_id": comment_id})
    topic_id = result.fetchone()[0]

    return topic_id

# add tag to user interests
def add_tag_to_interests(username, tag):
    sql = text("SELECT id FROM tags WHERE subject = :tag")
    result = db.session.execute(sql, {"tag": tag})
    subject_id = result.scalar()

    sql = text("SELECT interests @> ARRAY[:subject_id] FROM users WHERE username = :username")
    interest_exist = db.session.execute(sql, {"username": username, "subject_id": subject_id}).scalar()

    if not interest_exist:
        sql = text("UPDATE users SET interests = interests || ARRAY[:subject_id] WHERE username = :username")
        db.session.execute(sql, {"username": username, "subject_id": subject_id})
        db.session.commit()


def my_interest_list(username):

    sql = text("""
        SELECT tags.subject
        FROM users
        JOIN tags ON tags.id = ANY(users.interests)
        WHERE users.username = :username
    """)
    result = db.session.execute(sql, {"username": username})
    interest_tags = [row.subject for row in result]
    return interest_tags
 