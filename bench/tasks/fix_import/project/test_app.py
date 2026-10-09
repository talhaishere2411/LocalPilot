from app import greet_user


def test_greet_user():
    assert greet_user("Alice") == "Welcome, Alice!"
    assert greet_user("Bob") == "Welcome, Bob!"
