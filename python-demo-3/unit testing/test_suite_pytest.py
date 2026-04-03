# Fixtures (setup/teardown equivalent)
import pytest

@pytest.fixture
def sample_list():
    return [1, 2, 3]

def test_length(sample_list):
    assert len(sample_list) == 3


def test_sum():
    assert sum([1, 2, 3]) == 6

def test_max():
    assert max([1, 2, 3]) > 2

def test_raises():
    import pytest
    with pytest.raises(ZeroDivisionError):
        1 / 0