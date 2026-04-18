from helpers import percentage


def test_percentage_half():
    assert percentage(50, 100) == 50


def test_percentage_quarter():
    assert percentage(1, 4) == 25


def test_percentage_full():
    assert percentage(100, 100) == 100


def test_percentage_zero():
    assert percentage(0, 100) == 0
