# Тесты

## test_user_service

Тесты проверяют работу сервиса клиентов

TestRegister:

* test_register - проверяет регистрацию
* test_register_same_name - проверяет регистрацию с тем же логином
* test_register_same_mail - проверяет регистрацию с той же почтой

TestLogin:

* test_login - проверяет аутентификацию
* test_login_no_user - проверяет аутентификацию с несуществующим логином
* test_login_wrong_password - проверяет аутентификацию с несуществующим паролем

TestUpdate:

* test_update - проверяет успешность изменения данных
* test_update_wrong_token - проверяет изменение данных с неправильным токеном
* test_update_login - проверяет попытку изменения логина
* test_update_password - проверяет попытку изменения пароля
* test_update_do_not_find_user - проверяет изменение данных с несуществующим пользователем

TestGetInfo:

* test_get_info - проверяет получение данных о пользователе
* test_get_info_do_not_find_user - провеяет получение данных у несуществующего пользователя
* test_get_info_wrong_token - проверяет получение данных с неправильным токеном

TestAddFrined:

* test_add_friend - добавление друга
* test_add_friend_no_user - добавление друга у несуществующего пользователя
* test_add_friend_no_friend_user - добавление в друзья несуществующего пользователя
* test_add_friend_wrong_token - добавление пользователя с неправильным токеном
* test_add_friend_add_again - добавление друга, который уже добавлен

## запуск тестов

docker-compose build - настроить все сервисы
docker-compose up - запусить работу сервисов и тестов заодно


