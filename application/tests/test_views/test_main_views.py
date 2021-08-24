import pytest
from app import app


@pytest.fixture
def client():
    with app.test_client() as test_client:
        with app.app_context():
            yield test_client


def test_indexes_requests_view(client):
    rv = client.get('/')
    print('data is ============', rv.data)
    assert rv.status_code < 400
