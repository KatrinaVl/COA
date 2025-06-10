from flask import Flask, jsonify
from flask import request
from flask import make_response
import jwt
import json
import hashlib
import requests
import logging
import json
import logging
import os
import socket
import time
import urllib
import uuid
import pytest

import requests

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import grpc
from proto import post_service_pb2
from proto import post_service_pb2_grpc
from proto import analitic_service_pb2
from proto import analitic_service_pb2_grpc

from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime, date


app = Flask(__name__)
LOGGER = logging.getLogger(__name__)


channel = grpc.insecure_channel("post_server:50051")
stub = post_service_pb2_grpc.PostServiceStub(channel)

channel_an = grpc.insecure_channel("analitic_server:50052")
stub_an = analitic_service_pb2_grpc.AnaliticServiceStub(channel_an)

def make_requests(method, addr, handle, params=None, data=None, cookies=None, headers=None):
    if data is not None:
        data = json.dumps(data)
    addr = os.environ.get('USERSERVICE_SERVER_URL', 'http://127.0.0.1:8091')
    req = requests.Request(
        method,
        addr +
        handle,
        params=params,
        data=data,
        cookies=cookies,
        headers=headers)
    prepared = req.prepare()
    s = requests.Session()
    resp = s.send(prepared)
    return resp

@app.route("/register", methods=['POST'])
def register():
    d = request.get_json(force=True)

    login = d['login']
    password = d['password']
    mail = d['mail']
    
    r = make_requests(
                'POST',
                'http://127.0.0.1:8091',
                '/register',
                data=d)

    return r.content, r.status_code

@app.route("/login", methods=['POST'])
def login():
    d = request.get_json(force=True)

    login = d['login']
    password = d['password']
    
    r = make_requests(
                'POST',
                'http://127.0.0.1:8091',
                '/login',
                data=d)

    return r.content, r.status_code


@app.route("/update", methods=['PUT'])
def update():
    d = request.get_json(force=True)
    id_ = request.args.get("id")
    token = request.cookies.get('token')
    
    r = make_requests(
                'PUT',
                'http://127.0.0.1:8091',
                '/update',
                params={
                'id': id_},
                data=d,
                cookies= {
                    'token' : token
                })

    return r.content, r.status_code


@app.route("/get_info", methods=['GET'])
def get_info():
    id_ = request.args.get("id")
    token = request.cookies.get('token')

    r = make_requests(
                'GET',
                'http://127.0.0.1:8091',
                '/get_info',
                params={
                'id': id_},
                cookies= {
                    'token' : token
                })

    return r.content, r.status_code


@app.route("/add_friend", methods=['PUT'])
def add_friend():
    d = request.get_json(force=True)
    id_ = request.args.get("id")
    id_friend = request.args.get("id_friend")
    token = request.cookies.get('token')

    r = make_requests(
                'PUT',
                'http://127.0.0.1:8091',
                '/add_friend',
                params={
                'id': id_,
                'id_friend' : id_friend},
                data = d,
                cookies= {
                    'token' : token
                })

    return r.content, r.status_code


@app.route("/create_post", methods=['POST'])
def create_post():
    d = request.get_json(force=True)

    r = make_requests(
                'GET',
                'http://127.0.0.1:8091',
                '/get_info',
                params={
                'id': d['creator_id']},
                cookies= {
                    'token' : d['token'],
                })

    if r.status_code != 200:
        return r.content, r.status_code


    try: 
        response = stub.CreatePost(post_service_pb2.CreatePostRequest(
            title=d['title'],
            description=d['description'],
            creator_id=d['creator_id'],
            is_private=d['is_private'],
            tags=d['tags']
        ))

        ans = {"id" : response.id, "title" : response.title, "description" : response.description, 
                "creator_id" : response.creator_id, "created_at" : response.created_at, "updated_at" : response.updated_at, 
                "is_private" : response.is_private, "tags" : list(response.tags)}

        return jsonify(ans), 201

    except Exception as e:
        return jsonify({"message" : f'{str(e)}'}), 400

@app.route("/update_post", methods=['POST'])
def update_post():
    d = request.get_json(force=True)

    r = make_requests(
                'GET',
                'http://127.0.0.1:8091',
                '/get_info',
                params={
                'id': d['creator_id']},
                cookies= {
                    'token' : d['token'],
                })

    if r.status_code != 200:
        return r.content, r.status_code

    try:

        response = stub.UpdatePost(post_service_pb2.UpdatePostRequest(
            id=d['id'],
            title=d['title'],
            description=d['description'],
            creator_id=d['creator_id'],
            is_private=d['is_private'],
            tags=d['tags']
        ))

        ans = {"id" : response.id, "title" : response.title, "description" : response.description, 
                "creator_id" : response.creator_id, "created_at" : response.created_at, "updated_at" : response.updated_at, 
                "is_private" : response.is_private, "tags" : list(response.tags)}

        return jsonify(ans), 200

    except Exception as e:
        return jsonify({"message" : f'{str(e)}'}), 400

@app.route("/delete_post", methods=['POST'])
def delete_post():
    d = request.get_json(force=True)

    r = make_requests(
                'GET',
                'http://127.0.0.1:8091',
                '/get_info',
                params={
                'id': d['creator_id']},
                cookies= {
                    'token' : d['token'],
                })

    if r.status_code != 200:
        return r.content, r.status_code

    try:
        response = stub.DeletePost(post_service_pb2.PostRequest(
            id=d['id']
        ))

        ans = {"Messege" : "Post was deleted"}

        return jsonify(ans), 200

    except Exception as e:
        return jsonify({"message" : f'{str(e)}'}), 400

@app.route("/get_post", methods=['GET'])
def get_post():
    d = request.get_json(force=True)

    r = make_requests(
                'GET',
                'http://127.0.0.1:8091',
                '/get_info',
                params={
                'id': d['creator_id']},
                cookies= {
                    'token' : d['token'],
                })

    if r.status_code != 200:
        return r.content, r.status_code

    try:
        response = stub.GetPost(post_service_pb2.PostRequest(
            id=d['id']
        ))

        ans = {"id" : response.id, "title" : response.title, "description" : response.description, 
                "creator_id" : response.creator_id, "created_at" : response.created_at, "updated_at" : response.updated_at, 
                "is_private" : response.is_private, "tags" : list(response.tags)}

        return jsonify(ans), 200

    except Exception as e:
        return jsonify({"message" : f'{str(e)}'}), 400

@app.route("/get_all", methods=['GET'])
def get_all():
    d = request.get_json(force=True)

    r = make_requests(
                'GET',
                'http://127.0.0.1:8091',
                '/get_info',
                params={
                'id': d['creator_id']},
                cookies= {
                    'token' : d['token'],
                })

    if r.status_code != 200:
        return r.content, r.status_code

    try:
        response = stub.ListPosts(post_service_pb2.PostPagin(pages = d['pages'], n_page = d['n_page']))

        ans_list = {}
        k = 0

        for r in response.posts:
            ans = {"id" : r.id, "title" : r.title, "description" : r.description, 
                "creator_id" : r.creator_id, "created_at" : r.created_at, "updated_at" : r.updated_at, 
                "is_private" : r.is_private, "tags" : list(r.tags)}

            ans_list[k] = ans
            k += 1

        return jsonify(ans_list), 200

    except Exception as e:
        return jsonify({"message" : f'{str(e)}'}), 400



###### метод просмотра поста

@app.route("/view_post", methods=['GET'])
def view_post():
    d = request.get_json(force=True)

    try:

        response = stub.ViewPost(post_service_pb2.ViewRequest(
            id=d['id'],
            user_id=d['user_id']
        ))

        ans = {"id" : response.id, "title" : response.title, "description" : response.description, 
                "creator_id" : response.creator_id, "created_at" : response.created_at, "updated_at" : response.updated_at, 
                "is_private" : response.is_private, "tags" : list(response.tags)}

        return jsonify(ans), 200

    except Exception as e:
        return jsonify({"message" : f'{str(e)}'}), 400


###### метод лайка поста

@app.route("/like_post", methods=['POST'])
def like_post():
    d = request.get_json(force=True)

    try:
        response = stub.LikePost(post_service_pb2.LikeRequest(
            post_id=d['post_id'],
            user_id=d['user_id']
        ))


        if response.success :
            return jsonify({"message" : f"OK"}), 200
        else :
            return jsonify({"message" : f"Wrong information"}), 400

    except Exception as e:
        return jsonify({"message" : f'{str(e)}'}), 400



###### метод комментария к посту

@app.route("/comment_post", methods=['POST'])
def comment_post():
    d = request.get_json(force=True)

    try:
        if "parent_id" in d:
            response = stub.CommentPost(post_service_pb2.CommentRequest(
                text=d['text'],
                post_id=d['post_id'],
                user_id=d['user_id'],
                parent_id=d['parent_id']
            ))
        else:
            response = stub.CommentPost(post_service_pb2.CommentRequest(
                text=d['text'],
                post_id=d['post_id'],
                user_id=d['user_id']
            ))



        ans = {"id" : response.id, "text" : response.text}

        return jsonify(ans), 200

    except Exception as e:
        return jsonify({"message" : f'{str(e)}'}), 400



####### метод получения вех коментариев

@app.route("/get_comments_post", methods=['GET'])
def get_comments_post():
    d = request.get_json(force=True)

    try:
        response = stub.GetComments(post_service_pb2.GetCommentsRequest(
            id=d['id'],
            page = d['page'],
            per_page = d['per_page'],
        ))

        ans_list = {}
        k = 0

        for r in response.comments:
            if r.parent_id:
                ans = {"id" : r.id, "text" : r.text, "parent_id" : r.parent_id}
            else:
                ans = {"id" : r.id, "text" : r.text}

            ans_list[k] = ans
            k += 1

        return jsonify(ans_list), 200

    except Exception as e:
        return jsonify({"message" : f'{str(e)}'}), 400


@app.route("/get_number_likes", methods=['GET'])
def get_number_likes():
    d = request.get_json(force=True)

    try:
        post_id = d.get('post_id')
        if not post_id:
            return jsonify({"message": "Missing 'post_id' in request"}), 400

        response = stub_an.GetNumberLikes(analitic_service_pb2.NumberRequest(id=post_id))
        return jsonify({
                "likes": response.num
            }), 200


    except Exception as e:
        return jsonify({"message" : f'{str(e)}'}), 400


@app.route("/get_number_see", methods=['GET'])
def get_number_see():
    d = request.get_json(force=True)

    try:
        post_id = d.get('post_id')
        if not post_id:
            return jsonify({"message": "Missing 'post_id' in request"}), 400

        
        response = stub_an.GetNumberSee(analitic_service_pb2.NumberRequest(id=post_id))
        return jsonify({
                "see": response.num
            }), 200


    except Exception as e:
        return jsonify({"message" : f'{str(e)}'}), 400


@app.route("/get_number_comments", methods=['GET'])
def get_number_comments():
    d = request.get_json(force=True)

    try:
        post_id = d.get('post_id')
        if not post_id:
            return jsonify({"message": "Missing 'post_id' in request"}), 400

    
        response = stub_an.GetNumberComments(analitic_service_pb2.NumberRequest(id=post_id))
        return jsonify({
                "comments": response.num
            }), 200


    except Exception as e:
        return jsonify({"message" : f'{str(e)}'}), 400


@app.route("/get_dynamic_likes", methods=['GET'])
def get_dynamic_likes():
    d = request.get_json(force=True)

    try:
        post_id = d.get('post_id')
        if not post_id:
            return jsonify({"message": "Missing 'post_id' in request"}), 400

        ans_list = []
        
        response = stub_an.GetLikes(analitic_service_pb2.NumberRequest(id=post_id))

        for r in response.days:
            date_str = r.date.ToDatetime().strftime('%Y-%m-%d')
            
            ans = {"date" : date_str, "num" : r.num}

            ans_list.append(ans)
        
        
        return jsonify({
                "dynamic": ans_list
            }), 200

    except Exception as e:
        return jsonify({"message" : f'{str(e)}'}), 400


@app.route("/get_dynamic_see", methods=['GET'])
def get_dynamic_see():
    d = request.get_json(force=True)

    try:
        post_id = d.get('post_id')
        if not post_id:
            return jsonify({"message": "Missing 'post_id' in request"}), 400

        ans_list = []
        
        response = stub_an.GetSee(analitic_service_pb2.NumberRequest(id=post_id))

        for r in response.days:
            date_str = r.date.ToDatetime().strftime('%Y-%m-%d')
            
            ans = {"date" : date_str, "num" : r.num}

            ans_list.append(ans)
        
        
        return jsonify({
                "dynamic": ans_list
            }), 200

    except Exception as e:
        return jsonify({"message" : f'{str(e)}'}), 400


@app.route("/get_dynamic_comments", methods=['GET'])
def get_dynamic_comments():
    d = request.get_json(force=True)

    try:
        post_id = d.get('post_id')
        if not post_id:
            return jsonify({"message": "Missing 'post_id' in request"}), 400

        ans_list = []
        
        response = stub_an.GetComments(analitic_service_pb2.NumberRequest(id=post_id))

        for r in response.days:
            date_str = r.date.ToDatetime().strftime('%Y-%m-%d')
            
            ans = {"date" : date_str, "num" : r.num}

            ans_list.append(ans)
        
        
        return jsonify({
                "dynamic": ans_list
            }), 200

    except Exception as e:
        return jsonify({"message" : f'{str(e)}'}), 400


@app.route("/get_top_posts", methods=['GET'])
def get_top_posts():
    d = request.get_json(force=True)

    try:
        type_ = d.get('type')
        

        ans_list = []
        
        response = stub_an.GetTopPosts(analitic_service_pb2.TopRequest(type=type_))

        for r in response.ids:
            
            ans = {"date" : r.id, "num" : r.count}

            ans_list.append(ans)
        
        
        return jsonify({
                "top_posts": ans_list
            }), 200

    except Exception as e:
        return jsonify({"message" : f'{str(e)}'}), 400


@app.route("/get_top_users", methods=['GET'])
def get_top_users():
    d = request.get_json(force=True)

    try:
        type_ = d.get('type')
        

        ans_list = []
        
        response = stub_an.GetTopUsers(analitic_service_pb2.TopRequest(type=type_))

        for r in response.ids:
            
            ans = {"date" : r.id, "num" : r.count}

            ans_list.append(ans)
        
        
        return jsonify({
                "top_users": ans_list
            }), 200

    except Exception as e:
        return jsonify({"message" : f'{str(e)}'}), 400

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port='8090')
