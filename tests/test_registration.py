import pytest
import sqlite3
import os
from registration.registration import create_db, add_user, authenticate_user, display_users

@pytest.fixture(scope="module")
def setup_database():
    """Фикстура для настройки базы данных перед тестами и её очистки после."""
    create_db()
    yield
    try:
        os.remove('users.db')
    except PermissionError:
        pass

@pytest.fixture
def connection():
    """Фикстура для получения соединения с базой данных и его закрытия после теста."""
    conn = sqlite3.connect('users.db')
    yield conn
    conn.close()


def test_create_db(setup_database, connection):
    """Тест создания базы данных и таблицы пользователей."""
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    table_exists = cursor.fetchone()
    assert table_exists, "Таблица 'users' должна существовать в базе данных."

def test_add_new_user(setup_database, connection):
    """Тест добавления нового пользователя."""
    add_user('testuser', 'testuser@example.com', 'password123')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username='testuser';")
    user = cursor.fetchone()
    assert user, "Пользователь должен быть добавлен в базу данных."

# Возможные варианты тестов:
"""
Тест добавления пользователя с существующим логином.
Тест успешной аутентификации пользователя.
Тест аутентификации несуществующего пользователя.
Тест аутентификации пользователя с неправильным паролем.
Тест отображения списка пользователей.
"""

def test_add_existing_user(setup_database, connection):
    """Тест добавления пользователя с существующим логином."""
    add_user('duplicateuser', 'dup@example.com', 'pass123')
    result = add_user('duplicateuser', 'another@example.com', 'pass456')
    assert result is False or result is None, "Добавление пользователя с существующим логином должно быть отклонено."

def test_successful_authentication(setup_database):
    """Тест успешной аутентификации пользователя."""
    add_user('authuser', 'auth@example.com', 'authpass')
    result = authenticate_user('authuser', 'authpass')
    assert result is True, "Аутентификация с правильными данными должна пройти успешно."

def test_authentication_nonexistent_user(setup_database):
    """Тест аутентификации несуществующего пользователя."""
    result = authenticate_user('ghostuser', 'nopass')
    assert result is False, "Аутентификация несуществующего пользователя должна возвращать False."

def test_authentication_wrong_password(setup_database):
    """Тест аутентификации пользователя с неправильным паролем."""
    add_user('realuser', 'real@example.com', 'realpass')
    result = authenticate_user('realuser', 'wrongpass')
    assert result is False, "Аутентификация с неправильным паролем должна возвращать False."

def test_display_users_output(capsys, setup_database):
    """Тест отображения списка пользователей."""
    add_user('shownuser', 'shown@example.com', 'showpass')
    display_users()
    captured = capsys.readouterr()
    assert 'shownuser' in captured.out, "Список пользователей должен содержать добавленного пользователя."
