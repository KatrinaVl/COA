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


app = Flask(__name__)
LOGGER = logging.getLogger(__name__)


channel = grpc.insecure_channel("post_server:50051")
stub = post_service_pb2_grpc.PostServiceStub(channel)

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

@app.route("/like_post", methods=['GET'])
def like_post():
    d = request.get_json(force=True)

    try:
        response = stub.LikePost(post_service_pb2.PostRequest(
            id=d['id'],
        ))


        if response.success :
            return "OK", 200
        else :
            return "Wrong information", 400

    except Exception as e:
        return jsonify({"message" : f'{str(e)}'}), 400



###### метод комментария к посту

@app.route("/comment_post", methods=['GET'])
def comment_post():
    d = request.get_json(force=True)

    try:
        response = stub.CommentPost(post_service_pb2.CommentRequest(
            id=d['id'],
            text=d['text'],
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
        GetComments(GetCommentsRequest)
        response = stub.GetComments(post_service_pb2.GetCommentsRequest(
            id=d['id'],
            page = d['page'],
            per_page = d['per_page'],
        ))

        ans_list = {}
        k = 0

        for r in response.comments:
            ans = {"id" : r.id, "text" : r.text}

            ans_list[k] = ans
            k += 1

        return jsonify(ans_list), 200

    except Exception as e:
        return jsonify({"message" : f'{str(e)}'}), 400

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port='8090')
