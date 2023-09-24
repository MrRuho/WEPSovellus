from sqlalchemy.sql import text
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Display the most popular topic at first, based on the highest number of points. 
# if query not empty, searches for similarity in the header, sender, and tag.
def show_topics(query):
    
    sql = """
    SELECT t.id, t.header, t.sender, t.tag, COUNT(m.id) AS message_count
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
    GROUP BY t.id, t.header, t.sender, t.tag
    ORDER BY t.score DESC
    """
    params = {"query": f"%{query}%"}
    result = db.session.execute(text(sql), params)
    topics = result.fetchall()

    return topics

def latest_topic():
    sql ="""
    SELECT id,header, sender, tag  
    FROM topic
    WHERE id = (SELECT MAX(id) FROM topic)
    """
    result = db.session.execute(text(sql))
    latest_topic = result.fetchone()

    return latest_topic

def topic_comments(topic_id):
    comments_query = text("SELECT content, sender FROM messages WHERE topic_id = :topic_id")
    comments_result = db.session.execute(comments_query, {"topic_id": topic_id})
    topic_comments = comments_result.fetchall()

    return topic_comments

def selected_topic(topic_id):
    topic_query = text("SELECT id, header, content, sender FROM topic WHERE id = :topic_id")
    topic_result = db.session.execute(topic_query, {"topic_id": topic_id})
    selected_topic = topic_result.fetchone()

    return selected_topic

def publish_topic(header, content, sender, tag):
    sql = text("INSERT INTO topic (header, content, sender, tag) VALUES (:header, :content, :sender, :tag)")
    db.session.execute(sql, {"header": header, "content": content, "sender": sender, "tag": tag})
    db.session.commit()

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

    sql = text("INSERT INTO messages (content, sender, topic_id) VALUES (:content,:sender,:topic_id)")
    db.session.execute(sql, {"content":content, "sender":sender, "topic_id":topic_id})
    db.session.commit()

    sql = text("UPDATE topic SET score = score + :score WHERE id = :topic_id")
    db.session.execute(sql, {"score": 10, "topic_id": topic_id})
    db.session.commit()

