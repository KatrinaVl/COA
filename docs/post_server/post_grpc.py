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
# from kafka import KafkaProducer
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

        like = Like(
            id=like_id,
            user_id=request.user_id,
            post_id = request.post_id,
            created_at=now,
        )

        self.kafka_producer.send_post_licked_event(request.id, request.user_id)

        db.add(like)
        db.commit()
        db.refresh(like)

        r_like = post_service_pb2.LikeResponce(
            success = True,
        )

        db.close()

        return r_like

        #добавить кафку

    def CommentPost(self, request, context): 
        comm_id = str(uuid.uuid4())
        now = datetime.utcnow()

        db = SessionLocal()

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

        self.kafka_producer.send_post_commented_event(request.id, request.user_id, request.parent_id)

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

        #добавить кафку


    def GetComments(self, request, context):
        db = SessionLocal()
        comments = list_comments(db)

        s = (request.per_page * (request.n_page - 1))
        e = min(((request.per_page * request.n_page)), len(posts))

        db.close()
        return post_service_pb2.GetCommentsResponse(comments=[
            post_service_pb2.Comment(
                id=p.id,
                text=p.text,
            ) for p in posts[s:e]
        ])
