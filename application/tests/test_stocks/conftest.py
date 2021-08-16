import pytest

@pytest.fixture(scope='module')
def myfixture():
    ticker = 'NVDA'
    yield ticker


@pytest.fixture(scope='module')
def id_fixture():
    id_fix = 0
    yield id_fix
