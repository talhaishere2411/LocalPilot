from formatter import format_greeting


def test_format_greeting():
    assert format_greeting("Alice") == "HELLO, ALICE!"
    assert format_greeting("Bob") == "HELLO, BOB!"


def test_no_typo_in_source():
    # Check that the source code doesn't contain the typo
    import formatter
    import inspect
    source = inspect.getsource(formatter.format_greeting)
    assert 'mesage' not in source
    assert 'message' in source
