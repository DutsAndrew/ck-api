import pytest
from fastapi.testclient import TestClient

# @pytest.mark.skip(reason='Not implemented')
def test_delete_account_without_token_rejects_request(test_client_with_db: TestClient):
    response = test_client_with_db.post('/account/delete')
    assert response.status_code == 422
    assert response.json()['detail'] == [
        {
            'type': 'missing',
            'loc': ['header', 'authorization'],
            'msg': 'Field required',
            'input': None,
            'url': 'https://errors.pydantic.dev/2.1/v/missing'
        }
    ]
