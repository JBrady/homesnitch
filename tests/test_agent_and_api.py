import sys
import pytest
from backend.api import app, last_report
import requests
import agent

class DummyResponse:
    def __init__(self):
        self._json = {'ok': True}
    def raise_for_status(self):
        pass
    def json(self):
        return self._json

@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client


def test_agent_test_endpoint(client):
    # ensure dummy test works and updates last_report
    last_report.clear()
    resp = client.get('/agent/test')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['status'] == 'ok'
    assert 'devices' in data
    assert data['devices'][0]['ip'] == '192.168.0.99'
    # verify GET /report returns the same
    resp2 = client.get('/report')
    assert resp2.get_json()[0]['ip'] == '192.168.0.99'


def test_agent_cli_test_mode(monkeypatch, capsys):
    # monkeypatch requests.post to capture payload
    captured = {}
    def fake_post(url, json=None, **kwargs):
        captured['url'] = url
        captured['json'] = json
        return DummyResponse()
    monkeypatch.setattr(requests, 'post', fake_post)
    # run agent with --test flag
    sys.argv = ['agent.py', '--server', 'http://example.com', '--test']
    agent.main()
    out = capsys.readouterr().out
    assert 'Report successful:' in out
    assert captured['url'] == 'http://example.com'
    assert captured['json']['devices'][0]['ip'] == '192.168.0.99'
