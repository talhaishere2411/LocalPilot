import config


def test_get_max_retries():
    assert config.get_max_retries() == 3


def test_get_timeout():
    assert config.get_timeout() == 30


def test_max_retries_constant_exists():
    # Check that MAX_RETRIES constant exists
    assert hasattr(config, 'MAX_RETRIES')
    assert config.MAX_RETRIES == 3
    # Check that function uses the constant
    assert config.get_max_retries() == config.MAX_RETRIES
