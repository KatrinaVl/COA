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

app = Flask(__name__)
LOGGER = logging.getLogger(__name__)

def wait_for_socket(host, port):
    retries = 10
    exception = None
    while retries > 0:
        try:
            socket.socket().connect((host, port))
            return
        except ConnectionRefusedError as e:
            exception = e
            print(f'Got ConnectionError for url {host}:{port}: {e} , retrying')
            retries -= 1
            time.sleep(2)
    raise exception

@pytest.fixture
def userservice_addr():
    addr = os.environ.get('USERSERVICE_SERVER_URL', 'http://127.0.0.1:8091')
    host = urllib.parse.urlparse(addr).hostname
    port = urllib.parse.urlparse(addr).port
    wait_for_socket(host, port)
    yield addr


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


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port='8090')
