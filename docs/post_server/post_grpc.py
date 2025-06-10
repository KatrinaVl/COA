from proto import post_service_pb2
from proto import post_service_pb2_grpc
import uuid
from datetime import datetime

from model import Post, Like, Comment
from p_db import SessionLocal, list_posts, update_post, delete_post
import json
from google.protobuf import empty_pb2
import grpc

from pydantic import BaseModel
import json
import os

from kafka_producer import KafkaProducer

class PostServiceImpl(post_service_pb2_grpc.PostServiceServicer):

    def __init__(self):
        self.kafka_producer = KafkaProducer()

    def CreatePost(self, request, context):
        post_id = str(uuid.uuid4())
        now = datetime.utcnow()

        db = SessionLocal()

        post = Post(
            id=post_id,
            title=request.title,
            description=request.description,
            creator_id=request.creator_id,
            created_at=now,
            updated_at=now,
            is_private=request.is_private,
            tags=",".join(request.tags)
        )

        db.add(post)
        db.commit()
        db.refresh(post)

        r_post = post_service_pb2.Post(
            id=post.id,
            title=post.title,
            description=post.description,
            creator_id=post.creator_id,
            created_at=post.created_at.isoformat(),
            updated_at=post.updated_at.isoformat(),
            is_private=post.is_private,
            tags=post.tags.split(',') if post.tags else []
        )

        db.close()

        return r_post

    def UpdatePost(self, request, context):
        db = SessionLocal()
        post = update_post(db, request.id, request.title, request.description, request.is_private, request.tags)
        db.close()
        if not post:
            context.abort(grpc.StatusCode.NOT_FOUND, "Post not found")

        r_post = post_service_pb2.Post(
            id=post.id,
            title=post.title,
            description=post.description,
            creator_id=post.creator_id,
            created_at=post.created_at.isoformat(),
            updated_at=post.updated_at.isoformat(),
            is_private=post.is_private,
            tags=post.tags.split(',') if post.tags else []
        )

        return r_post

    def DeletePost(self, request, context):
        db = SessionLocal()
        delete_post(db, request.id)
        db.close()
        return empty_pb2.Empty()

    def GetPost(self, request, context):
        db = SessionLocal()
        post = db.query(Post).filter(Post.id == request.id).first()
        db.close()
        if not post:
            context.abort(grpc.StatusCode.NOT_FOUND, "Post not found")
        r_post = post_service_pb2.Post(
            id=post.id,
            title=post.title,
            description=post.description,
            creator_id=post.creator_id,
            created_at=post.created_at.isoformat(),
            updated_at=post.updated_at.isoformat(),
            is_private=post.is_private,
            tags=post.tags.split(',') if post.tags else []
        )

        return r_post

    def ListPosts(self, request, context):
        db = SessionLocal()
        posts = list_posts(db)

        s = (request.pages * (request.n_page - 1))
        e = min(((request.pages * request.n_page)), len(posts))

        db.close()
        return post_service_pb2.PostList(posts=[
            post_service_pb2.Post(
                id=p.id,
                title=p.title,
                description=p.description,
                updated_at=p.updated_at.isoformat(),
                tags=p.tags
            ) for p in posts[s:e]
        ])

    def ViewPost(self, request, context):
        db = SessionLocal()
        post = db.query(Post).filter(Post.id == request.id).first()
        db.close()
        if not post:
            context.abort(grpc.StatusCode.NOT_FOUND, "Post not found")

        
        self.kafka_producer.send_post_viewed_event(request.id, request.user_id)

        r_post = post_service_pb2.Post(
            id=post.id,
            title=post.title,
            description=post.description,
            creator_id=post.creator_id,
            created_at=post.created_at.isoformat(),
            updated_at=post.updated_at.isoformat(),
            is_private=post.is_private,
            tags=post.tags.split(',') if post.tags else []
        )

        return r_post


    def LikePost(self, request, context): 
        like_id = str(uuid.uuid4())
        now = datetime.utcnow()

        db = SessionLocal()

        post = db.query(Post).filter(Post.id == request.post_id).first()
        if not post:
            context.abort(grpc.StatusCode.NOT_FOUND, "Post not found")

        like_check = db.query(Like).filter(Like.user_id == request.user_id and Like.post_id == request.post_id).first()
        if like_check:
            context.abort(grpc.StatusCode.NOT_FOUND, "Like already exist")

        like = Like(
            id=like_id,
            user_id=request.user_id,
            post_id = request.post_id,
            created_at=now,
        )

        self.kafka_producer.send_post_liked_event(request.post_id, request.user_id)

        db.add(like)
        db.commit()
        db.refresh(like)

        r_like = post_service_pb2.LikeResponse(
            success = True,
        )

        db.close()

        return r_like

    def CommentPost(self, request, context): 
        comm_id = str(uuid.uuid4())
        now = datetime.utcnow()

        db = SessionLocal()

        post_check = db.query(Post).filter(Post.id == request.post_id).first()
        if not post_check:
            context.abort(grpc.StatusCode.NOT_FOUND, "Post not found")

        post = Comment(
            id=comm_id,
            user_id = request.user_id,
            post_id = request.post_id,
            parent_id = request.parent_id,
            text = request.text,
            created_at = now,
        )

        db.add(post)
        db.commit()
        db.refresh(post)

        self.kafka_producer.send_comment_created_event({"id":comm_id, "user_id":request.user_id, "post_id":request.post_id, 
                                                        "parent_id":request.parent_id, "text":request.text, "created_at" : now})

        r_post = post_service_pb2.Comment(
            id=comm_id,
            text=request.text,
            parent_id=request.parent_id,
        )

        db.close()

        return r_post


    def GetComments(self, request, context):
        db = SessionLocal()
        post = db.query(Post).filter(Post.id == request.id).first()
        if not post:
            context.abort(grpc.StatusCode.NOT_FOUND, "Post not found")
        comments = db.query(Comment).filter(Comment.post_id == request.id).all()

        s = (request.per_page * (request.page - 1))
        e = min(((request.per_page * request.page)), len(comments))

        db.close()
        return post_service_pb2.GetCommentsResponse(comments=[
            post_service_pb2.Comment(
                id=p.id,
                text=p.text,
                parent_id=p.parent_id
            ) for p in comments[s:e]
        ])
