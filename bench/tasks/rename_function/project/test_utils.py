from utils import calculate_total, process_order


def test_calculate_total():
    assert calculate_total([1, 2, 3]) == 6
    assert calculate_total([10, 20]) == 30


def test_process_order():
    assert process_order([5, 10, 15]) == 30
    assert process_order([100]) == 100
