import json
import logging
import os
import socket
import time
import urllib
import uuid

import jwt
import pytest
import requests

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
def api_addr():
    addr = os.environ.get('API_SERVER_URL', 'http://127.0.0.1:8090')
    host = urllib.parse.urlparse(addr).hostname
    port = urllib.parse.urlparse(addr).port
    wait_for_socket(host, port)
    yield addr


def make_requests(method, addr, handle, params=None, data=None, cookies=None):
    if data is not None:
        data = json.dumps(data)
    req = requests.Request(
        method,
        addr +
        handle,
        params=params,
        data=data,
        cookies=cookies)
    prepared = req.prepare()
    LOGGER.info(f'>>> {prepared.method} {prepared.url}')
    if len(req.data) > 0:
        LOGGER.info(f'>>> {req.data}')
    if req.cookies is not None:
        LOGGER.info(f'>>> {req.cookies}')
    s = requests.Session()
    resp = s.send(prepared)
    LOGGER.info(f'<<< {resp.status_code}')
    if len(resp.content) > 0:
        LOGGER.info(f'<<< {resp.content}')
    if len(resp.cookies) > 0:
        LOGGER.info(f'<<< {resp.cookies}')
    return resp


def make_user(api_addr):
    username = str(uuid.uuid4())
    password = str(uuid.uuid4())
    mail = str(uuid.uuid4())
    r = make_requests(
        'POST',
        api_addr,
        '/register',
        data={
            'login': username,
            'password': password,
            'mail' : mail})
    assert r.status_code == 201
    cookies = r.cookies.get_dict()
    read_value = json.loads(r.content)['user_id']

    assert r.status_code == 201
    cookies = r.cookies.get_dict()
    read_value = json.loads(r.content)['user_id']

    r = make_requests(
            'POST',
            api_addr,
            '/login',
            data={
                'login': username,
                'password': password})
    assert r.status_code == 201

    token = json.loads(r.content)['token']

    return ((username, password, mail, read_value, token), cookies)

def make_user_without_registration(api_addr):
    username = str(uuid.uuid4())
    password = str(uuid.uuid4())
    mail = str(uuid.uuid4())

    r = make_requests(
            'POST',
            api_addr,
            '/login',
            data={
                'login': username,
                'password': password})
    assert r.status_code == 201

    token = json.loads(r.content)['token']

    return ((username, password, mail, token), cookies)


def make_user_without_login(api_addr):
    username = str(uuid.uuid4())
    password = str(uuid.uuid4())
    mail = str(uuid.uuid4())
    r = make_requests(
        'POST',
        api_addr,
        '/register',
        data={
            'login': username,
            'password': password,
            'mail' : mail})
    assert r.status_code == 201
    cookies = r.cookies.get_dict()
    read_value = json.loads(r.content)['user_id']


    return ((username, password, mail, read_value), cookies)


@pytest.fixture
def user(api_addr):
    yield make_user(api_addr)

@pytest.fixture
def wr_user_l(api_addr):
    yield make_user_without_login(api_addr)


@pytest.fixture
def another_user(api_addr):
    yield make_user(api_addr)



class Tests:

    @staticmethod
    def test_create(api_addr, user):
        ((username, password, mail, r_v, t), _) = user #r_v - user_id
        r = make_requests(
            'POST',
            api_addr,
            '/create_post',
            data={
                'title': "do you like hse?",
                'description': "lalalala",
                'creator_id' : str(r_v),
                'is_private' : False,
                'tags' : "", 
                'token' : t, })

        assert r.status_code == 201

        data = json.loads(r.content)

        assert data['title'] == "do you like hse?"
        assert data['description'] == "lalalala"
        assert data['creator_id'] == str(r_v)
        assert data['is_private'] == False

    @staticmethod
    def test_create_without_auth(api_addr, user):
        ((username, password, mail, r_v, t), _) = user #r_v - user_id
        r = make_requests(
            'POST',
            api_addr,
            '/create_post',
            data={
                'title': "do you like hse?",
                'description': "lalalala",
                'creator_id' : str(r_v),
                'is_private' : False,
                'tags' : "", 
                "token" : "", })

        assert r.status_code != 201

    @staticmethod
    def test_create_without_registration(api_addr, user):
        ((username, password, mail, r_v, t), _) = user #r_v - user_id
        r = make_requests(
            'POST',
            api_addr,
            '/create_post',
            data={
                'title': "do you like hse?",
                'description': "lalalala",
                'creator_id' : "",
                'is_private' : False,
                'tags' : "", 
                'token' : "", })

        assert r.status_code != 201


    @staticmethod
    def test_update(api_addr, user):
        ((username, password, mail, r_v, t), _) = user
        LOGGER.info(f'>>> {r_v}')
        r_create = make_requests(
            'POST',
            api_addr,
            '/create_post',
            data={
                'title': "do you like hse?",
                'description': "lalalala",
                'creator_id' : str(r_v),
                'is_private' : False,
                'tags' : "", 
                'token' : t,})

        assert r_create.status_code == 201

        data = json.loads(r_create.content)

        r = make_requests(
            'POST',
            api_addr,
            '/update_post',
            data={
                'id' : data['id'],
                'title': "do you like hse?",
                'description': "lalalala",
                'creator_id' : str(r_v),
                'is_private' : False,
                'tags' : "", 
                "token" : t})

        assert r.status_code == 200

        data = json.loads(r.content)

        assert data['title'] == "do you like hse?"
        assert data['description'] == "lalalala"
        assert data['creator_id'] == str(r_v)
        assert data['is_private'] == False


    @staticmethod
    def test_update_wrong_post(api_addr, user):
        ((username, password, mail, r_v, t), _) = user
        LOGGER.info(f'>>> {r_v}')
        r_create = make_requests(
            'POST',
            api_addr,
            '/create_post',
            data={
                'title': "do you like hse?",
                'description': "lalalala",
                'creator_id' : str(r_v),
                'is_private' : False,
                'tags' : "", 
                'token' : t,})

        assert r_create.status_code == 201

        data = json.loads(r_create.content)

        r = make_requests(
            'POST',
            api_addr,
            '/update_post',
            data={
                'id' : "efgne",
                'title': "do you like hse?",
                'description': "lalalala",
                'creator_id' : str(r_v),
                'is_private' : False,
                'tags' : "", 
                "token" : t})

        assert r.status_code == 400

    @staticmethod
    def test_delete(api_addr, user):
        ((username, password, mail, r_v, t), _) = user
        r_create = make_requests(
            'POST',
            api_addr,
            '/create_post',
            data={
                'title': "do you like hse?",
                'description': "lalalala",
                'creator_id' : str(r_v),
                'is_private' : False,
                'tags' : "", 
                'token' : t,})

        assert r_create.status_code == 201

        data = json.loads(r_create.content)

        r = make_requests(
            'POST',
            api_addr,
            '/delete_post',
            data={
                'id' : data['id'], 
                "token" : t,
                'creator_id' : str(r_v)})

        assert r.status_code == 200

    @staticmethod
    def test_get(api_addr, user):
        ((username, password, mail, r_v, t), _) = user
        r_create = make_requests(
            'POST',
            api_addr,
            '/create_post',
            data={
                'title': "do you like hse?",
                'description': "lalalala",
                'creator_id' : str(r_v),
                'is_private' : False,
                'tags' : "", 
                'token' : t,})

        assert r_create.status_code == 201

        data = json.loads(r_create.content)

        r = make_requests(
            'GET',
            api_addr,
            '/get_post',
            data={
                'id' : data['id'], 
                "token" : t,
                'creator_id' : str(r_v)})

        assert r.status_code == 200

        data = json.loads(r.content)

        assert data['title'] == "do you like hse?"
        assert data['description'] == "lalalala"
        assert data['creator_id'] == str(r_v)
        assert data['is_private'] == False


    @staticmethod
    def test_get_wrong_post(api_addr, user):
        ((username, password, mail, r_v, t), _) = user
        r_create = make_requests(
            'POST',
            api_addr,
            '/create_post',
            data={
                'title': "do you like hse?",
                'description': "lalalala",
                'creator_id' : str(r_v),
                'is_private' : False,
                'tags' : "", 
                'token' : t,})

        assert r_create.status_code == 201

        data = json.loads(r_create.content)

        r = make_requests(
            'GET',
            api_addr,
            '/get_post',
            data={
                'id' : "sdfbsfg", 
                "token" : t,
                'creator_id' : str(r_v)})

        assert r.status_code == 400


    @staticmethod
    def test_get_list(api_addr, user):
        ((username, password, mail, r_v, t), _) = user
        r_create = make_requests(
            'POST',
            api_addr,
            '/create_post',
            data={
                'title': "do you like hse?",
                'description': "lalalala",
                'creator_id' : str(r_v),
                'is_private' : False,
                'tags' : "", 
                'token' : t,})

        assert r_create.status_code == 201

        data = json.loads(r_create.content)

        r = make_requests(
            'GET',
            api_addr,
            '/get_all',
            data={
                'id' : data['id'], 
                "token" : t,
                'creator_id' : str(r_v)})

        assert r.status_code == 200
