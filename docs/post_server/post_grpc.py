from proto import post_service_pb2
from proto import post_service_pb2_grpc
import uuid
from datetime import datetime

from model import Post
from p_db import SessionLocal, list_posts, update_post, delete_post
import json
from google.protobuf import empty_pb2

class PostServiceImpl(post_service_pb2_grpc.PostServiceServicer):


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