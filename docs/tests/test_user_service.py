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


@pytest.fixture
def userservice_addr():
    addr = os.environ.get('USERSERVICE_SERVER_URL', 'http://127.0.0.1:8091')
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
    return ((username, password, mail, read_value), cookies)


@pytest.fixture
def user(api_addr):
    yield make_user(api_addr)


@pytest.fixture
def another_user(api_addr):
    yield make_user(api_addr)



class TestsRegister:

    @staticmethod
    def test_register(api_addr, userservice_addr, user):
        ((username, password, mail, r_v), _) = user
        r = make_requests(
            'POST',
            api_addr,
            '/register',
            data={
                'login': username + "4",
                'password': password,
                'mail' : 'mail_8@edu.hse.ru4'})
        assert r.status_code == 201

    @staticmethod
    def test_register_same_name(api_addr, userservice_addr, user):
        ((username, password, mail, r_v), _) = user
        r = make_requests(
            'POST',
            api_addr,
            '/register',
            data={
                'login': 'test_7',
                'password': 'password____',
                'mail' : 'mail_7@edu.hse.ru'})
        assert r.status_code == 400

    @staticmethod
    def test_register_same_mail(api_addr, userservice_addr, user):
        ((username, password, mail, r_v), _) = user
        r = make_requests(
            'POST',
            api_addr,
            '/register',
            data={
                'login': 'test_*',
                'password': 'password_____',
                'mail' : 'mail_7@edu.hse.ru'})
        assert r.status_code == 400


class TestLogin:
    @staticmethod
    def test_login(api_addr, userservice_addr, user):
        ((username, password, mail, r_v), _) = user
        r = make_requests(
            'POST',
            api_addr,
            '/login',
            data={
                'login': username,
                'password': password})
        assert r.status_code == 201


    @staticmethod
    def test_login_no_user(api_addr, userservice_addr, user):
        ((username, password, mail, r_v), _) = user
        r = make_requests(
            'POST',
            api_addr,
            '/login',
            data={
                'login': username + "not_ok",
                'password': password})
        assert r.status_code == 401

    @staticmethod
    def test_login_wrong_password(api_addr, userservice_addr, user):
        ((username, password, mail, r_v), _) = user
        r = make_requests(
            'POST',
            api_addr,
            '/login',
            data={
                'login': username,
                'password': 'password___'})
        assert r.status_code == 401

        
class TestUpdate:

    @staticmethod
    def test_update(api_addr, userservice_addr, user):
        ((username, password, mail, r_v), _) = user
        r_login = make_requests(
            'POST',
            api_addr,
            '/login',
            data={
                'login': username,
                'password': password})

        token = json.loads(r_login.content)['token']

        r_update = make_requests(
            'PUT',
            api_addr,
            '/update',
            params={
                'id': r_v},
            data={
                'name': 'kate',
                'surname': 'vl'},
            cookies={
                'token' : token})
        assert r_update.status_code == 200

    @staticmethod
    def test_update_wrong_token(api_addr, userservice_addr, user):
        ((username, password, mail, r_v), _) = user
        r_login = make_requests(
            'POST',
            api_addr,
            '/login',
            data={
                'login': username,
                'password': password})

        token = json.loads(r_login.content)['token']

        r_update = make_requests(
            'PUT',
            api_addr,
            '/update',
            params={
                'id': r_v},
            data={
                'name': 'kate',
                'surname': 'vl'},
            cookies={
                'token' : 'ttok'})
        assert r_update.status_code == 403

    @staticmethod
    def test_update_login(api_addr, userservice_addr, user):
        ((username, password, mail, r_v), _) = user
        r_login = make_requests(
            'POST',
            api_addr,
            '/login',
            data={
                'login': username,
                'password': password})

        token = json.loads(r_login.content)['token']

        r_update = make_requests(
            'PUT',
            api_addr,
            '/update',
            params={
                'id': r_v},
            data={
                'name': 'kate',
                'surname': 'vl',
                "login" : "tutu"},
            cookies={
                'token' : token})
        assert r_update.status_code == 400

    @staticmethod
    def test_update_password(api_addr, userservice_addr, user):
        ((username, password, mail, r_v), _) = user
        r_login = make_requests(
            'POST',
            api_addr,
            '/login',
            data={
                'login': username,
                'password': password})

        token = json.loads(r_login.content)['token']

        r_update = make_requests(
            'PUT',
            api_addr,
            '/update',
            params={
                'id': r_v},
            data={
                'name': 'kate',
                'surname': 'vl',
                "password" : "tutu"},
            cookies={
                'token' : token})
        assert r_update.status_code == 400

    @staticmethod
    def test_update_do_not_find_user(api_addr, userservice_addr, user):
        ((username, password, mail, r_v), _) = user
        r_login = make_requests(
            'POST',
            api_addr,
            '/login',
            data={
                'login': username,
                'password': password})

        token = json.loads(r_login.content)['token']

        r_update = make_requests(
            'PUT',
            api_addr,
            '/update',
            params={
                'id': '1'},
            data={
                'name': 'kate',
                'surname': 'vl',
                "password" : "tutu"},
            cookies={
                'token' : token})
        assert r_update.status_code == 404

class TestGetInfo:

    @staticmethod
    def test_get_info(api_addr, userservice_addr, user):
        ((username, password, mail, r_v), _) = user
        r_login = make_requests(
            'POST',
            api_addr,
            '/login',
            data={
                'login': username,
                'password': password})

        token = json.loads(r_login.content)['token']

        r_get_info = make_requests(
            'GET',
            api_addr,
            '/get_info',
            params={
                'id': r_v},
            cookies={
                'token' : token})
        assert r_get_info.status_code == 200

    @staticmethod
    def test_get_info_do_not_find_user(api_addr, userservice_addr, user):
        ((username, password, mail, r_v), _) = user
        r_login = make_requests(
            'POST',
            api_addr,
            '/login',
            data={
                'login': username,
                'password': password})

        token = json.loads(r_login.content)['token']

        r_get_info = make_requests(
            'GET',
            api_addr,
            '/get_info',
            params={
                'id': '1'},
            cookies={
                'token' : token})
        assert r_get_info.status_code == 404

    @staticmethod
    def test_get_info_wrong_token(api_addr, userservice_addr, user):
        ((username, password, mail, r_v), _) = user
        r_login = make_requests(
            'POST',
            api_addr,
            '/login',
            data={
                'login': username,
                'password': password})

        token = json.loads(r_login.content)['token']

        r_get_info = make_requests(
            'GET',
            api_addr,
            '/get_info',
            params={
                'id': r_v},
            cookies={
                'token' : 'ttok'})
        assert r_get_info.status_code == 403

class TestAddFrined:

    @staticmethod
    def test_add_friend(api_addr, userservice_addr, user, another_user):
        ((username, password, mail, r_v), _) = user
        ((username_an, password_an, mail_an, r_v_an), _) = another_user
        r_login = make_requests(
            'POST',
            api_addr,
            '/login',
            data={
                'login': username,
                'password': password})

        token = json.loads(r_login.content)['token']

        r_add_friend = make_requests(
            'PUT',
            api_addr,
            '/add_friend',
            params={
                'id': r_v,
                'id_friend' : r_v_an},
            data = {"name" : "kate", "surname" : "vladimirova"},
            cookies={
                'token' : token})
        assert r_add_friend.status_code == 200


    @staticmethod
    def test_add_friend_no_user(api_addr, userservice_addr, user, another_user):
        ((username, password, mail, r_v), _) = user
        ((username_an, password_an, mail_an, r_v_an), _) = another_user
        r_login = make_requests(
            'POST',
            api_addr,
            '/login',
            data={
                'login': username,
                'password': password})

        token = json.loads(r_login.content)['token']

        r_add_friend = make_requests(
            'PUT',
            api_addr,
            '/add_friend',
            params={
                'id': '1',
                'id_friend' : r_v_an},
            data = {"name" : "kate", "surname" : "vladimirova"},
            cookies={
                'token' : token})
        assert r_add_friend.status_code == 404


    @staticmethod
    def test_add_friend_no_friend_user(api_addr, userservice_addr, user, another_user):
        ((username, password, mail, r_v), _) = user
        ((username_an, password_an, mail_an, r_v_an), _) = another_user
        r_login = make_requests(
            'POST',
            api_addr,
            '/login',
            data={
                'login': username,
                'password': password})

        token = json.loads(r_login.content)['token']

        r_add_friend = make_requests(
            'PUT',
            api_addr,
            '/add_friend',
            params={
                'id': r_v,
                'id_friend' : '1'},
            data = {"name" : "kate", "surname" : "vladimirova"},
            cookies={
                'token' : token})
        assert r_add_friend.status_code == 404

    @staticmethod
    def test_add_friend_wrong_token(api_addr, userservice_addr, user, another_user):
        ((username, password, mail, r_v), _) = user
        ((username_an, password_an, mail_an, r_v_an), _) = another_user
        r_login = make_requests(
            'POST',
            api_addr,
            '/login',
            data={
                'login': username,
                'password': password})

        token = json.loads(r_login.content)['token']

        r_add_friend = make_requests(
            'PUT',
            api_addr,
            '/add_friend',
            params={
                'id': r_v,
                'id_friend' : r_v_an},
            data = {"name" : "kate", "surname" : "vladimirova"},
            cookies={
                'token' : 'ttok'})
        assert r_add_friend.status_code == 403


    @staticmethod
    def test_add_friend_add_again(api_addr, userservice_addr, user, another_user):
        ((username, password, mail, r_v), _) = user
        ((username_an, password_an, mail_an, r_v_an), _) = another_user
        r_login = make_requests(
            'POST',
            api_addr,
            '/login',
            data={
                'login': username,
                'password': password})

        token = json.loads(r_login.content)['token']

        r_add_friend = make_requests(
            'PUT',
            api_addr,
            '/add_friend',
            params={
                'id': r_v,
                'id_friend' : r_v_an},
            data = {"name" : "kate", "surname" : "vladimirova"},
            cookies={
                'token' : token})

        r_add_friend = make_requests(
            'PUT',
            api_addr,
            '/add_friend',
            params={
                'id': r_v,
                'id_friend' : r_v_an},
            data = {"name" : "kate", "surname" : "vladimirova"},
            cookies={
                'token' : token})
        assert r_add_friend.status_code == 400

