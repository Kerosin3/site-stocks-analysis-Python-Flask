import pytest

@pytest.fixture(scope='module')
def myfixture():
    ticker = 'NVDA'
    yield ticker
