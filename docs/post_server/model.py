from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Post(Base):
    __tablename__ = 'posts'

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    creator_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_private = Column(Boolean, default=False)
    tags = Column(String)


class Like(Base):
    __tablename__ = 'likes'

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    post_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    post_id = Column(String, nullable=False)
    parent_id = Column(String, nullable=False)
    text = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
