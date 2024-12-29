def test_get_version(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {'version': '0.1.0'}
