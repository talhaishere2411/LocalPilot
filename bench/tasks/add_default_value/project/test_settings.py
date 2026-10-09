import inspect
from settings import create_config


def test_create_config_with_all_params():
    config = create_config("myapp", "localhost", 8080)
    assert config == {"name": "myapp", "host": "localhost", "port": 8080}


def test_create_config_with_defaults():
    config = create_config("myapp")
    assert config == {"name": "myapp", "host": "localhost", "port": 8000}


def test_port_has_default():
    sig = inspect.signature(create_config)
    assert sig.parameters['port'].default == 8000
