import pytest

@pytest.fixture(scope='module')
def username_fixture():
    username = 'Alex'
    yield username



