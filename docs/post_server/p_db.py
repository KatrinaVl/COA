from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import Base, Post
import json
from datetime import datetime

DATABASE_URL = "sqlite:///./posts.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def list_posts(db):
    return db.query(Post).all()

def update_post(db, post_id, title, description, is_private, tags):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        return None
    post.title = title
    post.description = description
    post.tags = ",".join(tags)
    post.updated_at = datetime.utcnow()
    post.is_private = is_private
    db.commit()
    db.refresh(post)
    return post

def delete_post(db, post_id):
    post = db.query(Post).filter(Post.id == post_id).first()
    if post:
        db.delete(post)
        db.commit()
    return post