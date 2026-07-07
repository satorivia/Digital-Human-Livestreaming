from app.main import app, healthz

def test_healthz():
    if app is None:
        assert healthz()['data']['status']=='ok'
    else:
        from fastapi.testclient import TestClient
        r=TestClient(app).get('/api/v1/healthz')
        assert r.status_code==200 and r.json()['data']['status']=='ok'
